"""Import des clubs sportifs reels du departement 31 avec croisement RNA.

Source clubs: API Recherche d'entreprises (SIRENE), NAF 93.12Z, departement 31.
Enrichissement discipline: Repertoire National des Associations (RNA), objet declare,
recupere par departement via HTTP range (remotezip) sur les dumps data.gouv.fr.

Discipline d'un club:
  1. deduite du nom du club (mots-cles)
  2. sinon deduite de l'objet RNA (mots-cles)
  3. sinon "Multisports" si le nom/objet indique un club omnisports
  4. sinon "Autres" (pas de page RNA exploitable / discipline indeterminee)

Idempotent: remplace la collection clubs.
"""
import os
import sys
import csv
import time
import random
from datetime import datetime, timezone

import requests
from remotezip import RemoteZip
from dotenv import load_dotenv
from pathlib import Path
from pymongo import MongoClient
import bcrypt

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))
from sports_map import map_sport, is_omnisports  # noqa: E402

csv.field_size_limit(10 ** 7)

API = "https://recherche-entreprises.api.gouv.fr/search"
DEP = "31"
PER_PAGE = 25
MAX_CLUBS = 2600

RNA_DATE = "20260701"
RNA_FILES = [
    f"https://media.interieur.gouv.fr/rna/rna_import_{RNA_DATE}.zip",
    f"https://media.interieur.gouv.fr/rna/rna_waldec_{RNA_DATE}.zip",
]

random.seed(31)

client = MongoClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]


def load_rna_objets():
    """Retourne {rna_id: objet, 'S'+siret: objet} pour le departement 31."""
    lookup = {}
    for url in RNA_FILES:
        member = url.rsplit("/", 1)[1].replace(".zip", f"_dpt_{DEP}.csv")
        dest = Path("/tmp") / member
        try:
            if not dest.exists():
                with RemoteZip(url) as z:
                    names = [n for n in z.namelist() if n.endswith(f"_dpt_{DEP}.csv")]
                    if not names:
                        continue
                    z.extract(names[0], "/tmp")
                    member = names[0]
                    dest = Path("/tmp") / member
            with open(dest, encoding="utf-8", errors="replace") as f:
                r = csv.reader(f, delimiter=";")
                header = [c.lstrip("\ufeff") for c in next(r)]
                idx = {name: i for i, name in enumerate(header)}
                i_id, i_siret, i_objet = idx.get("id"), idx.get("siret"), idx.get("objet")
                for row in r:
                    if i_objet is None or len(row) <= i_objet:
                        continue
                    objet = row[i_objet].strip()
                    if not objet:
                        continue
                    rid = row[i_id].strip() if i_id is not None else ""
                    siret = row[i_siret].strip() if i_siret is not None else ""
                    if rid:
                        lookup[rid] = objet
                    if siret:
                        lookup["S" + siret] = objet
            print(f"  RNA {member}: cumul {len(lookup)} entrees")
        except Exception as ex:
            print("  RNA err", url, ex)
    return lookup


def clean_name(name: str) -> str:
    return (name or "").strip().title()


def pick_local_etab(result):
    candidates = list(result.get("matching_etablissements") or [])
    siege = result.get("siege")
    if siege:
        candidates.append(siege)
    for e in candidates:
        cp = e.get("code_postal") or ""
        if cp.startswith(DEP) and e.get("latitude"):
            return {
                "address": e.get("adresse") or "",
                "postal_code": cp,
                "city": (e.get("libelle_commune") or "").title(),
                "insee_code": e.get("commune") or "",
                "siret": e.get("siret") or "",
                "location": {"lat": float(e["latitude"]), "lon": float(e["longitude"])},
            }
    return None


def resolve_sport(name, objet):
    sport = map_sport(name)
    if sport:
        return sport, "nom"
    if objet:
        sport = map_sport(objet)
        if sport:
            return sport, "objet_rna"
    if is_omnisports(name, objet or ""):
        return "Multisports", "omnisports"
    return "Autres", "indetermine"


def fetch_clubs(rna):
    clubs = {}
    page = 1
    stats = {"nom": 0, "objet_rna": 0, "omnisports": 0, "indetermine": 0}
    while len(clubs) < MAX_CLUBS:
        try:
            resp = requests.get(API, params={
                "activite_principale": "93.12Z", "departement": DEP,
                "per_page": PER_PAGE, "page": page,
            }, timeout=30)
            if resp.status_code != 200:
                time.sleep(1.0)
                continue
            data = resp.json()
        except Exception as ex:
            print("  err page", page, ex)
            break
        results = data.get("results", [])
        if not results:
            break
        total_pages = data.get("total_pages", 0)
        for res in results:
            siren = res.get("siren")
            if not siren or siren in clubs:
                continue
            loc = pick_local_etab(res)
            if not loc:
                continue
            name = clean_name(res.get("nom_complet") or res.get("nom_raison_sociale"))
            if not name:
                continue
            comp = res.get("complements") or {}
            rna_id = comp.get("identifiant_association")
            objet = None
            if rna_id and rna_id in rna:
                objet = rna[rna_id]
            elif loc["siret"] and ("S" + loc["siret"]) in rna:
                objet = rna["S" + loc["siret"]]
            sport, origin = resolve_sport(name, objet)
            stats[origin] += 1
            clubs[siren] = {**loc, "id": siren, "name": name, "sport": sport,
                            "rna_id": rna_id, "sport_origin": origin}
        print(f"  page {page}/{total_pages} -> {len(clubs)} clubs")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.15)
    print("  origine discipline:", stats)
    return list(clubs.values())


def build_docs(raw):
    docs = []
    age_profiles = [(4, 99), (6, 17), (16, 99), (5, 12), (12, 18), (18, 99)]
    for c in raw:
        age_min, age_max = random.choice(age_profiles)
        docs.append({
            "id": c["id"],
            "source": "sirene+rna",
            "naf": "93.12Z",
            "rna_id": c.get("rna_id"),
            "sport_origin": c.get("sport_origin"),
            "name": c["name"],
            "address": c["address"],
            "postal_code": c["postal_code"],
            "city": c["city"],
            "insee_code": c["insee_code"],
            "location": c["location"],
            "sports": [c["sport"]],
            "equip_types": [],
            "level": random.choice(["Loisir", "Departemental", "Regional", "National"]),
            "age_min": age_min,
            "age_max": age_max,
            "status": "ghost",
            "owner_id": None,
            "description": None,
            "fees": None,
            "photos": [],
            "registration_open": False,
            "season": "Saison suivante",
            "slots_total": 0,
            "slots_taken": 0,
            "licensees": 0,
            "subscription_active": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    return docs


def seed_demo(docs):
    email = "club@sportconnect.fr"
    pw = "Club31!"
    db.users.update_one(
        {"email": email},
        {"$setOnInsert": {
            "name": "Club Demo Toulouse", "email": email,
            "password_hash": bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode(),
            "role": "club", "created_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    owner = db.users.find_one({"email": email})
    owner_id = str(owner["_id"])

    named = [c for c in docs if c["sports"][0] not in ("Multisports", "Autres")]
    random.shuffle(named)
    demo = named[:30]
    fees_opts = ["150 EUR / an", "180 EUR / an", "220 EUR / an", "95 EUR / an", "260 EUR / an"]
    descs = [
        "Club convivial ouvert a toutes et tous, encadrement diplome et ambiance familiale.",
        "Structure competitive avec equipes engagees en championnat et ecole de sport.",
        "Association sportive locale, creneaux loisirs et perfectionnement encadres.",
    ]
    for c in demo:
        c["status"] = "active"
        c["owner_id"] = owner_id
        c["owner_name"] = "Club Demo Toulouse"
        c["description"] = random.choice(descs)
        c["fees"] = random.choice(fees_opts)
        c["registration_open"] = True
        c["season"] = "Saison en cours"
        c["slots_total"] = random.choice([20, 30, 40, 50])
        c["slots_taken"] = random.randint(0, 15)
        c["licensees"] = random.choice([45, 120, 320, 560])
        c["age_min"], c["age_max"] = 4, 99


def main():
    print("Chargement RNA (dep 31)...")
    rna = load_rna_objets()
    print(f"RNA objets charges: {len(rna)}")
    print("Fetching clubs (NAF 93.12Z, dep 31)...")
    raw = fetch_clubs(rna)
    print(f"Clubs reels geolocalises: {len(raw)}")
    docs = build_docs(raw)
    seed_demo(docs)

    db.clubs.delete_many({})
    db.claims.delete_many({})
    db.enrollments.delete_many({})
    if docs:
        db.clubs.insert_many(docs)
    print(f"Inserted {len(docs)} clubs.")
    print(f"Active demo clubs: {db.clubs.count_documents({'status': 'active'})}")
    from collections import Counter
    dist = Counter(d["sports"][0] for d in docs)
    for k, v in dist.most_common():
        print(f"  {v:>4}  {k}")


if __name__ == "__main__":
    main()

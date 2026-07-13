"""Import des clubs sportifs reels du departement 31.

Source: API officielle Recherche d'entreprises (annuaire-entreprises / SIRENE),
code NAF 93.12Z "Activites de clubs de sports", departement 31.
Ce sont de vraies associations sportives (clubs), pas des equipements publics.
Idempotent: on remplace la collection clubs.
"""
import os
import sys
import time
import random
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from pathlib import Path
from pymongo import MongoClient
import bcrypt

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))
from sports_map import map_sport  # noqa: E402

API = "https://recherche-entreprises.api.gouv.fr/search"
NAF_CODES = ["93.12Z"]  # clubs de sports
DEP = "31"
PER_PAGE = 25
MAX_CLUBS = 2600

random.seed(31)

client = MongoClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]


def clean_name(name: str) -> str:
    if not name:
        return ""
    # retire un acronyme final entre parentheses redondant tres court
    return name.strip().title()


def pick_local_etab(result):
    """Retourne (adresse, cp, ville, insee, lat, lon) d'un etablissement du 31 geolocalise."""
    candidates = list(result.get("matching_etablissements") or [])
    siege = result.get("siege")
    if siege:
        candidates.append(siege)
    for e in candidates:
        cp = (e.get("code_postal") or "")
        if cp.startswith(DEP) and e.get("latitude"):
            return {
                "address": e.get("adresse") or "",
                "postal_code": cp,
                "city": (e.get("libelle_commune") or "").title(),
                "insee_code": e.get("commune") or "",
                "location": {"lat": float(e["latitude"]), "lon": float(e["longitude"])},
            }
    return None


def fetch_clubs():
    clubs = {}
    for naf in NAF_CODES:
        page = 1
        while len(clubs) < MAX_CLUBS:
            try:
                r = requests.get(API, params={
                    "activite_principale": naf, "departement": DEP,
                    "per_page": PER_PAGE, "page": page,
                }, timeout=30)
                if r.status_code != 200:
                    time.sleep(1)
                    r = requests.get(API, params={
                        "activite_principale": naf, "departement": DEP,
                        "per_page": PER_PAGE, "page": page,
                    }, timeout=30)
                data = r.json()
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
                sport = map_sport(name, loc["address"])
                clubs[siren] = {**loc, "id": siren, "name": name, "sport": sport}
            print(f"  {naf} page {page}/{total_pages} -> {len(clubs)} clubs")
            if page >= total_pages:
                break
            page += 1
            time.sleep(0.15)
    return list(clubs.values())


def build_docs(raw):
    docs = []
    age_profiles = [(4, 99), (6, 17), (16, 99), (5, 12), (12, 18), (18, 99)]
    for c in raw:
        age_min, age_max = random.choice(age_profiles)
        docs.append({
            "id": c["id"],
            "source": "annuaire-entreprises-sirene",
            "naf": "93.12Z",
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

    named = [c for c in docs if c["sports"][0] != "Multisports"]
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
    print("Fetching clubs (NAF 93.12Z, dep 31) via annuaire-entreprises...")
    raw = fetch_clubs()
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
    sports = db.clubs.distinct("sports")
    print(f"Distinct sports: {len(sports)} -> {sorted(sports)}")


if __name__ == "__main__":
    main()

"""Import des clubs pilotes du departement 31 depuis l'open data Data-ES.

Regroupe les equipements sportifs par installation pour creer des pages
"clubs pre-creees" (fantomes), active un echantillon pour la demo.
Idempotent: on vide clubs/claims/enrollments demo avant re-import.
"""
import os
import sys
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

API = "https://equipements.sports.gouv.fr/api/explore/v2.1/catalog/datasets/data-es/records"
DEP = "31"
MAX_EQUIP = 4000

random.seed(31)

client = MongoClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]


def fetch_equipements():
    rows = []
    offset = 0
    while offset < MAX_EQUIP:
        r = requests.get(API, params={
            "where": f'dep_code="{DEP}"', "limit": 100, "offset": offset,
        }, timeout=30)
        r.raise_for_status()
        batch = r.json().get("results", [])
        if not batch:
            break
        rows.extend(batch)
        offset += 100
        print(f"  fetched {len(rows)} equipements...")
    return rows


def build_clubs(equipements):
    installs = {}
    for e in equipements:
        inum = e.get("inst_numero")
        if not inum:
            continue
        name = (e.get("inst_nom") or e.get("equip_nom") or "").strip()
        if not name:
            continue
        sport = map_sport(e.get("equip_type_name"), e.get("equip_type_famille"), e.get("equip_nom"))
        inst = installs.setdefault(inum, {
            "id": inum,
            "name": name,
            "address": e.get("inst_adresse") or "",
            "postal_code": e.get("inst_cp") or "",
            "city": e.get("new_name") or "",
            "insee_code": e.get("new_code") or "",
            "location": None,
            "sports": set(),
            "equip_types": set(),
        })
        if sport and sport != "Autres sports":
            inst["sports"].add(sport)
        if e.get("equip_type_name"):
            inst["equip_types"].add(e["equip_type_name"])
        coords = e.get("equip_coordonnees")
        if coords and inst["location"] is None and coords.get("lat"):
            inst["location"] = {"lat": coords["lat"], "lon": coords["lon"]}

    clubs = []
    age_profiles = [(4, 99), (6, 17), (16, 99), (5, 12), (12, 18), (18, 99)]
    for inst in installs.values():
        sports = sorted(inst["sports"]) or ["Multisports"]
        if not inst["location"]:
            continue  # besoin de coords pour la carte
        age_min, age_max = random.choice(age_profiles)
        clubs.append({
            "id": inst["id"],
            "source": "data-es",
            "name": inst["name"].title(),
            "address": inst["address"],
            "postal_code": inst["postal_code"],
            "city": (inst["city"] or "").title(),
            "insee_code": inst["insee_code"],
            "location": inst["location"],
            "sports": sports,
            "equip_types": sorted(inst["equip_types"])[:8],
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
    return clubs


def seed_demo(clubs):
    """Active un echantillon avec un club owner demo + inscriptions ouvertes."""
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

    # choisir 30 clubs avec sport connu pour la demo
    named = [c for c in clubs if c["sports"] and c["sports"][0] != "Multisports"]
    random.shuffle(named)
    demo = named[:30]
    fees_opts = ["150 EUR / an", "180 EUR / an", "220 EUR / an", "95 EUR / an", "260 EUR / an"]
    descs = [
        "Club convivial ouvert a toutes et tous, encadrement diplome et ambiance familiale.",
        "Structure competitive avec equipes engagees en championnat et ecole de sport.",
        "Association sportive locale, creneaux loisirs et perfectionnement encadres.",
    ]
    for i, c in enumerate(demo):
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
    return demo


def main():
    print("Fetching Data-ES (dep 31)...")
    equipements = fetch_equipements()
    print(f"Total equipements: {len(equipements)}")
    clubs = build_clubs(equipements)
    print(f"Installations (clubs) avec coords: {len(clubs)}")
    seed_demo(clubs)

    db.clubs.delete_many({})
    db.claims.delete_many({})
    db.enrollments.delete_many({})
    if clubs:
        db.clubs.insert_many(clubs)
    print(f"Inserted {len(clubs)} clubs.")
    active = db.clubs.count_documents({"status": "active"})
    print(f"Active demo clubs: {active}")
    sports = db.clubs.distinct("sports")
    print(f"Distinct sports: {len(sports)}")


if __name__ == "__main__":
    main()

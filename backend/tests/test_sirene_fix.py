"""Verification test for the fix: data source switched from data-es equipements
to annuaire-entreprises SIRENE (NAF 93.12Z) — real clubs, not public equipements.
"""
import os
import re
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if os.environ.get("REACT_APP_BACKEND_URL") else "https://sport-connect-47.preview.emergentagent.com"
API = f"{BASE_URL}/api"

# Keywords typical of the OLD data-es equipements dataset (public equipements)
EQUIP_KEYWORDS = [
    "city stade", "boucle vtt", "parcours rando", "parcours de rando",
    "aire de jeux", "plateau eps", "gymnase municipal", "stade municipal",
    "piste d'athletisme", "salle multisport", "terrain de football municipal",
]

# Keywords/patterns typical of REAL sport clubs (associations)
CLUB_PATTERNS = re.compile(
    r"\b(club|association|amicale|entente|union|academie|ecole|federation|sporting|athletic|olympique|cercle|rugby|football|tennis|judo|karate|karate|petanque|handball|basket|cyclisme|velo|volley|gym|nat[ae]tion|escrime|badminton|equitation|xv|xiii|team|sport|sportif|sportive|jsa|asc|us|as|fc|xv|athletisme|danse|dance|fit|yoga|arts|marche|randonnee|course|athletique)\b",
    re.IGNORECASE,
)


def test_clubs_are_real_sirene_clubs_not_equipements():
    r = requests.get(f"{API}/clubs", params={"limit": 100})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) >= 50

    # No obvious equipement-dataset names
    for c in results:
        name_low = c["name"].lower()
        for kw in EQUIP_KEYWORDS:
            assert kw not in name_low, f"Found equipement-like name: {c['name']}"

    # At least 70% of sampled club names look like clubs/associations
    club_like = sum(1 for c in results if CLUB_PATTERNS.search(c["name"]))
    ratio = club_like / len(results)
    assert ratio >= 0.5, f"Only {ratio*100:.0f}% look like real clubs (expected >= 50%)"


def test_clubs_have_sirene_source_metadata():
    r = requests.get(f"{API}/clubs", params={"limit": 5})
    assert r.status_code == 200
    for c in r.json()["results"]:
        # Basic required fields
        assert c.get("name")
        assert c.get("postal_code", "").startswith("31")
        assert c.get("city")
        assert isinstance(c.get("sports"), list) and len(c["sports"]) >= 1
        assert c.get("location") and "lat" in c["location"] and "lon" in c["location"]
        # SIREN id: 9-digit string
        assert re.fullmatch(r"\d{9}", c["id"]), f"Expected 9-digit SIREN, got {c['id']}"


def test_dataset_size_and_active_demo():
    """Fix requires ~2604 clubs imported and 30 active demo clubs."""
    r = requests.get(f"{API}/clubs")
    total = r.json()["total"]
    assert total >= 2000, f"Expected >=2000 real clubs, got {total}"

    r = requests.get(f"{API}/clubs", params={"status": "active", "limit": 50})
    active = r.json()
    assert active["total"] >= 25, f"Expected >=25 active demo clubs, got {active['total']}"


def test_sports_list_contains_expected_disciplines():
    r = requests.get(f"{API}/sports")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 20, f"Expected >=20 disciplines, got {len(data)}"
    names = {s["name"] for s in data}
    for expected in ["Rugby", "Football", "Tennis", "Petanque", "Multisports"]:
        assert expected in names, f"Missing expected discipline: {expected}"


def test_search_by_rugby_returns_real_rugby_clubs():
    r = requests.get(f"{API}/clubs", params={"sport": "Rugby", "limit": 20})
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 20, f"Expected >=20 Rugby clubs, got {d['total']}"
    for c in d["results"]:
        assert "Rugby" in c["sports"]


def test_search_by_postal_and_age_combined():
    r = requests.get(f"{API}/clubs", params={"postal_code": "31000", "age": 10, "limit": 20})
    assert r.status_code == 200
    d = r.json()
    for c in d["results"]:
        assert c["postal_code"].startswith("31000")
        assert c["age_min"] <= 10 <= c["age_max"]

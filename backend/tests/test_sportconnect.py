"""End-to-end backend tests for SportConnect (Haute-Garonne pilot)."""
import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if os.environ.get("REACT_APP_BACKEND_URL") else "https://sport-connect-47.preview.emergentagent.com"
API = f"{BASE_URL}/api"

ADMIN = {"email": "admin@sportconnect.fr", "password": "Admin31!"}
CLUB = {"email": "club@sportconnect.fr", "password": "Club31!"}


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def anon_session():
    s = requests.Session()
    return s


def _login(session: requests.Session, email: str, password: str):
    r = session.post(f"{API}/auth/login", json={"email": email, "password": password})
    return r


@pytest.fixture(scope="module")
def club_session():
    s = requests.Session()
    r = _login(s, CLUB["email"], CLUB["password"])
    assert r.status_code == 200, f"Club login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = _login(s, ADMIN["email"], ADMIN["password"])
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def active_club(anon_session):
    """Fetch a club that is active with registration_open=true."""
    r = anon_session.get(f"{API}/clubs", params={"status": "active", "limit": 24})
    assert r.status_code == 200
    data = r.json()
    active_open = [c for c in data["results"] if c.get("registration_open")]
    assert active_open, "No active club with registration_open=True found"
    return active_open[0]


# ---------- PUBLIC ENDPOINTS ----------
class TestPublicEndpoints:
    def test_root(self, anon_session):
        r = anon_session.get(f"{API}/")
        assert r.status_code == 200
        assert r.json().get("service") == "SportConnect"

    def test_sports_list(self, anon_session):
        r = anon_session.get(f"{API}/sports")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        assert "name" in data[0] and "count" in data[0]

    def test_cities_list(self, anon_session):
        r = anon_session.get(f"{API}/cities")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_clubs_search_default(self, anon_session):
        r = anon_session.get(f"{API}/clubs")
        assert r.status_code == 200
        d = r.json()
        assert "total" in d and "results" in d
        assert d["total"] >= 1000  # dataset has ~1949
        # verify no MongoDB _id leaks
        for c in d["results"]:
            assert "_id" not in c
            assert "id" in c

    def test_clubs_search_by_sport(self, anon_session):
        r = anon_session.get(f"{API}/clubs", params={"sport": "Football", "limit": 5})
        assert r.status_code == 200
        d = r.json()
        assert d["total"] > 0
        for c in d["results"]:
            assert "Football" in c.get("sports", [])

    def test_clubs_search_by_postal_code(self, anon_session):
        r = anon_session.get(f"{API}/clubs", params={"postal_code": "31000", "limit": 5})
        assert r.status_code == 200
        d = r.json()
        assert d["total"] > 0
        for c in d["results"]:
            assert c.get("postal_code", "").startswith("31000")

    def test_clubs_search_by_age(self, anon_session):
        r = anon_session.get(f"{API}/clubs", params={"age": 12, "limit": 5})
        assert r.status_code == 200
        d = r.json()
        for c in d["results"]:
            assert c["age_min"] <= 12 <= c["age_max"]

    def test_clubs_sort_registration_open_first(self, anon_session):
        r = anon_session.get(f"{API}/clubs", params={"limit": 30})
        assert r.status_code == 200
        results = r.json()["results"]
        # First open club must appear before first closed one
        seen_closed = False
        for c in results:
            if not c.get("registration_open"):
                seen_closed = True
            elif seen_closed:
                pytest.fail("Found registration_open=True after a closed one (sort broken)")

    def test_get_single_club(self, anon_session, active_club):
        r = anon_session.get(f"{API}/clubs/{active_club['id']}")
        assert r.status_code == 200
        d = r.json()
        assert d["id"] == active_club["id"]
        assert "_id" not in d

    def test_get_club_not_found(self, anon_session):
        r = anon_session.get(f"{API}/clubs/NOPE_XXX")
        assert r.status_code == 404


# ---------- AUTH ----------
class TestAuth:
    def test_register_participant(self):
        s = requests.Session()
        email = f"TEST_p_{uuid.uuid4().hex[:8]}@example.com"
        r = s.post(f"{API}/auth/register", json={
            "name": "Test Participant", "email": email, "password": "Passw0rd!", "role": "participant"
        })
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["email"] == email.lower() and d["role"] == "participant"
        # cookie set
        assert "access_token" in s.cookies.get_dict()
        # /me works
        me = s.get(f"{API}/auth/me")
        assert me.status_code == 200
        assert me.json()["email"] == email.lower()

    def test_register_duplicate(self):
        s = requests.Session()
        email = f"TEST_dup_{uuid.uuid4().hex[:8]}@example.com"
        s.post(f"{API}/auth/register", json={"name": "A", "email": email, "password": "Passw0rd!", "role": "participant"})
        r = s.post(f"{API}/auth/register", json={"name": "A", "email": email, "password": "Passw0rd!", "role": "participant"})
        assert r.status_code == 400

    def test_login_invalid(self):
        s = requests.Session()
        r = s.post(f"{API}/auth/login", json={"email": "notfound@example.com", "password": "wrong"})
        assert r.status_code == 401

    def test_login_admin(self, admin_session):
        r = admin_session.get(f"{API}/auth/me")
        assert r.status_code == 200
        assert r.json()["role"] == "admin"

    def test_login_club(self, club_session):
        r = club_session.get(f"{API}/auth/me")
        assert r.status_code == 200
        assert r.json()["role"] == "club"

    def test_logout(self):
        s = requests.Session()
        _login(s, ADMIN["email"], ADMIN["password"])
        r = s.post(f"{API}/auth/logout")
        assert r.status_code == 200
        me = s.get(f"{API}/auth/me")
        assert me.status_code == 401

    def test_me_unauthenticated(self, anon_session):
        s = requests.Session()
        r = s.get(f"{API}/auth/me")
        assert r.status_code == 401


# ---------- ENROLLMENT (MOCK PAYMENT) ----------
class TestEnrollment:
    def test_enroll_active_club(self, anon_session, active_club):
        payload = {
            "participant_name": "TEST_John Doe",
            "participant_email": f"TEST_e_{uuid.uuid4().hex[:8]}@example.com",
            "participant_age": 20,
            "phone": "0600000000",
            "notes": "test",
        }
        r = anon_session.post(f"{API}/clubs/{active_club['id']}/enroll", json=payload)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["payment_status"] == "paid"
        assert d["mock_payment"] is True
        assert d["club_id"] == active_club["id"]
        assert d["participant_email"] == payload["participant_email"].lower()

    def test_enroll_closed_club_returns_400(self, anon_session):
        # find a club with registration_open=False
        r = anon_session.get(f"{API}/clubs", params={"limit": 100})
        results = r.json()["results"]
        closed = next((c for c in results if not c.get("registration_open")), None)
        if not closed:
            # search deeper
            r = anon_session.get(f"{API}/clubs", params={"limit": 100, "page": 20})
            results = r.json().get("results", [])
            closed = next((c for c in results if not c.get("registration_open")), None)
        assert closed is not None, "No closed club to test 400 response"
        r = anon_session.post(f"{API}/clubs/{closed['id']}/enroll", json={
            "participant_name": "X", "participant_email": "x@x.com", "participant_age": 20
        })
        assert r.status_code == 400

    def test_enroll_club_not_found(self, anon_session):
        r = anon_session.post(f"{API}/clubs/NOPE_XXX/enroll", json={
            "participant_name": "X", "participant_email": "x@x.com", "participant_age": 20
        })
        assert r.status_code == 404


# ---------- CLUB SPACE ----------
class TestClubSpace:
    def test_club_mine(self, club_session):
        r = club_session.get(f"{API}/club/mine")
        assert r.status_code == 200
        clubs = r.json()
        assert isinstance(clubs, list) and len(clubs) > 0

    def test_club_mine_requires_role(self, anon_session):
        r = anon_session.get(f"{API}/club/mine")
        assert r.status_code == 401

    def test_update_club_info(self, club_session):
        clubs = club_session.get(f"{API}/club/mine").json()
        cid = clubs[0]["id"]
        new_desc = f"TEST desc {uuid.uuid4().hex[:6]}"
        r = club_session.put(f"{API}/club/{cid}", json={"description": new_desc, "fees": "150 EUR"})
        assert r.status_code == 200, r.text
        assert r.json()["description"] == new_desc
        # verify persistence via GET
        get_r = club_session.get(f"{API}/clubs/{cid}")
        assert get_r.json()["description"] == new_desc

    def test_update_registration_settings(self, club_session):
        clubs = club_session.get(f"{API}/club/mine").json()
        cid = clubs[0]["id"]
        r = club_session.put(f"{API}/club/{cid}/registration", json={
            "registration_open": True, "season": "2026", "slots_total": 100, "slots_taken": 5, "licensees": 120
        })
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["registration_open"] is True
        assert d["slots_total"] == 100
        assert d["subscription"]["tier"] == "Club moyen"

    def test_club_enrollments(self, club_session):
        clubs = club_session.get(f"{API}/club/mine").json()
        cid = clubs[0]["id"]
        r = club_session.get(f"{API}/club/{cid}/enrollments")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_subscribe(self, club_session):
        clubs = club_session.get(f"{API}/club/mine").json()
        cid = clubs[0]["id"]
        r = club_session.post(f"{API}/club/{cid}/subscribe")
        assert r.status_code == 200
        d = r.json()
        assert d["ok"] is True
        assert d["mock_payment"] is True
        assert "subscription" in d and "tier" in d["subscription"]

    def test_announce(self, club_session):
        clubs = club_session.get(f"{API}/club/mine").json()
        cid = clubs[0]["id"]
        r = club_session.post(f"{API}/club/{cid}/announce", json={"subject": "TEST", "message": "Hello"})
        assert r.status_code == 200
        assert r.json()["ok"] is True
        assert r.json()["mock_email"] is True

    def test_club_endpoints_require_auth(self, anon_session):
        # /club/mine should be 401
        assert anon_session.get(f"{API}/club/mine").status_code == 401
        assert anon_session.put(f"{API}/club/xxx", json={}).status_code == 401
        assert anon_session.post(f"{API}/club/xxx/subscribe").status_code == 401

    def test_club_endpoints_forbid_participant(self):
        s = requests.Session()
        email = f"TEST_part_{uuid.uuid4().hex[:8]}@example.com"
        s.post(f"{API}/auth/register", json={"name": "P", "email": email, "password": "Passw0rd!", "role": "participant"})
        r = s.get(f"{API}/club/mine")
        assert r.status_code == 403


# ---------- CLAIM FLOW ----------
class TestClaimFlow:
    def test_claim_and_admin_approve(self, admin_session, anon_session):
        # Create a fresh club user
        s = requests.Session()
        email = f"TEST_club_{uuid.uuid4().hex[:8]}@example.com"
        reg = s.post(f"{API}/auth/register", json={
            "name": "Test Club Owner", "email": email, "password": "Passw0rd!", "role": "club"
        })
        assert reg.status_code == 200

        # Find a ghost club
        r = anon_session.get(f"{API}/clubs", params={"status": "ghost", "limit": 5})
        results = r.json()["results"]
        assert len(results) > 0, "No ghost club to claim"
        ghost = results[0]

        # Claim
        r = s.post(f"{API}/clubs/{ghost['id']}/claim")
        assert r.status_code == 200, r.text
        claim = r.json()
        assert claim["status"] == "pending"

        # Verify status changed to 'claimed'
        r = anon_session.get(f"{API}/clubs/{ghost['id']}")
        assert r.json()["status"] == "claimed"

        # Admin sees the claim
        r = admin_session.get(f"{API}/admin/claims")
        assert r.status_code == 200
        assert any(c["id"] == claim["id"] for c in r.json())

        # Admin approves
        r = admin_session.post(f"{API}/admin/claims/{claim['id']}/approve")
        assert r.status_code == 200
        assert r.json()["ok"] is True

        # Club is now active + owner set
        r = anon_session.get(f"{API}/clubs/{ghost['id']}")
        d = r.json()
        assert d["status"] == "active"

        # The claiming user now sees it in /club/mine
        r = s.get(f"{API}/club/mine")
        assert r.status_code == 200
        assert any(c["id"] == ghost["id"] for c in r.json())

    def test_claim_requires_club_role(self):
        s = requests.Session()
        email = f"TEST_part_{uuid.uuid4().hex[:8]}@example.com"
        s.post(f"{API}/auth/register", json={"name": "P", "email": email, "password": "Passw0rd!", "role": "participant"})
        # any club id will do; role check happens first
        r = s.get(f"{API}/clubs", params={"limit": 1})
        cid = r.json()["results"][0]["id"]
        r = s.post(f"{API}/clubs/{cid}/claim")
        assert r.status_code == 403


# ---------- ADMIN ----------
class TestAdmin:
    def test_admin_stats(self, admin_session):
        r = admin_session.get(f"{API}/admin/stats")
        assert r.status_code == 200
        d = r.json()
        for k in ["clubs_total", "clubs_active", "clubs_claimed", "clubs_ghost", "enrollments", "pending_claims", "users"]:
            assert k in d and isinstance(d[k], int)
        assert d["clubs_total"] > 0

    def test_admin_stats_requires_admin(self, club_session, anon_session):
        assert club_session.get(f"{API}/admin/stats").status_code == 403
        assert anon_session.get(f"{API}/admin/stats").status_code == 401

    def test_admin_claims(self, admin_session):
        r = admin_session.get(f"{API}/admin/claims")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_reject_action_invalid(self, admin_session):
        r = admin_session.post(f"{API}/admin/claims/nope/xxxx")
        assert r.status_code in (400, 404)

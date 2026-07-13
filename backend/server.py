from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import logging
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List

import bcrypt
import jwt
from bson import ObjectId
from fastapi import FastAPI, APIRouter, Request, Response, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sportconnect")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="SportConnect API")
api = APIRouter(prefix="/api")

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALG = "HS256"

# ----------------------------------------------------------------------------
# Auth helpers
# ----------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token", value=token, httponly=True, secure=True,
        samesite="none", max_age=604800, path="/",
    )


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifie")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expiree")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")


async def require_role(user: dict, *roles: str):
    if user["role"] not in roles:
        raise HTTPException(status_code=403, detail="Acces refuse")


# ----------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------

class RegisterInput(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "participant"  # participant | club


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class ClubUpdateInput(BaseModel):
    description: Optional[str] = None
    level: Optional[str] = None
    fees: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    schedule: Optional[str] = None
    photos: Optional[List[str]] = None
    sports: Optional[List[str]] = None


class RegistrationSettingsInput(BaseModel):
    registration_open: bool
    season: str = "Saison en cours"
    slots_total: int = 0
    slots_taken: int = 0
    licensees: int = 0


class EnrollInput(BaseModel):
    participant_name: str
    participant_email: EmailStr
    participant_age: int
    phone: Optional[str] = None
    notes: Optional[str] = None


class AnnounceInput(BaseModel):
    subject: str
    message: str


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def club_public(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


def subscription_tier(licensees: int) -> dict:
    if licensees < 100:
        return {"tier": "Petit club", "range": "< 100 licencies", "price_year": 199}
    if licensees <= 500:
        return {"tier": "Club moyen", "range": "100 - 500 licencies", "price_year": 499}
    return {"tier": "Grand club", "range": "> 500 licencies", "price_year": 999}


async def send_mock_email(to: str, subject: str, body: str):
    logger.info("[EMAIL MOCK] -> %s | %s | %s", to, subject, body[:120])


# ----------------------------------------------------------------------------
# Auth routes
# ----------------------------------------------------------------------------

@api.post("/auth/register")
async def register(data: RegisterInput, response: Response):
    email = data.email.lower()
    if data.role not in ("participant", "club"):
        raise HTTPException(status_code=400, detail="Role invalide")
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Cet email est deja utilise")
    doc = {
        "name": data.name,
        "email": email,
        "password_hash": hash_password(data.password),
        "role": data.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(doc)
    uid = str(result.inserted_id)
    token = create_access_token(uid, email, data.role)
    set_auth_cookie(response, token)
    return {"id": uid, "name": data.name, "email": email, "role": data.role}


@api.post("/auth/login")
async def login(data: LoginInput, response: Response):
    email = data.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    uid = str(user["_id"])
    token = create_access_token(uid, email, user["role"])
    set_auth_cookie(response, token)
    return {"id": uid, "name": user.get("name"), "email": email, "role": user["role"]}


@api.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return user


# ----------------------------------------------------------------------------
# Sports / search
# ----------------------------------------------------------------------------

@api.get("/sports")
async def list_sports():
    pipeline = [
        {"$unwind": "$sports"},
        {"$group": {"_id": "$sports", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    rows = await db.clubs.aggregate(pipeline).to_list(200)
    return [{"name": r["_id"], "count": r["count"]} for r in rows if r["_id"]]


@api.get("/cities")
async def list_cities():
    rows = await db.clubs.distinct("city")
    return sorted([c for c in rows if c])


@api.get("/clubs")
async def search_clubs(
    sport: Optional[str] = None,
    postal_code: Optional[str] = None,
    city: Optional[str] = None,
    age: Optional[int] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    page: int = 1,
    limit: int = 24,
):
    query: dict = {}
    if sport:
        query["sports"] = sport
    if postal_code:
        query["postal_code"] = {"$regex": f"^{postal_code}"}
    if city:
        query["city"] = city
    if status:
        query["status"] = status
    if age is not None:
        query["age_min"] = {"$lte": age}
        query["age_max"] = {"$gte": age}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}

    total = await db.clubs.count_documents(query)
    skip = max(0, (page - 1) * limit)
    docs = await db.clubs.find(query).sort([("registration_open", -1), ("name", 1)]).skip(skip).limit(limit).to_list(limit)
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": [club_public(d) for d in docs],
    }


@api.get("/clubs/{club_id}")
async def get_club(club_id: str):
    doc = await db.clubs.find_one({"id": club_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Club introuvable")
    return club_public(doc)


# ----------------------------------------------------------------------------
# Claim + club management
# ----------------------------------------------------------------------------

@api.post("/clubs/{club_id}/claim")
async def claim_club(club_id: str, user: dict = Depends(get_current_user)):
    await require_role(user, "club")
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club introuvable")
    if club.get("status") == "active":
        raise HTTPException(status_code=400, detail="Ce club est deja active")
    existing = await db.claims.find_one({"club_id": club_id, "user_id": user["id"], "status": "pending"})
    if existing:
        raise HTTPException(status_code=400, detail="Revendication deja en attente")
    claim = {
        "id": secrets.token_hex(8),
        "club_id": club_id,
        "club_name": club["name"],
        "user_id": user["id"],
        "user_name": user["name"],
        "user_email": user["email"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.claims.insert_one(claim)
    await db.clubs.update_one({"id": club_id}, {"$set": {"status": "claimed"}})
    await send_mock_email(user["email"], "Revendication recue", f"Votre demande pour {club['name']} est en cours de moderation.")
    claim.pop("_id", None)
    return claim


@api.get("/club/mine")
async def my_clubs(user: dict = Depends(get_current_user)):
    await require_role(user, "club")
    docs = await db.clubs.find({"owner_id": user["id"]}).to_list(100)
    return [club_public(d) for d in docs]


async def _owned_club(club_id: str, user: dict) -> dict:
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club introuvable")
    if club.get("owner_id") != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Vous ne gerez pas ce club")
    return club


@api.put("/club/{club_id}")
async def update_club(club_id: str, data: ClubUpdateInput, user: dict = Depends(get_current_user)):
    await require_role(user, "club", "admin")
    await _owned_club(club_id, user)
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    if update:
        await db.clubs.update_one({"id": club_id}, {"$set": update})
    doc = await db.clubs.find_one({"id": club_id})
    return club_public(doc)


@api.put("/club/{club_id}/registration")
async def update_registration(club_id: str, data: RegistrationSettingsInput, user: dict = Depends(get_current_user)):
    await require_role(user, "club", "admin")
    await _owned_club(club_id, user)
    await db.clubs.update_one({"id": club_id}, {"$set": {
        "registration_open": data.registration_open,
        "season": data.season,
        "slots_total": data.slots_total,
        "slots_taken": data.slots_taken,
        "licensees": data.licensees,
        "subscription": subscription_tier(data.licensees),
    }})
    doc = await db.clubs.find_one({"id": club_id})
    return club_public(doc)


@api.get("/club/{club_id}/enrollments")
async def club_enrollments(club_id: str, user: dict = Depends(get_current_user)):
    await require_role(user, "club", "admin")
    await _owned_club(club_id, user)
    docs = await db.enrollments.find({"club_id": club_id}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return docs


@api.get("/club/{club_id}/subscription")
async def club_subscription(club_id: str, user: dict = Depends(get_current_user)):
    await require_role(user, "club", "admin")
    club = await _owned_club(club_id, user)
    return subscription_tier(club.get("licensees", 0))


@api.post("/club/{club_id}/subscribe")
async def club_subscribe(club_id: str, user: dict = Depends(get_current_user)):
    await require_role(user, "club", "admin")
    club = await _owned_club(club_id, user)
    tier = subscription_tier(club.get("licensees", 0))
    await db.clubs.update_one({"id": club_id}, {"$set": {
        "subscription_active": True,
        "subscription_paid_at": datetime.now(timezone.utc).isoformat(),
        "subscription": tier,
    }})
    await send_mock_email(user["email"], "Abonnement actif", f"Abonnement {tier['tier']} ({tier['price_year']} EUR/an) confirme.")
    return {"ok": True, "mock_payment": True, "subscription": tier}


@api.post("/club/{club_id}/announce")
async def announce(club_id: str, data: AnnounceInput, user: dict = Depends(get_current_user)):
    await require_role(user, "club", "admin")
    await _owned_club(club_id, user)
    members = await db.enrollments.find({"club_id": club_id}).to_list(1000)
    for m in members:
        await send_mock_email(m["participant_email"], data.subject, data.message)
    return {"ok": True, "recipients": len(members), "mock_email": True}


# ----------------------------------------------------------------------------
# Enrollment (participant) + mock payment
# ----------------------------------------------------------------------------

@api.post("/clubs/{club_id}/enroll")
async def enroll(club_id: str, data: EnrollInput, request: Request):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club introuvable")
    if not club.get("registration_open"):
        raise HTTPException(status_code=400, detail="Les inscriptions sont fermees pour ce club")

    user_id = None
    try:
        u = await get_current_user(request)
        user_id = u["id"]
    except HTTPException:
        pass

    enrollment = {
        "id": secrets.token_hex(8),
        "club_id": club_id,
        "club_name": club["name"],
        "user_id": user_id,
        "participant_name": data.participant_name,
        "participant_email": data.participant_email.lower(),
        "participant_age": data.participant_age,
        "phone": data.phone,
        "notes": data.notes,
        "fees": club.get("fees"),
        "season": club.get("season", "Saison en cours"),
        "payment_status": "paid",  # MOCK payment
        "mock_payment": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.enrollments.insert_one(enrollment)
    await db.clubs.update_one({"id": club_id}, {"$inc": {"slots_taken": 1}})
    await send_mock_email(
        data.participant_email,
        f"Inscription confirmee - {club['name']}",
        f"Bonjour {data.participant_name}, votre inscription et paiement (simule) sont confirmes.",
    )
    enrollment.pop("_id", None)
    return enrollment


@api.get("/my/enrollments")
async def my_enrollments(user: dict = Depends(get_current_user)):
    docs = await db.enrollments.find(
        {"$or": [{"user_id": user["id"]}, {"participant_email": user["email"]}]}, {"_id": 0}
    ).sort("created_at", -1).to_list(200)
    return docs


# ----------------------------------------------------------------------------
# Admin
# ----------------------------------------------------------------------------

@api.get("/admin/stats")
async def admin_stats(user: dict = Depends(get_current_user)):
    await require_role(user, "admin")
    return {
        "clubs_total": await db.clubs.count_documents({}),
        "clubs_active": await db.clubs.count_documents({"status": "active"}),
        "clubs_claimed": await db.clubs.count_documents({"status": "claimed"}),
        "clubs_ghost": await db.clubs.count_documents({"status": "ghost"}),
        "enrollments": await db.enrollments.count_documents({}),
        "pending_claims": await db.claims.count_documents({"status": "pending"}),
        "users": await db.users.count_documents({}),
    }


@api.get("/admin/claims")
async def admin_claims(user: dict = Depends(get_current_user)):
    await require_role(user, "admin")
    docs = await db.claims.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return docs


@api.post("/admin/claims/{claim_id}/{action}")
async def resolve_claim(claim_id: str, action: str, user: dict = Depends(get_current_user)):
    await require_role(user, "admin")
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action invalide")
    claim = await db.claims.find_one({"id": claim_id})
    if not claim:
        raise HTTPException(status_code=404, detail="Revendication introuvable")
    if action == "approve":
        await db.claims.update_one({"id": claim_id}, {"$set": {"status": "approved"}})
        await db.clubs.update_one({"id": claim["club_id"]}, {"$set": {
            "status": "active", "owner_id": claim["user_id"], "owner_name": claim["user_name"],
        }})
        await send_mock_email(claim["user_email"], "Page activee", f"{claim['club_name']} est maintenant active. Vous pouvez la gerer.")
    else:
        await db.claims.update_one({"id": claim_id}, {"$set": {"status": "rejected"}})
        await db.clubs.update_one({"id": claim["club_id"]}, {"$set": {"status": "ghost"}})
        await send_mock_email(claim["user_email"], "Revendication refusee", f"Votre demande pour {claim['club_name']} a ete refusee.")
    return {"ok": True, "action": action}


@api.get("/")
async def root():
    return {"service": "SportConnect", "zone": "Haute-Garonne (31)"}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.clubs.create_index("id", unique=True)
    await db.clubs.create_index("sports")
    await db.clubs.create_index("postal_code")
    admin_email = os.environ["ADMIN_EMAIL"].lower()
    admin_password = os.environ["ADMIN_PASSWORD"]
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "name": "Admin SportConnect", "email": admin_email,
            "password_hash": hash_password(admin_password), "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Admin seeded: %s", admin_email)
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})


@app.on_event("shutdown")
async def shutdown():
    client.close()

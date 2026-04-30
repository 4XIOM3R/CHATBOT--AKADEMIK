from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.models import User
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS
from api.deps import get_db
from services.browser import init_browser
from services.auth import login as sia_login_func
from endpoints.khs import fetch_khs
from endpoints.absen import fetch_absen
from endpoints.pembayaran import fetch_pembayaran
from pipelines.khs_pipeline import run_khs_pipeline
from pipelines.absen_pipeline import run_absen_pipeline
from pipelines.pembayaran_pipeline import run_pembayaran_pipeline
import uuid

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# SCHEMA
# =========================
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# HELPER
# =========================
def hash_password(password: str) -> str:
    # Bcrypt has a 72-byte limit
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(data.password)

    new_user = User(
        email=data.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created",
        "user_id": str(new_user.id)
    }


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================
# SIA LOGIN & SYNC
# =========================
@router.post("/sia-login")
def sia_login(db: Session = Depends(get_db)):
    driver = init_browser()
    try:
        # 1. Login Manual via Browser
        success = sia_login_func(driver)
        if not success:
            raise HTTPException(status_code=401, detail="Login SIA gagal atau timeout")

        # 2. Identifikasi atau Buat User
        # Untuk kemudahan, kita gunakan user default jika belum ada
        user = db.query(User).first()
        if not user:
            user = User(
                email="mahasiswa@uty.ac.id",
                password=hash_password("password_default")
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        user_uuid = user.id

        # 3. Langsung Sync Data
        khs_res = fetch_khs(driver)
        absen_res = fetch_absen(driver)
        pay_res = fetch_pembayaran(driver)

        # 4. Jalankan Pipeline
        run_khs_pipeline(user_id=user_uuid, khs_json=khs_res.get("data", []))
        run_absen_pipeline(user_id=user_uuid, absen_json=absen_res)
        run_pembayaran_pipeline(user_id=user_uuid, pembayaran_json=pay_res.get("data", []))

        # 5. Generate Token
        payload = {
            "sub": str(user_uuid),
            "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Login & Sync Berhasil"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SIA Login Error: {str(e)}")
    finally:
        driver.quit()
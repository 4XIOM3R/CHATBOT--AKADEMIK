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
from services.alert_handler import dismiss_all_alerts
import uuid
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# SKEMA
# =========================
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# FUNGSI PEMBANTU
# =========================
def hash_password(password: str) -> str:
    # Bcrypt memiliki batas 72-byte
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)


# =========================
# DAFTAR
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
# MASUK
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
# LOGIN SIA & SINKRONISASI
# =========================
@router.post("/sia-login")
def sia_login(db: Session = Depends(get_db)):
    driver = None
    sync_status = {
        "khs": "pending",
        "absen": "pending",
        "pembayaran": "pending"
    }

    try:
        logger.info("[SIA-LOGIN] Initializing browser...")
        driver = init_browser()

        # 1. Login Manual via Browser
        logger.info("[SIA-LOGIN] Waiting for manual login (5 min timeout)...")
        success = sia_login_func(driver)
        if not success:
            raise HTTPException(status_code=401, detail="Login SIA gagal atau timeout")

        logger.info("[SIA-LOGIN] Login successful!")

        # 2. Identifikasi atau Buat User
        logger.info("[SIA-LOGIN] Getting or creating user...")
        user = db.query(User).first()
        if not user:
            user = User(
                email="mahasiswa@uty.ac.id",
                password=hash_password("password_default")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"[SIA-LOGIN] Created new user: {user.id}")

        user_uuid = user.id

        # 3. Langsung Sync Data
        logger.info(f"[SIA-LOGIN] Starting data sync for user: {user_uuid}")

        try:
            logger.info("[SYNC] Fetching KHS...")
            start = time.time()
            khs_res = fetch_khs(driver)
            sync_status["khs"] = "success"
            logger.info(f"[SYNC] KHS fetched in {time.time()-start:.2f}s: {len(khs_res.get('data', []))} records")
        except Exception as e:
            sync_status["khs"] = f"error: {str(e)}"
            logger.error(f"[SYNC] KHS failed: {str(e)}")
            raise

        try:
            logger.info("[SYNC] Fetching ABSEN...")
            start = time.time()
            absen_res = fetch_absen(driver)
            sync_status["absen"] = "success"
            logger.info(f"[SYNC] ABSEN fetched in {time.time()-start:.2f}s: {len(absen_res)} records")
        except Exception as e:
            sync_status["absen"] = f"error: {str(e)}"
            logger.error(f"[SYNC] ABSEN failed: {str(e)}")
            raise

        try:
            logger.info("[SYNC] Fetching PEMBAYARAN...")
            start = time.time()
            pay_res = fetch_pembayaran(driver)
            sync_status["pembayaran"] = "success"
            logger.info(f"[SYNC] PEMBAYARAN fetched in {time.time()-start:.2f}s: {len(pay_res.get('data', []))} records")
        except Exception as e:
            sync_status["pembayaran"] = f"error: {str(e)}"
            logger.error(f"[SYNC] PEMBAYARAN failed: {str(e)}")
            raise

        # 4. Jalankan Pipeline (Database Insert)
        logger.info("[SYNC] Running pipelines to insert data to database...")
        try:
            logger.info("[PIPELINE] Inserting KHS data...")
            run_khs_pipeline(db=db, user_id=user_uuid, khs_json=khs_res.get("data", []))
            logger.info("[PIPELINE] KHS inserted successfully")

            logger.info("[PIPELINE] Inserting ABSEN data...")
            run_absen_pipeline(db=db, user_id=user_uuid, absen_json=absen_res)
            logger.info("[PIPELINE] ABSEN inserted successfully")

            logger.info("[PIPELINE] Inserting PEMBAYARAN data...")
            run_pembayaran_pipeline(db=db, user_id=user_uuid, pembayaran_json=pay_res.get("data", []))
            logger.info("[PIPELINE] PEMBAYARAN inserted successfully")

            db.commit()
            logger.info("[PIPELINE] All data committed to database")

        except Exception as e:
            db.rollback()
            logger.error(f"[PIPELINE] Error during data insertion: {str(e)}")
            raise

        # 5. Generate Token
        logger.info("[SIA-LOGIN] Generating authentication token...")
        payload = {
            "sub": str(user_uuid),
            "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        logger.info("[SIA-LOGIN] Login and sync completed successfully!")
        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Login & Sinkronisasi Data Berhasil",
            "user_id": str(user_uuid),
            "sync_status": sync_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[SIA-LOGIN] Error: {error_msg}")

        # Pesan error yang lebih baik untuk masalah umum SIA
        if "pembayaran" in error_msg.lower() or "tunggakan" in error_msg.lower():
            detail = "Login gagal: Akun memiliki tunggakan pembayaran. Mohon lunasi terlebih dahulu di SIA UTY."
        elif "timeout" in error_msg.lower():
            detail = "Login timeout: Mohon ulangi dan selesaikan login dalam 5 menit."
        elif "alert" in error_msg.lower():
            detail = f"Login gagal karena alert: {error_msg}"
        elif "fetch" in error_msg.lower() or "khs" in error_msg.lower() or "absen" in error_msg.lower():
            detail = f"Gagal mengambil data akademik: {error_msg}. Mohon coba lagi atau hubungi admin."
        else:
            detail = f"SIA Login Error: {error_msg}"

        raise HTTPException(status_code=500, detail=detail)

    finally:
        if driver:
            logger.info("[SIA-LOGIN] Closing browser...")
            dismiss_all_alerts(driver, timeout=1)
            driver.quit()
            logger.info("[SIA-LOGIN] Browser closed")
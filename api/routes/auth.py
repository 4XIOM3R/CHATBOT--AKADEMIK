from fastapi import APIRouter, HTTPException
from db.session import SessionLocal
from db.models import User
from passlib.context import CryptContext
from jose import jwt
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS


router = APIRouter()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# SCHEMA
# =========================
class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: RegisterRequest):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == data.email).first()

        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        password = data.password[:72]
        hashed_password = pwd_context.hash(password)

        new_user = User(
            email=data.email,
            password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User created", "user_id": str(new_user.id)}


        return {"message": "User created", "user_id": user_id}

    finally:
        db.close()


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data.email).first()


        if not user:
            raise HTTPException(status_code=401, detail="Invalid email")

        # 🔥 FIX DI SINI
        if not pwd_context.verify(data.password[:72], user.password):
            raise HTTPException(status_code=401, detail="Wrong password")

        payload = {
            "sub": str(user.id),
            "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        db.close()
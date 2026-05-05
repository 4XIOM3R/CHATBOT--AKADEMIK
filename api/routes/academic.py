from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_current_user, get_db
from services import academic_service

router = APIRouter()

@router.get("/khs")
def get_khs(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return academic_service.get_khs_by_user(db, user_id)

@router.get("/ips")
def get_ips(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return academic_service.get_ips_per_semester(db, user_id)

@router.get("/ipk")
def get_ipk(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return {"ipk": academic_service.get_ipk(db, user_id)}

@router.get("/absen")
def get_absen(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return academic_service.get_absen_by_user(db, user_id)

@router.get("/pembayaran")
def get_pembayaran(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return academic_service.get_pembayaran_by_user(db, user_id)


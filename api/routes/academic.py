from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_current_user, get_db
from services import academic_service

router = APIRouter()

@router.get("/khs")
def get_khs(user_id: str = Depends(get_current_user)):
    return academic_service.get_khs_by_user(user_id)

@router.get("/ips")
def get_ips(user_id: str = Depends(get_current_user)):
    return academic_service.get_ips_per_semester(user_id)

@router.get("/ipk")
def get_ipk(user_id: str = Depends(get_current_user)):
    return {"ipk": academic_service.get_ipk(user_id)}

@router.get("/absen")
def get_absen(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Note: Absen service not implemented in academic_service.py, 
    # choosing to keep raw SQL or implement it in service. 
    # For now, let's keep it here but we could extend the service.
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT c.name, c.sks, a.hadir, a.izin, a.alpha
        FROM absensi a
        JOIN courses c ON a.course_id = c.id
        WHERE a.user_id = :user_id
    """), {"user_id": user_id})

    return [
        {
            "mata_kuliah": row[0],
            "sks": row[1],
            "hadir": row[2],
            "izin": row[3],
            "alpha": row[4]
        }
        for row in result
    ]

@router.get("/pembayaran")
def get_pembayaran(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT jenis, tahun_ajaran, semester, tagihan
        FROM pembayaran
        WHERE user_id = :user_id
    """), {"user_id": user_id})

    return [
        {
            "jenis": row[0],
            "tahun_ajaran": row[1],
            "semester": row[2],
            "tagihan": row[3]
        }
        for row in result
    ]


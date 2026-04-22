from fastapi import APIRouter, Depends
from db.session import SessionLocal
from sqlalchemy import text
from api.deps import get_current_user

router = APIRouter()


# =========================
# KHS (PER USER)
# =========================
@router.get("/khs")
def get_khs(user_id: str = Depends(get_current_user)):  # 🔥 FIX DI SINI
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                k.semester,
                c.kode,
                c.name,
                c.sks,
                k.grade,
                k.weight,
                k.total
            FROM khs k
            JOIN courses c ON k.course_id = c.id
            WHERE k.user_id = :user_id
            ORDER BY k.semester;
        """), {"user_id": user_id})

        return [
            {
                "semester": row[0],
                "kode": row[1],
                "mata_kuliah": row[2],
                "sks": row[3],
                "nilai": row[4],
                "bobot": row[5],
                "total": row[6],
            }
            for row in result
        ]
    finally:
        db.close()


# =========================
# IPS (PER USER)
# =========================
@router.get("/ips")
def get_ips(user_id: str = Depends(get_current_user)):  # 🔥 FIX DI SINI
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                semester,
                ROUND((SUM(total)/SUM(c.sks))::numeric, 2) as ips
            FROM khs k
            JOIN courses c ON k.course_id = c.id
            WHERE k.user_id = :user_id
            GROUP BY semester
            ORDER BY semester;
        """), {"user_id": user_id})

        return [
            {"semester": row[0], "ips": float(row[1])}
            for row in result
        ]
    finally:
        db.close()


# =========================
# IPK (PER USER)
# =========================
@router.get("/ipk")
def get_ipk(user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT ROUND((SUM(total)/SUM(c.sks))::numeric, 2)
            FROM khs k
            JOIN courses c ON k.course_id = c.id
            WHERE k.user_id = :user_id;
        """), {"user_id": user_id}).scalar()

        return {"ipk": float(result) if result else 0}
    finally:
        db.close()


# =========================
# ABSEN (PER USER)
# =========================
@router.get("/absen")
def get_absen(user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                c.name,
                c.sks,
                a.hadir,
                a.izin,
                a.alpha
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
    finally:
        db.close()


# =========================
# PEMBAYARAN (PER USER)
# =========================
@router.get("/pembayaran")
def get_pembayaran(user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
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
    finally:
        db.close()
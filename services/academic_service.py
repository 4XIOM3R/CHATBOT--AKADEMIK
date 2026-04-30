from db.session import SessionLocal
from db.models import KHS, Course, Absen, Pembayaran
from sqlalchemy import func


def get_khs_by_user(user_id: str):
    db = SessionLocal()
    try:
        data = (
            db.query(
                KHS.semester,
                Course.kode,
                Course.name,
                Course.sks,
                KHS.grade,
                KHS.weight,
                KHS.total,
            )
            .join(Course, Course.id == KHS.course_id)
            .filter(KHS.user_id == user_id)
            .order_by(KHS.semester)
            .all()
        )

        return [
            {
                "semester": row.semester,
                "kode": row.kode,
                "mata_kuliah": row.name,
                "sks": row.sks,
                "nilai": row.grade,
                "bobot": row.weight,
                "total": row.total,
            }
            for row in data
        ]
    finally:
        db.close()


def get_absen_by_user(user_id: str):
    db = SessionLocal()
    try:
        data = (
            db.query(
                Course.name,
                Absen.hadir,
                Absen.izin,
                Absen.alpha
            )
            .join(Course, Course.id == Absen.course_id)
            .filter(Absen.user_id == user_id)
            .all()
        )

        return [
            {
                "mata_kuliah": row.name,
                "hadir": row.hadir,
                "izin": row.izin,
                "alpha": row.alpha,
            }
            for row in data
        ]
    finally:
        db.close()


def get_pembayaran_by_user(user_id: str):
    db = SessionLocal()
    try:
        data = (
            db.query(Pembayaran)
            .filter(Pembayaran.user_id == user_id)
            .all()
        )

        return [
            {
                "jenis": row.jenis,
                "tahun_ajaran": row.tahun_ajaran,
                "semester": row.semester,
                "tagihan": row.tagihan,
            }
            for row in data
        ]
    finally:
        db.close()


def get_ipk(user_id: str):
    db = SessionLocal()
    try:
        result = db.query(
            func.sum(KHS.total).label("total_nilai"),
            func.sum(Course.sks).label("total_sks"), # Should use Course.sks for IPK weight usually, or KHS.weight if it reflects SKS
        ).join(Course, Course.id == KHS.course_id).filter(KHS.user_id == user_id).first()

        if not result or not result.total_sks:
            return 0

        return round(float(result.total_nilai) / float(result.total_sks), 2)
    finally:
        db.close()


def get_ips_per_semester(user_id: str):
    db = SessionLocal()
    try:
        data = db.query(
            KHS.semester,
            func.sum(KHS.total).label("total_nilai"),
            func.sum(Course.sks).label("total_sks"),
        ).join(Course, Course.id == KHS.course_id).filter(
            KHS.user_id == user_id
        ).group_by(KHS.semester).all()

        return [
            {
                "semester": row.semester,
                "ips": round(float(row.total_nilai) / float(row.total_sks), 2)
                if row.total_sks else 0
            }
            for row in data
        ]
    finally:
        db.close()

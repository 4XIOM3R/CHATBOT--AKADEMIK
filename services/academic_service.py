from db.session import SessionLocal
from db.models import KHS, Course
from sqlalchemy import func


def get_khs_by_user(user_id: str):
    db = SessionLocal()
    try:
        data = (
            db.query(
                KHS.semester,
                Course.code,
                Course.name,
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
                "kode": row.code,
                "mata_kuliah": row.name,
                "nilai": row.grade,
                "bobot": row.weight,
                "total": row.total,
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
            func.sum(KHS.weight).label("total_sks"),
        ).filter(KHS.user_id == user_id).first()

        if not result or result.total_sks == 0:
            return 0

        return round(result.total_nilai / result.total_sks, 2)
    finally:
        db.close()


def get_ips_per_semester(user_id: str):
    db = SessionLocal()
    try:
        data = db.query(
            KHS.semester,
            func.sum(KHS.total).label("total_nilai"),
            func.sum(KHS.weight).label("total_sks"),
        ).filter(
            KHS.user_id == user_id
        ).group_by(KHS.semester).all()

        return [
            {
                "semester": row.semester,
                "ips": round(row.total_nilai / row.total_sks, 2)
                if row.total_sks else 0
            }
            for row in data
        ]
    finally:
        db.close()
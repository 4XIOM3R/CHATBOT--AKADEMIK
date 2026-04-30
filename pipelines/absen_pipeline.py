import logging
from db.session import SessionLocal
from db.models import Absen, Course

logger = logging.getLogger(__name__)

def get_or_create_course(db, kode: str, nama: str):
    course = db.query(Course).filter(Course.kode == kode).first()

    if course:
        if nama and nama != "Unknown":
            course.name = nama
        return course

    course = Course(kode=kode, name=nama)
    db.add(course)
    db.flush()
    return course


def run_absen_pipeline(user_id, absen_json):
    db = SessionLocal()

    try:
        db.query(Absen).filter(Absen.user_id == user_id).delete()

        for item in absen_json:
            nama_mk = item.get("mata_kuliah", "Unknown")
            # Jika kode tidak ada, gunakan nama matakuliah sebagai kode (lebih aman daripada split kata pertama)
            kode_mk = item.get("kode", nama_mk)

            course = get_or_create_course(db, kode_mk, nama_mk)
            pertemuan = item.get("pertemuan", {})

            h, i, a = 0, 0, 0
            for status in pertemuan.values():
                status = str(status).upper()
                if status == "H":
                    h += 1
                elif status in ["I", "S"]:
                    i += 1
                elif status == "A":
                    a += 1

            db.add(Absen(
                user_id=user_id,
                course_id=course.id,
                hadir=h,
                izin=i,
                alpha=a,
            ))

        db.commit()
        logger.info(f"✅ Absen Pipeline success for user {user_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ ERROR Absen Pipeline: {str(e)}")
        raise

    finally:
        db.close()
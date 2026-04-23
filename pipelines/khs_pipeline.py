import logging
from db.session import SessionLocal
from db.models import KHS, Course

logger = logging.getLogger(__name__)

def get_or_create_course(db, kode, nama, sks):
    course = db.query(Course).filter(Course.kode == kode).first()

    if course:
        # Update name/sks if changed
        course.name = nama
        course.sks = sks
        return course

    course = Course(kode=kode, name=nama, sks=sks)
    db.add(course)
    db.flush()
    return course


def run_khs_pipeline(user_id, khs_json):
    db = SessionLocal()

    try:
        db.query(KHS).filter(KHS.user_id == user_id).delete()

        for item in khs_json:
            course = get_or_create_course(
                db,
                kode=item["kode"],
                nama=item["mata_kuliah"],
                sks=int(item["sks"]),
            )

            db.add(KHS(
                user_id=user_id,
                course_id=course.id,
                semester=int(item["semester"]),
                grade=item["nilai"],
                weight=float(item["bobot"]),
                total=float(item["total"]),
            ))

        db.commit()
        logger.info(f"✅ KHS Pipeline success for user {user_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ ERROR KHS Pipeline: {str(e)}")
        raise

    finally:
        db.close()
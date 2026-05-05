import logging
from collections import Counter
from sqlalchemy.orm import Session
from db.models import KHS, Course, User

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


def calculate_current_semester(khs_json):
    """Hitung current_semester dari data KHS berdasarkan semester tertinggi.
    
    Logic: Ambil semester tertinggi dari semua data KHS.
    Semester berikutnya (tertinggi + 1) adalah semester yang sedang berjalan.
    
    Args:
        khs_json: List of KHS data dicts.
    
    Returns:
        int: Current semester (semester tertinggi + 1), atau 1 jika tidak ada data.
    """
    if not khs_json:
        return 1
    
    semesters = []
    for item in khs_json:
        try:
            sem = int(item.get("semester", 0))
            if sem > 0:
                semesters.append(sem)
        except (ValueError, TypeError):
            continue
    
    if not semesters:
        return 1
    
    # Current semester = semester tertinggi + 1 (karena KHS = semester yang sudah selesai)
    max_semester = max(semesters)
    return max_semester + 1


def update_user_current_semester(db: Session, user_id, current_semester: int):
    """Update current_semester pada User model."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.current_semester = current_semester
        logger.info(f"Updated user {user_id} current_semester to {current_semester}")
    else:
        logger.warning(f"User {user_id} not found, cannot update current_semester")


def run_khs_pipeline(db: Session, user_id, khs_json):
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

        # Hitung dan update current_semester pada User
        current_semester = calculate_current_semester(khs_json)
        update_user_current_semester(db, user_id, current_semester)

        logger.info(f"KHS Pipeline success for user {user_id} (current_semester: {current_semester})")

    except Exception as e:
        logger.error(f"ERROR KHS Pipeline: {str(e)}")
        raise

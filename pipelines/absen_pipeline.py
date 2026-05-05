import logging
from sqlalchemy.orm import Session
from db.models import Absen, Course, User

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


def run_absen_pipeline(db: Session, user_id, absen_json):
    """Pipeline untuk menyimpan data absensi ke database.
    
    Args:
        db: Database session.
        user_id: UUID user.
        absen_json: List data absen, atau dict dengan key 'data' dan 'semester_info'.
    """
    try:
        # Handle both dict format (from fetch_absen) and list format (legacy)
        if isinstance(absen_json, dict):
            absen_data = absen_json.get("data", [])
            semester_info = absen_json.get("semester_info", None)
        else:
            absen_data = absen_json
            semester_info = None
        
        # Dapatkan current_semester dari User untuk di-assign ke absen
        user = db.query(User).filter(User.id == user_id).first()
        current_semester = user.current_semester if user else None
        
        db.query(Absen).filter(Absen.user_id == user_id).delete()

        for item in absen_data:
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
                semester=current_semester,
                hadir=h,
                izin=i,
                alpha=a,
            ))

        logger.info(f"Absen Pipeline success for user {user_id} (semester: {current_semester})")

    except Exception as e:
        logger.error(f"ERROR Absen Pipeline: {str(e)}")
        raise
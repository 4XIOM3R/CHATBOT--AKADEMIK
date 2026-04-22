from db.session import SessionLocal
from db.models import Absen, Course


def get_or_create_course(db, kode: str, nama: str):
    course = db.query(Course).filter(Course.code == kode).first()
    if course:
        return course

    course = Course(code=kode, name=nama)
    db.add(course)
    db.flush()  # biar dapat id
    return course


def run_absen_pipeline(user_id: str, absen_json: list[dict]):
    db = SessionLocal()

    try:
        # 🔥 hapus data lama user
        db.query(Absen).filter(Absen.user_id == user_id).delete()

        for item in absen_json:
            # UTY Absen logic: Ambil kode dari nama jika tidak ada
            nama_mk = item.get("mata_kuliah", "Unknown")
            kode_mk = item.get("kode", nama_mk.split()[0] if " " in nama_mk else nama_mk)

            course = get_or_create_course(
                db,
                kode=kode_mk,
                nama=nama_mk,
            )

            # Hitung rekap dari pertemuan
            pertemuan = item.get("pertemuan", {})
            h = 0
            i = 0
            a = 0
            for status in pertemuan.values():
                if status == "H": h += 1
                elif status == "I" or status == "S": i += 1
                elif status == "A": a += 1

            absen = Absen(
                user_id=user_id,
                course_id=course.id,
                hadir=h,
                izin=i,
                alpha=a,
            )
            db.add(absen)


        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
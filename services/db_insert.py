from db.session import SessionLocal
from db.models import Course, KHS

# =========================
# GET / CREATE COURSE
# =========================
def get_or_create_course(db, kode, name, sks):
    course = db.query(Course).filter_by(kode=kode).first()

    if not course:
        course = Course(
            kode=kode,
            name=name,
            sks=sks
        )
        db.add(course)
        db.commit()
        db.refresh(course)

    return course


# =========================
# INSERT KHS
# =========================
def insert_khs_from_json(khs_json, user_id):
    db = SessionLocal()

    try:
        # 🔥 HAPUS DATA LAMA USER (BIAR TIDAK DUPLIKAT)
        db.query(KHS).filter(KHS.user_id == user_id).delete()

        for item in khs_json["data"]:
            course = get_or_create_course(
                db,
                kode=item["kode"],
                name=item["mata_kuliah"],
                sks=item["sks"]
            )

            khs = KHS(
                user_id=user_id,
                course_id=course.id,
                semester=int(item["semester"]),
                grade=item["nilai"],
                weight=float(item["bobot"]),
                total=float(item["total"])
            )

            db.add(khs)

        db.commit()

    finally:
        db.close()  
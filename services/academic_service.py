from sqlalchemy.orm import Session
from db.models import KHS, Course, Absen, Pembayaran, User
from sqlalchemy import func


def get_user_current_semester(db: Session, user_id: str) -> int:
    """Ambil current_semester dari User. Default 1 jika belum di-set."""
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.current_semester:
        return user.current_semester
    return 1


def get_khs_by_user(db: Session, user_id: str):
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


def get_absen_by_user(db: Session, user_id: str, semester: int = None):
    """Ambil data absen. Jika semester diberikan, filter by semester.
    Jika tidak, gunakan current_semester dari User.
    """
    if semester is None:
        semester = get_user_current_semester(db, user_id)
    
    query = (
        db.query(
            Course.name,
            Absen.hadir,
            Absen.izin,
            Absen.alpha,
            Absen.semester,
        )
        .join(Course, Course.id == Absen.course_id)
        .filter(Absen.user_id == user_id)
    )
    
    # Filter by semester jika absen punya data semester
    if semester:
        query = query.filter(
            (Absen.semester == semester) | (Absen.semester == None)
        )
    
    data = query.all()

    return [
        {
            "mata_kuliah": row.name,
            "hadir": row.hadir,
            "izin": row.izin,
            "alpha": row.alpha,
        }
        for row in data
    ]


def get_pembayaran_by_user(db: Session, user_id: str, semester: int = None):
    """Ambil data pembayaran. Jika semester diberikan, filter by semester.
    Jika tidak, gunakan current_semester dari User.
    """
    if semester is None:
        semester = get_user_current_semester(db, user_id)
    
    query = db.query(Pembayaran).filter(Pembayaran.user_id == user_id)
    
    # Filter by semester (1=Ganjil, 2=Genap)
    if semester:
        # Konversi current_semester ke tipe ganjil/genap: ganjil=1, genap=2
        semester_type = 1 if semester % 2 == 1 else 2
        query = query.filter(Pembayaran.semester == semester_type)
    
    data = query.all()

    return [
        {
            "jenis": row.jenis,
            "tahun_ajaran": row.tahun_ajaran,
            "semester": row.semester,
            "tagihan": row.tagihan,
        }
        for row in data
    ]


def get_pembayaran_all_by_user(db: Session, user_id: str):
    """Ambil SEMUA data pembayaran tanpa filter semester."""
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


def get_ipk(db: Session, user_id: str):
    result = db.query(
        func.sum(KHS.total).label("total_nilai"),
        func.sum(Course.sks).label("total_sks"),
    ).join(Course, Course.id == KHS.course_id).filter(KHS.user_id == user_id).first()

    if not result or not result.total_sks:
        return 0

    return round(float(result.total_nilai) / float(result.total_sks), 2)


def get_ips_per_semester(db: Session, user_id: str):
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

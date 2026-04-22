from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base
import uuid
from datetime import datetime

# =====================
# USER
# =====================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# =====================
# COURSE
# =====================
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    kode = Column(String)
    name = Column(String)
    sks = Column(Integer)
    sks = Column(Integer)


# =====================
# KHS
# =====================
class KHS(Base):
    __tablename__ = "khs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)  # ✅ UUID
    course_id = Column(Integer)
    semester = Column(Integer)
    grade = Column(String)
    weight = Column(Float)
    total = Column(Float)


# =====================
# ABSEN
# =====================
class Absen(Base):
    __tablename__ = "absensi"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    course_id = Column(Integer)
    hadir = Column(Integer, default=0)
    izin = Column(Integer, default=0)
    alpha = Column(Integer, default=0)


# =====================
# PEMBAYARAN
# =====================
class Pembayaran(Base):
    __tablename__ = "pembayaran"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    jenis = Column(String)
    tahun_ajaran = Column(String)
    semester = Column(String)
    tagihan = Column(String)  # string karena ada 'Rp.' dari scraper

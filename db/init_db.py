from db.session import engine
from db.models import Base

# WAJIB import semua model
from db.models import Absen, KHS, Course, Pembayaran, User

Base.metadata.create_all(bind=engine)

print(" Tables created")
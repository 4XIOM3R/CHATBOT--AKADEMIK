import json
from datetime import datetime, timedelta
import uuid

from services.browser import init_browser
from services.auth import login

from endpoints.khs import fetch_khs
from endpoints.absen import fetch_absen
from services.sync_kartu_ujian import sync_kartu_ujian
from endpoints.pembayaran import fetch_pembayaran

from utils.generate_khssmt import generate_khssmt

from db.session import engine, Base
from db import models

from pipelines.khs_pipeline import run_khs_pipeline


# =========================
# INIT DB
# =========================
Base.metadata.create_all(bind=engine)


# =========================
# INIT BROWSER
# =========================
driver = init_browser()


# =========================
# LOGIN
# =========================
login(driver)


# Default user_id untuk manual scraping (bisa diganti dengan id user asli dari tabel users)
TEST_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


# Default user_id untuk manual scraping (bisa diganti dengan id user asli dari tabel users)
TEST_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


# =========================
# KHS
# =========================
khs_result = fetch_khs(driver)

khs_payload = {
    **khs_result,
    "expired_at": (datetime.now() + timedelta(days=30)).isoformat()
}

with open("data/khs.json", "w", encoding="utf-8") as f:
    json.dump(khs_payload, f, indent=2, ensure_ascii=False)

print("\n🎓 KHS DONE")
print("IPK:", khs_result["ipk"])


# =========================
# KHSSMT (GENERATE)
# =========================
khssmt = generate_khssmt(khs_result["data"])

with open("data/khssmt.json", "w", encoding="utf-8") as f:
    json.dump(khssmt, f, indent=2, ensure_ascii=False)

print("\n📊 KHSSMT GENERATED")
print("Jumlah semester:", len(khssmt))


# =========================
# ABSEN
# =========================
absen_result = fetch_absen(driver)

absen_payload = {
    "data": absen_result,
    "expired_at": (datetime.now() + timedelta(days=30)).isoformat()
}

with open("data/absen.json", "w", encoding="utf-8") as f:
    json.dump(absen_payload, f, indent=2, ensure_ascii=False)

print("\n📅 ABSEN DONE")
print("Jumlah matkul:", len(absen_result))


# =========================
# PEMBAYARAN
# =========================
pembayaran = fetch_pembayaran(driver)

with open("data/pembayaran.json", "w", encoding="utf-8") as f:
    json.dump({
        "data": pembayaran["data"],
        "total_tagihan": pembayaran["total_tagihan"],
        "expired_at": (datetime.now() + timedelta(days=30)).isoformat()
    }, f, indent=2, ensure_ascii=False)

print("\n💰 PEMBAYARAN DONE")
print("Jumlah item:", len(pembayaran["data"]))
print("Total:", pembayaran["total_tagihan"])


# =========================
# KARTU UJIAN
# =========================
sync_kartu_ujian(driver, str(TEST_USER_ID))

print("\n🧾 KARTU UJIAN DONE")


from pipelines.absen_pipeline import run_absen_pipeline
from pipelines.pembayaran_pipeline import run_pembayaran_pipeline


# =========================
# INSERT KE DATABASE
# =========================
# Default user_id untuk manual scraping (bisa diganti dengan id user asli dari tabel users)
TEST_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

run_khs_pipeline(user_id=TEST_USER_ID)
run_absen_pipeline(user_id=TEST_USER_ID, absen_json=absen_result)
run_pembayaran_pipeline(user_id=TEST_USER_ID, pembayaran_json=pembayaran["data"])

print("\n✅ INSERT DB DONE")



# =========================
# DONE
# =========================
print("\n🚀 SEMUA SELESAI")
import json
import logging
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
from pipelines.khs_pipeline import run_khs_pipeline
from pipelines.absen_pipeline import run_absen_pipeline
from pipelines.pembayaran_pipeline import run_pembayaran_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Default user_id untuk manual scraping
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

logger.info("🎓 KHS DONE")
logger.info(f"IPK: {khs_result.get('ipk')}")

# =========================
# KHSSMT (GENERATE)
# =========================
khssmt = generate_khssmt(khs_result["data"])
with open("data/khssmt.json", "w", encoding="utf-8") as f:
    json.dump(khssmt, f, indent=2, ensure_ascii=False)

logger.info("📊 KHSSMT GENERATED")

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

logger.info("📅 ABSEN DONE")

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

logger.info("💰 PEMBAYARAN DONE")

# =========================
# KARTU UJIAN
# =========================
sync_kartu_ujian(driver, str(TEST_USER_ID))
logger.info("🧾 KARTU UJIAN DONE")

# =========================
# INSERT KE DATABASE
# =========================
run_khs_pipeline(user_id=TEST_USER_ID, khs_json=khs_result["data"])
run_absen_pipeline(user_id=TEST_USER_ID, absen_json=absen_result)
run_pembayaran_pipeline(user_id=TEST_USER_ID, pembayaran_json=pembayaran["data"])

logger.info("✅ INSERT DB DONE")

# =========================
# DONE
# =========================
driver.quit()
logger.info("🚀 SEMUA SELESAI")
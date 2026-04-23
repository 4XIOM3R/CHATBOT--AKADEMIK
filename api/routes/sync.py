from fastapi import APIRouter, Depends, HTTPException
import uuid
import logging
from api.deps import get_current_user
from services.browser import init_browser
from services.auth import login
from endpoints.khs import fetch_khs
from endpoints.absen import fetch_absen
from endpoints.pembayaran import fetch_pembayaran
from pipelines.khs_pipeline import run_khs_pipeline
from pipelines.absen_pipeline import run_absen_pipeline
from pipelines.pembayaran_pipeline import run_pembayaran_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

# =========================
# HELPER (ANTI ERROR)
# =========================
def safe_data(res):
    if isinstance(res, dict):
        return res.get("data", [])
    return res or []


# =========================
# SYNC ALL DATA
# =========================
@router.post("/sync")
def sync_data(user_id: str = Depends(get_current_user)):
    driver = init_browser()

    try:
        user_uuid = uuid.UUID(str(user_id))

        # 🔐 LOGIN
        # Note: login(driver) currently uses input() which is not suitable for an API
        # but I will keep it for now as per user's logic, or ideally it should be automated.
        login(driver)

        # =====================
        # SCRAPING
        # =====================
        khs_response = fetch_khs(driver)
        absen_response = fetch_absen(driver)
        pembayaran_response = fetch_pembayaran(driver)

        # =====================
        # FIX STRUCTURE
        # =====================
        khs_data = safe_data(khs_response)
        absen_data = safe_data(absen_response)
        pembayaran_data = safe_data(pembayaran_response)

        # =====================
        # LOGGING
        # =====================
        logger.info(f"📊 KHS: {len(khs_data)}")
        logger.info(f"📊 ABSEN: {len(absen_data)}")
        logger.info(f"📊 PEMBAYARAN: {len(pembayaran_data)}")

        # =====================
        # PIPELINE
        # =====================
        run_khs_pipeline(user_id=user_uuid, khs_json=khs_data)
        run_absen_pipeline(user_id=user_uuid, absen_json=absen_data)
        run_pembayaran_pipeline(user_id=user_uuid, pembayaran_json=pembayaran_data)

        return {
            "status": "success",
            "message": "Sync berhasil",
            "user_id": str(user_uuid),
            "khs_count": len(khs_data),
            "absen_count": len(absen_data),
            "pembayaran_count": len(pembayaran_data),
        }

    except Exception as e:
        logger.error(f"❌ Sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

    finally:
        driver.quit()
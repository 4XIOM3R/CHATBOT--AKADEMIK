from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import logging
from pydantic import BaseModel
from typing import Optional
from api.deps import get_current_user, get_db
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

class SyncRequest(BaseModel):
    npm: Optional[str] = None
    password: Optional[str] = None

# =========================
# FUNGSI PEMBANTU (ANTI ERROR)
# =========================
def safe_data(res):
    if isinstance(res, dict):
        return res.get("data", [])
    return res or []


# =========================
# SINKRONISASI SEMUA DATA
# =========================
@router.post("/sync")
def sync_data(data: Optional[SyncRequest] = None, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    driver = init_browser()

    try:
        user_uuid = uuid.UUID(str(user_id))
        
        # Ambil kredensial jika ada
        npm = data.npm if data else None
        pw = data.password if data else None

        # MASUK (Manual via browser)
        success = login(driver, username=npm, password=pw)
        if not success:
            raise HTTPException(status_code=401, detail="Login SIA gagal atau timeout")

        # =====================
        # PENGAMBILAN DATA (SCRAPING)
        # =====================
        khs_response = fetch_khs(driver)
        absen_response = fetch_absen(driver)
        pembayaran_response = fetch_pembayaran(driver)

        # =====================
        # PERBAIKAN STRUKTUR
        # =====================
        khs_data = safe_data(khs_response)
        pembayaran_data = safe_data(pembayaran_response)
        
        # absen_response sekarang berupa dict dengan 'data' dan 'semester_info'
        absen_data = safe_data(absen_response)

        # =====================
        # PENCATATAN (LOGGING)
        # =====================
        logger.info(f"KHS: {len(khs_data)}")
        logger.info(f"ABSEN: {len(absen_data)}")
        logger.info(f"PEMBAYARAN: {len(pembayaran_data)}")
        
        if isinstance(absen_response, dict) and absen_response.get("semester_info"):
            logger.info(f"Semester Info (dari SIA): {absen_response['semester_info']}")

        # =====================
        # ALUR DATA (PIPELINE)
        # =====================
        # KHS pipeline harus dijalankan PERTAMA karena menghitung current_semester
        run_khs_pipeline(db=db, user_id=user_uuid, khs_json=khs_data)
        
        # Absen pipeline menggunakan current_semester dari User (yang sudah di-update oleh KHS pipeline)
        run_absen_pipeline(db=db, user_id=user_uuid, absen_json=absen_response)
        
        run_pembayaran_pipeline(db=db, user_id=user_uuid, pembayaran_json=pembayaran_data)

        db.commit()

        return {
            "status": "success",
            "message": "Sync berhasil",
            "user_id": str(user_uuid),
            "khs_count": len(khs_data),
            "absen_count": len(absen_data),
            "pembayaran_count": len(pembayaran_data),
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

    finally:
        driver.quit()

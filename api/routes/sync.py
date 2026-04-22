from fastapi import APIRouter, Depends
import uuid

from api.deps import get_current_user

from services.browser import init_browser
from services.auth import login

from endpoints.khs import fetch_khs
from endpoints.absen import fetch_absen
from endpoints.pembayaran import fetch_pembayaran

from pipelines.khs_pipeline import run_khs_pipeline
from services.sync_kartu_ujian import sync_kartu_ujian

from pipelines.absen_pipeline import run_absen_pipeline
from pipelines.pembayaran_pipeline import run_pembayaran_pipeline

router = APIRouter()


@router.post("/sync")
def sync_data(user=Depends(get_current_user)):
    driver = init_browser()

    try:
        # 🔥 convert ke UUID SEKALI
        user_uuid = uuid.UUID(str(user))

        # 🔐 login (captcha manual)
        login(driver)

        # =====================
        # SCRAPING
        # =====================
        khs_data = fetch_khs(driver)
        absen_data = fetch_absen(driver)
        pembayaran_data = fetch_pembayaran(driver)

        # =====================
        # PIPELINE / DB
        # =====================
        run_khs_pipeline(
            user_id=user_uuid,
            khs_json=khs_data
        )

        run_absen_pipeline(
            user_id=user_uuid,
            absen_json=absen_data
        )

        run_pembayaran_pipeline(
            user_id=user_uuid,
            pembayaran_json=pembayaran_data["data"]
        )

        return {
            "message": "Sync berhasil",
            "user_id": str(user_uuid),
            "khs_count": len(khs_data),
            "absen_count": len(absen_data),
            "pembayaran_count": len(pembayaran_data["data"]),
        }

    finally:
        driver.quit()


@router.post("/sync-kartu-ujian")
def sync_kartu(user=Depends(get_current_user)):
    driver = init_browser()

    try:
        # 🔥 convert ke UUID juga
        user_uuid = uuid.UUID(str(user))

        # 🔐 login
        login(driver)

        file_path = sync_kartu_ujian(driver, str(user_uuid))

        return {
            "message": "Kartu ujian berhasil di-download",
            "file": file_path
        }

    finally:
        driver.quit()
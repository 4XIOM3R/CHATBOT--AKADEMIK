import os

from endpoints.kartu_ujian import fetch_kartu_ujian_url
from services.downloader import download_kartu_ujian_file


def sync_kartu_ujian(driver, user_id: str) -> str:
    pdf_url = fetch_kartu_ujian_url(driver)

    os.makedirs("data", exist_ok=True)
    file_path = f"data/kartu_ujian_{user_id}.pdf"

    download_kartu_ujian_file(driver, pdf_url, file_path)

    return file_path
import requests


def download_kartu_ujian_file(driver, pdf_url: str, save_path: str) -> str:
    session = requests.Session()

    # 🔐 Ambil cookies dari Selenium (biar tetap login)
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://sia.uty.ac.id/std/kartuujian"
    }

    response = session.get(pdf_url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Gagal download PDF: {response.status_code}")

    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower():
        raise Exception("Response bukan file PDF")

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BASE_URL


def fetch_kartu_ujian_url(driver) -> str:
    driver.get(f"{BASE_URL}/std/kartuujian")

    wait = WebDriverWait(driver, 20)

    link = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href,'kartuujian/') and contains(@class,'btn')]")
        )
    )

    pdf_url = link.get_attribute("href")

    if not pdf_url:
        raise Exception("URL kartu ujian tidak ditemukan")

    return pdf_url
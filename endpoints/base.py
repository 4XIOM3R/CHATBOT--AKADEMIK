from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BASE_URL


def get_table_rows(driver, endpoint: str):
    driver.get(f"{BASE_URL}{endpoint}")

    wait = WebDriverWait(driver, 20)

    try:
        # tunggu sampai minimal 1 row muncul
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table//tbody//tr"))
        )

        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if not rows:
            raise Exception(f"Tabel kosong di {endpoint}")

        return rows

    except Exception as e:
        raise Exception(f"Gagal ambil tabel dari {endpoint}: {str(e)}")
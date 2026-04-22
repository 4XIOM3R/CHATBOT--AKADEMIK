from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BASE_URL
from utils.parser_khs import parse_khs

def fetch_khs(driver):
    driver.get(f"{BASE_URL}/std/khs")

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))

    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    data, total_sks, ipk = parse_khs(rows)

    return {
        "ipk": ipk,
        "total_sks": total_sks,
        "data": data
    }
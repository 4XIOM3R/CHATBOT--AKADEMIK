import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL, NPM, PASSWORD_SIA

logger = logging.getLogger(__name__)

def login(driver, username=None, password=None):
    driver.get(f"{BASE_URL}/login")
    
    logger.info("👉 Silakan login secara manual di browser (isi CAPTCHA jika ada)...")
    
    try:
        # Tunggu sampai URL berubah dari /login dan mengarah ke domain SIA
        # Timeout 5 menit (300 detik) untuk memberi waktu user login
        WebDriverWait(driver, 300).until(
            lambda d: "/login" not in d.current_url and "sia.uty.ac.id" in d.current_url
        )
        
        logger.info("✅ Login terdeteksi! Melanjutkan sinkronisasi...")
        return True
    except Exception as e:
        logger.error(f" Login timeout atau gagal: {str(e)}")
        return False
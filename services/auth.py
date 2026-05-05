import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from config import BASE_URL, NPM, PASSWORD_SIA
from services.alert_handler import dismiss_all_alerts

logger = logging.getLogger(__name__)

def inject_alert_handler(driver):
    """Inject JavaScript untuk auto-dismiss alerts"""
    try:
        logger.info("[ALERT] Injecting JavaScript alert handler...")
        js_code = """
        window.alert = function(msg) {
            console.log("ALERT DISMISSED: " + msg);
        };
        window.confirm = function(msg) {
            console.log("CONFIRM DISMISSED: " + msg);
            return true;
        };
        """
        driver.execute_script(js_code)
        logger.info("[ALERT] JavaScript handler injected successfully")
        return True
    except Exception as e:
        logger.warning(f"[ALERT] Failed to inject JS handler: {str(e)}")
        return False


def login(driver, username=None, password=None):
    driver.get(f"{BASE_URL}/login")

    logger.info("[LOGIN] Silakan login secara manual di browser (isi CAPTCHA jika ada)...")

    # Masukkan penangan peringatan
    time.sleep(1)
    inject_alert_handler(driver)

    try:
        start_time = time.time()
        timeout = 300  # 5 menit
        last_alert_dismiss = time.time()

        while time.time() - start_time < timeout:
            # Tutup peringatan setiap 2 detik
            if time.time() - last_alert_dismiss > 2:
                try:
                    dismiss_all_alerts(driver, timeout=1)
                except:
                    pass
                last_alert_dismiss = time.time()

            # Periksa jika sudah login
            try:
                current_url = driver.current_url
                if "/login" not in current_url and "sia.uty.ac.id" in current_url:
                    logger.info("[LOGIN] Login berhasil!")
                    # Tutup peringatan terakhir
                    time.sleep(1)
                    try:
                        dismiss_all_alerts(driver, timeout=1)
                    except:
                        pass
                    return True
            except Exception as e:
                logger.debug(f"[LOGIN] Check URL error: {str(e)}")

            time.sleep(0.5)

        raise Exception("Login timeout (5 menit)")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[LOGIN] Error: {error_msg}")

        # Coba sekali lagi untuk menutup semua peringatan
        try:
            dismiss_all_alerts(driver, timeout=2)
        except:
            pass

        return False

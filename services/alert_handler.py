"""
Alert handler untuk Selenium WebDriver
Digunakan untuk dismiss alerts yang muncul saat scraping SIA
"""

import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
import time

logger = logging.getLogger(__name__)


def dismiss_all_alerts(driver, timeout=5):
    """
    Dismiss semua alerts yang muncul
    Gunakan dalam loop untuk handle multiple alerts
    """
    dismissed_count = 0

    for _ in range(10):  # Max 10 alerts
        try:
            alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
            alert_text = alert.text
            logger.warning(f"[ALERT DISMISSED] {alert_text}")
            alert.accept()
            dismissed_count += 1
            time.sleep(0.5)
        except TimeoutException:
            break
        except Exception as e:
            logger.debug(f"[ALERT] Exception: {str(e)}")
            break

    if dismissed_count > 0:
        logger.info(f"[ALERT] Total alerts dismissed: {dismissed_count}")

    return dismissed_count


def dismiss_alert_if_present(driver, timeout=2):
    """Dismiss alert jika ada, return True jika ada alert"""
    try:
        alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
        logger.warning(f"[ALERT] {alert.text}")
        alert.accept()
        logger.info("[ALERT] Alert dismissed")
        return True
    except:
        return False


def try_action_with_alert_handling(driver, action_func, max_attempts=3):
    """
    Jalankan action dengan automatic alert handling
    Jika alert muncul, dismiss dan retry

    action_func: function yang ingin dijalankan
    """
    for attempt in range(max_attempts):
        try:
            logger.info(f"[ACTION] Attempt {attempt + 1}/{max_attempts}")
            return action_func()
        except Exception as e:
            error_msg = str(e)

            # Check apakah error berkaitan dengan alert
            if "alert" in error_msg.lower() or "unexpected" in error_msg.lower():
                logger.warning(f"[ACTION] Alert detected: {error_msg}")
                dismiss_all_alerts(driver)
                time.sleep(1)
            else:
                raise

    raise Exception(f"Action failed after {max_attempts} attempts")

from selenium import webdriver
import os
import shutil
import logging
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

def init_browser(headless=False):
    """
    Initialize Chrome WebDriver dengan optimasi untuk stability

    Args:
        headless: True untuk headless mode (no UI), False untuk visible browser
    """
    options = Options()

    # Direktori unduhan portabel
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    download_dir = os.path.join(base_dir, "data", "downloads")

    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }

    options.add_experimental_option("prefs", prefs)

    # Path profil Chrome
    profile_path = os.path.join(base_dir, "db", "chrome_profile")

    # Nonaktifkan kotak dialog
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Optimasi memori dan proses
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    # Peningkatan stabilitas
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions-except")
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless")
        logger.info("[BROWSER] Running in headless mode")
    else:
        logger.info("[BROWSER] Running with visible UI")

    # Gunakan profil jika ada dan tidak rusak, jika tidak mulai dari awal
    if os.path.exists(profile_path):
        try:
            options.add_argument(f"--user-data-dir={profile_path}")
            logger.info(f"[BROWSER] Using existing Chrome profile: {profile_path}")
        except Exception as e:
            logger.warning(f"[BROWSER] Chrome profile corrupted, creating fresh: {e}")
            if os.path.exists(profile_path):
                shutil.rmtree(profile_path, ignore_errors=True)
    else:
        logger.info("[BROWSER] Creating new Chrome profile")

    try:
        logger.info("[BROWSER] Initializing Chrome WebDriver...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        logger.info("[BROWSER] Chrome WebDriver initialized successfully")

        # Atur perilaku alert melalui CDP
        try:
            logger.info("[BROWSER] Configuring alert handling...")
            driver.execute_cdp_cmd('Page.handleJavaScriptDialog', {
                'accept': True,
                'promptText': ''
            })
        except:
            pass

        return driver

    except Exception as e:
        logger.error(f"[BROWSER] Failed to initialize Chrome: {str(e)}")
        logger.info("[BROWSER] Attempting with headless mode...")

        # Cadangan: coba mode headless
        if not headless:
            options.add_argument("--headless")
            try:
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
                logger.info("[BROWSER] Chrome initialized in headless mode")
                return driver
            except Exception as e2:
                logger.error(f"[BROWSER] Headless mode also failed: {str(e2)}")
                raise Exception(f"Chrome initialization failed: {str(e)}")
        else:
            raise
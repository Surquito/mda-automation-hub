from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config.settings import DOWNLOAD_PATH
from src.logger import logger


def get_driver():

    logger.info("🚀 Inicializando Chrome")

    driver_path = Path("drivers/chromedriver.exe")

    if not driver_path.exists():

        raise FileNotFoundError(
            f"No existe el driver: {driver_path}"
        )

    logger.info(f"📁 Driver encontrado: {driver_path}")
    logger.info(f"📥 Ruta descarga: {DOWNLOAD_PATH}")

    service = Service(str(driver_path))

    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    prefs = {
        "download.default_directory": str(Path(DOWNLOAD_PATH).resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }

    options.add_experimental_option(
        "prefs",
        prefs
    )

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    driver.maximize_window()

    logger.info("✅ Chrome iniciado")

    return driver
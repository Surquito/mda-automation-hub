from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import (
    JIRA_URL,
    JIRA_USER,
    JIRA_PASSWORD
)

from src.browser import get_driver
from src.logger import logger

import time



class JiraLogin:

    def start_session(self):

        try:

            logger.info("🌐 Abriendo Jira")

            driver = get_driver()

            driver.get(JIRA_URL)

            wait = WebDriverWait(driver, 20)

            logger.info("🔍 Buscando campo usuario")

            txt_usuario = wait.until(
                EC.presence_of_element_located(
                    (By.ID, "login-form-username")
                )
            )

            txt_usuario.clear()
            txt_usuario.send_keys(JIRA_USER)

            logger.info(
                f"Valor capturado en pantalla: "
                f"{txt_usuario.get_attribute('value')}"
            )

            logger.info(f"Usuario: {JIRA_USER}")
            logger.info(f"Password length: {len(JIRA_PASSWORD)}")

            logger.info(
                f"Usuario escrito: "
                f"{txt_usuario.get_attribute('value')}"
            )

            logger.info("✅ Usuario ingresado")

            logger.info("🔍 Buscando campo contraseña")

            txt_password = wait.until(
                EC.presence_of_element_located(
                    (By.ID, "login-form-password")
                )
            )

            txt_password.clear()
            txt_password.send_keys(JIRA_PASSWORD)

            logger.info(
                f"Password length: "
                f"{len(txt_password.get_attribute('value'))}"
            )

            logger.info("✅ Contraseña ingresada")

            logger.info("🔍 Buscando botón Iniciar Sesión")

            btn_login = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "login")
                )
            )

            btn_login.click()

            logger.info("✅ Botón login presionado")

            time.sleep(5)
            
            logger.info(
                f"URL actual: {driver.current_url}"
            )

            return driver

        except Exception as e:

            logger.error(
                f"❌ Error durante login: {e}"
            )

            raise
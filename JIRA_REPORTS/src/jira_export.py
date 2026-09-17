import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import (
    JIRA_FILTER_URL,
    DOWNLOAD_PATH
)

from src.logger import logger


class JiraExport:

    def __init__(self, driver):

        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def download_csv(self):

        try:
            self.clean_old_downloads()

            logger.info("📄 Accediendo al filtro Jira")

            self.driver.get(JIRA_FILTER_URL)

            logger.info("✅ Filtro cargado")

            logger.info("📤 Buscando botón Exportar")

            btn_exportar = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(.,'Exportar')]"
                    )
                )
            )

            btn_exportar.click()

            logger.info("✅ Menú Exportar abierto")

            errores = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div.aui-message-error"
            )

            if errores:

                mensaje = errores[0].text

                logger.warning(
                    f"⚠️ Error Jira: {mensaje}"
                )

                return None

            logger.info("⬇️ Buscando opción CSV (Todos los campos)")

            opcion_csv = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "allCsvFields"
                    )
                )
            )

            opcion_csv.click()

            logger.info("✅ Opción CSV seleccionada")

            logger.info("📋 Esperando ventana de exportación")

            btn_confirmar = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "csv-export-dialog-export-button"
                    )
                )
            )

            logger.info("✅ Ventana encontrada")

            btn_confirmar.click()

            logger.info(
                f"URL después de exportar: {self.driver.current_url}"
            )

            logger.info(
                f"Título página: {self.driver.title}"
            )

            logger.info("⬇️ Descarga iniciada")

            archivo = self.wait_download()

            logger.info(
                f"✅ Descarga completada: {archivo}"
            )

            return archivo

        except Exception as e:

            logger.error(
                f"❌ Error durante la exportación: {str(e)}"
            )

            raise

    def clean_old_downloads(self):

        logger.info(
            "🧹 Limpiando descargas incompletas"
        )

        for archivo in os.listdir(DOWNLOAD_PATH):

            if archivo.endswith(".crdownload"):

                ruta = os.path.join(
                    DOWNLOAD_PATH,
                    archivo
                )

                try:

                    os.remove(ruta)

                    logger.info(
                        f"🗑️ Eliminado: {archivo}"
                    )

                except Exception as e:

                    logger.error(
                        f"No se pudo eliminar {archivo}: {e}"
                    )

    def wait_download(self):

        logger.info("⏳ Esperando descarga")

        timeout = 900

        inicio = time.time()

        while True:

            # Ver archivos actuales
            archivos = os.listdir(DOWNLOAD_PATH)

            logger.info(
                f"Archivos: {archivos}"
            )

            # NUEVO BLOQUE
            crdownload = [
                f for f in archivos
                if f.endswith(".crdownload")
            ]

            if crdownload:

                logger.info(
                    f"⏳ Descarga aún en progreso: {crdownload}"
                )

            # Buscar CSV terminados
            csv_files = [
                os.path.join(DOWNLOAD_PATH, f)
                for f in archivos
                if f.endswith(".csv")
            ]

            if csv_files:

                archivo = max(
                    csv_files,
                    key=os.path.getmtime
                )

                edad = (
                    time.time()
                    - os.path.getmtime(archivo)
                )

                if edad < 30:

                    logger.info(
                        f"✅ Archivo encontrado: {archivo}"
                    )

                    return archivo

            if time.time() - inicio > timeout:

                raise TimeoutError(
                    "Tiempo máximo de espera excedido para la descarga."
                )

            time.sleep(2)
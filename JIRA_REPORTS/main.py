import time

from src.jira_login import JiraLogin
from src.jira_export import JiraExport
from src.database import Database
from src.logger import logger

#from src.powerbi_refresh import PowerBIRefresh



def ejecutar_proceso():

    driver = None

    try:

        login = JiraLogin()

        driver = login.start_session()

        exporter = JiraExport(driver)

        csv_file = exporter.download_csv()

        # No se generó archivo
        if not csv_file:

            logger.warning(
                "⚠️ No hay tickets para procesar"
            )

            return

        logger.info(
            f"CSV descargado: {csv_file}"
        )

        db = Database()

        db.load_csv(csv_file)

        #refresh = PowerBIRefresh(       
        #    driver       
        #)

        #refresh.refresh_dataset()

        logger.info(
            "✅ Proceso finalizado correctamente"
        )

    except Exception as e:

        logger.error(
            f"❌ Error general: {e}"
        )

    finally:

        if driver:

            driver.quit()

            logger.info(
                "🔒 Navegador cerrado"
            )


def main():

    while True:

        logger.info(
            "🚀 Iniciando ejecución programada"
        )

        ejecutar_proceso()

        logger.info(
            "⏳ Esperando 3600 segundos para la siguiente ejecución"
        )

        time.sleep(3600)


if __name__ == "__main__":
    main()
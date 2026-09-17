import traceback

from config.settings import MAIL_SUBJECT, MAIL_TO, MAIL_TO_CC
from src.kpi_service import KPIService
from src.logger import logger
from src.mailer import Mailer
from src.powerbi import PowerBI


def main():
    powerbi = None
    try:
        logger.info("🚀 Iniciando proceso")
        powerbi = PowerBI()

        imagenes_tendencias = powerbi.capturar_tendencias()
        logger.info("🖼️ Tendencias generadas: %s", imagenes_tendencias)

        pdf_file = powerbi.export_pdf()
        logger.info("📎 Archivo generado: %s", pdf_file)

        kpis = KPIService().get_resumen()

        Mailer().send_mail(
            destinatarios=MAIL_TO,
            cc=MAIL_TO_CC,
            bcc="",
            asunto=MAIL_SUBJECT,
            adjunto=pdf_file,
            imagenes_tendencias=imagenes_tendencias,
            kpis=kpis,
        )
        logger.info("✅ Proceso completado")
    except Exception as error:
        logger.error("❌ Error: %s", error)
        logger.error(traceback.format_exc())
    finally:
        if powerbi:
            try:
                powerbi.close()
            except Exception as error:
                logger.warning("⚠️ No se pudo cerrar Chrome: %s", error)
            logger.info("🔒 Navegador cerrado")


if __name__ == "__main__":
    main()

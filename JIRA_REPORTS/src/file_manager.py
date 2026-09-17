import os
from pathlib import Path

from config.settings import DOWNLOAD_PATH
from src.logger import logger


class FileManager:

    def get_last_csv(self):

        archivos = list(
            Path(DOWNLOAD_PATH).glob("*.csv")
        )

        if not archivos:

            raise FileNotFoundError(
                "No se encontró ningún CSV"
            )

        ultimo = max(
            archivos,
            key=os.path.getmtime
        )

        logger.info(
            f"📄 Archivo encontrado: {ultimo}"
        )

        return str(ultimo)
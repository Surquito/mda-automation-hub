import logging
import os

os.makedirs(
    "logs",
    exist_ok=True
)

logger = logging.getLogger(
    "powerbi"
)

logger.setLevel(
    logging.INFO
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

file_handler = logging.FileHandler(
    "logs/powerbi.log",
    encoding="utf-8"
)

file_handler.setFormatter(
    formatter
)

logger.addHandler(
    file_handler
)

logger.addHandler(
    logging.StreamHandler()
)
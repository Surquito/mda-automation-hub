import schedule
import time

from main import main

from src.logger import logger


def ejecutar():

    logger.info(
        "⏰ Hora programada alcanzada"
    )

    main()


schedule.every().day.at(
    "08:30"
).do(
    ejecutar
)

schedule.every().day.at(
    "13:30"
).do(
    ejecutar
)

schedule.every().day.at(
    "20:30"
).do(
    ejecutar
)

logger.info(
    "✅ Scheduler iniciado"
)

while True:

    schedule.run_pending()

    logger.info(
        f"⏳ Esperando siguiente corte... {time.strftime('%H:%M:%S')}"
    )

    time.sleep(3600)
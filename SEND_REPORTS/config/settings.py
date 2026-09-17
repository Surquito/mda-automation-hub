import os

from dotenv import load_dotenv


load_dotenv()


POWERBI_URL = os.getenv(
    "POWERBI_URL"
)

POWERBI_URL_TENDENCIA_1 = os.getenv(
    "POWERBI_URL_TENDENCIA_1"
)

POWERBI_URL_TENDENCIA_2 = os.getenv(
    "POWERBI_URL_TENDENCIA_2"
)

POWERBI_URL_TENDENCIA_3 = os.getenv(
    "POWERBI_URL_TENDENCIA_3"
)

POWERBI_URL_TENDENCIA_4 = os.getenv(
    "POWERBI_URL_TENDENCIA_4"
)

REPORT_PATH = os.getenv(
    "REPORT_PATH"
)

REPORT_PATH_TENDENCIAS = os.getenv(
    "REPORT_PATH_TENDENCIAS"
)

MAIL_TO = os.getenv(
    "MAIL_TO",
    ""
).strip()

MAIL_TO_CC = os.getenv(
    "MAIL_TO_CC",
    ""
).strip()

MAIL_SUBJECT = os.getenv(
    "MAIL_SUBJECT",
    "Dashboard MDA Diario"
).strip()


VARIABLES_OBLIGATORIAS = {
    "POWERBI_URL": POWERBI_URL,
    "POWERBI_URL_TENDENCIA_1": POWERBI_URL_TENDENCIA_1,
    "POWERBI_URL_TENDENCIA_2": POWERBI_URL_TENDENCIA_2,
    "POWERBI_URL_TENDENCIA_3": POWERBI_URL_TENDENCIA_3,
    "POWERBI_URL_TENDENCIA_4": POWERBI_URL_TENDENCIA_4,
    "REPORT_PATH": REPORT_PATH,
    "REPORT_PATH_TENDENCIAS": REPORT_PATH_TENDENCIAS,
}


for nombre, valor in VARIABLES_OBLIGATORIAS.items():

    if not valor:

        raise ValueError(
            f"No se configuró {nombre} en el archivo .env"
        )


os.makedirs(
    REPORT_PATH,
    exist_ok=True
)

os.makedirs(
    REPORT_PATH_TENDENCIAS,
    exist_ok=True
)
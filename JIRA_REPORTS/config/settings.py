import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

env_file = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_file)

# Jira
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")


print("JIRA_URL:", repr(JIRA_URL))
print("JIRA_USER:", repr(JIRA_USER))
print("JIRA_PASSWORD:", "*" * len(JIRA_PASSWORD))
print("DOWNLOAD_PATH =", repr(DOWNLOAD_PATH))


LOG_PATH = str(BASE_DIR / "logs")

# Tiempo de espera Selenium
TIMEOUT = 20

# URL del filtro Jira

JIRA_FILTER_URL = (

#    "https://jira.dpworld.pe/issues/?"
#    "jql=project%20%3D%20MDA%20AND%20created%20%3E%3D%202026-09-16%20AND%20created%20%3C%3D%202026-09-18"

#    dejar despues de parchar
    "https://jira.dpworld.pe/issues/"
    "?jql=project%20%3D%20MDA%20AND%20updated%20%3E%3D%20-1h"
)


print("=" * 50)
print("JIRA_URL =", repr(JIRA_URL))
print("JIRA_USER =", repr(JIRA_USER))
print("JIRA_PASSWORD =", repr(JIRA_PASSWORD))
print("=" * 50)

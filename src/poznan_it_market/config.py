import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
JJIT_API_URL = os.environ.get("JJIT_API_URL", "https://justjoin.it/api/candidate-api/offers")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DEMO_DATABASE_URL = os.environ.get("DEMO_DATABASE_URL")

DEMO_DATE = date(2026, 8, 11)
DEMO_SAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "data/raw/sample" / f"jjit_{DEMO_DATE.isoformat()}.json"
)


def require_database_url(url: str | None) -> str:
    if not url or not url.strip():
        raise ValueError("DATABASE_URL is required for database access.")
    return url

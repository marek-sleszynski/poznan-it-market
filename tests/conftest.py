import json
import os
from pathlib import Path

import pytest

from poznan_it_market.ingest.loader import get_connection

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")


@pytest.fixture
def sample_offers():
    SAMPLE_PATH = Path(__file__).parent.parent / "data/raw/sample/jjit_2026-08-11.json"
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture
def db_conn():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw.offers, raw.ingestion_runs CASCADE;")
        conn.commit()
        yield conn
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw.offers, raw.ingestion_runs CASCADE;")
        conn.commit()

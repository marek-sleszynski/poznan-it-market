import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "")


@pytest.fixture
def sample_offers():
    SAMPLE_PATH = Path(__file__).parent.parent / "data/raw/sample/jjit_2026-08-11.json"
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture
def db_conn(monkeypatch):
    test_url = os.environ.get("TEST_DATABASE_URL")
    if not test_url:
        pytest.fail("TEST_DATABASE_URL must be set for database tests.")

    from poznan_it_market import pipeline
    from poznan_it_market.ingest import loader

    monkeypatch.setattr(loader, "DATABASE_URL", test_url)
    monkeypatch.setattr(pipeline, "DATABASE_URL", test_url)
    monkeypatch.setattr(pipeline, "DEMO_DATABASE_URL", test_url)

    with loader.get_connection() as conn:
        if conn.info.dbname != "poznan_it_market_test":
            pytest.fail("Database tests require poznan_it_market_test.")

        conn.execute("TRUNCATE TABLE raw.offers, raw.ingestion_runs, raw.rejected_records CASCADE;")
        conn.commit()
        try:
            yield conn
        finally:
            conn.rollback()
            conn.execute("TRUNCATE TABLE raw.offers, raw.ingestion_runs CASCADE;")
            conn.commit()

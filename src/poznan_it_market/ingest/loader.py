import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from poznan_it_market.config import DATABASE_URL

INSERT_OFFERS_QUERY = """
INSERT INTO raw.offers (source, source_offer_id, payload, fetched_at, run_id)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (source, source_offer_id, (raw.to_date_utc(fetched_at))) DO NOTHING;
"""

START_RUN_QUERY = """
INSERT INTO raw.ingestion_runs (run_id, started_at, status)
VALUES (%s, %s, 'running');
"""

FINISH_RUN_QUERY = """
UPDATE raw.ingestion_runs
SET finished_at = %s, status = %s, pages_fetched = %s, records_accepted = %s, records_rejected = %s
WHERE run_id = %s;
"""


def get_connection(db_uri: str | None = None) -> psycopg.Connection:
    return psycopg.connect(db_uri or DATABASE_URL)


def load_raw_offers(
    conn: psycopg.Connection,
    offers: list[dict],
    source: str,
    run_id: uuid.UUID,
    fetched_at: datetime,
) -> int:
    records = [
        (source, str(o.get("slug") or o.get("id")), Jsonb(o), fetched_at, run_id) for o in offers
    ]
    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(INSERT_OFFERS_QUERY, records)
            return cur.rowcount


def log_run_start(conn: psycopg.Connection, run_id: uuid.UUID, started_at: datetime) -> None:
    with conn.transaction():
        conn.execute(START_RUN_QUERY, (run_id, started_at))


def log_run_finish(
    conn: psycopg.Connection, run_id: uuid.UUID, finished_at: datetime, status: str, count: int = 0
) -> None:
    with conn.transaction():
        conn.execute(FINISH_RUN_QUERY, (finished_at, status, 1, count, 0, run_id))


def run_pipeline() -> None:
    run_id = uuid.uuid4()
    now = datetime.now(UTC)

    sample_file = Path("data/raw/sample/jjit_2026-08-11.json")
    with open(sample_file, encoding="utf-8") as f:
        data = json.load(f)
        offers = data if isinstance(data, list) else data.get("data", [])

    with get_connection() as conn:
        log_run_start(conn, run_id, now)
        try:
            loaded_count = load_raw_offers(conn, offers, "justjoin.it", run_id, now)
            log_run_finish(conn, run_id, datetime.now(UTC), "success", loaded_count)
            print(f"SUKCES: Załadowano {loaded_count} ofert! Run ID: {run_id}")
        except Exception as e:
            log_run_finish(conn, run_id, datetime.now(UTC), "failed", 0)
            print(f"BŁĄD: {e}")
            raise


if __name__ == "__main__":
    run_pipeline()

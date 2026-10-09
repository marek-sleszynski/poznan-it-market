import uuid
from datetime import UTC, datetime

import psycopg
from psycopg.types.json import Jsonb

from poznan_it_market.config import DATABASE_URL, require_database_url

INSERT_OFFERS_QUERY = """
INSERT INTO raw.offers
    (source, source_offer_id, payload, fetched_at, run_id, data_mode)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (source, source_offer_id, (raw.to_date_utc(fetched_at)))
DO UPDATE SET
    payload = EXCLUDED.payload,
    fetched_at = EXCLUDED.fetched_at,
    run_id = EXCLUDED.run_id,
    data_mode = EXCLUDED.data_mode;
"""

START_RUN_QUERY = """
INSERT INTO raw.ingestion_runs
    (run_id, started_at, status, data_mode, observed_date)
VALUES (%s, %s, 'running', %s, %s);
"""

FINISH_RUN_QUERY = """
UPDATE raw.ingestion_runs
SET finished_at = %s,
    status = %s,
    pages_fetched = %s,
    records_accepted = %s,
    records_rejected = %s,
    stage = %s,
    error_type = %s,
    error_message = %s
WHERE run_id = %s;
"""


def get_connection(db_uri: str | None = None) -> psycopg.Connection:
    database_url = DATABASE_URL if db_uri is None else db_uri
    return psycopg.connect(require_database_url(database_url))


def load_raw_offers(
    conn: psycopg.Connection,
    offers: list[dict],
    source: str,
    run_id: uuid.UUID,
    fetched_at: datetime,
    data_mode: str = "unknown",
) -> int:
    records = [(source, o["slug"], Jsonb(o), fetched_at, run_id, data_mode) for o in offers]
    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(INSERT_OFFERS_QUERY, records)
            return cur.rowcount


def log_run_start(
    conn: psycopg.Connection,
    run_id: uuid.UUID,
    started_at: datetime,
    mode: str,
    observed_at: datetime,
) -> None:
    with conn.transaction():
        conn.execute(
            START_RUN_QUERY,
            (run_id, started_at, mode, observed_at.astimezone(UTC).date()),
        )


def log_run_finish(
    conn: psycopg.Connection,
    run_id: uuid.UUID,
    finished_at: datetime,
    status: str,
    count: int = 0,
    rejected_count: int = 0,
    pages_fetched: int | None = None,
    stage: str | None = None,
    error: Exception | None = None,
) -> None:
    with conn.transaction():
        conn.execute(
            FINISH_RUN_QUERY,
            (
                finished_at,
                status,
                pages_fetched,
                count,
                rejected_count,
                stage,
                type(error).__name__ if error is not None else None,
                str(error) if error is not None else None,
                run_id,
            ),
        )


def load_rejected_offers(
    conn: psycopg.Connection,
    rejected: list[tuple[dict, str]],
    run_id: uuid.UUID,
) -> int:
    if not rejected:
        return 0

    records = [(Jsonb(offer), "validation_error", message, run_id) for offer, message in rejected]

    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO raw.rejected_records
                    (payload, error_type, error_message, run_id)
                VALUES (%s, %s, %s, %s);
                """,
                records,
            )
            return cur.rowcount


if __name__ == "__main__":
    raise SystemExit("Use: poznan-it-market --mode demo|live")

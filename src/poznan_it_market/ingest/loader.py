import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.types.json import Jsonb

from poznan_it_market.config import DATABASE_URL, DEMO_DATABASE_URL
from poznan_it_market.ingest.client import get_http_client
from poznan_it_market.ingest.justjoinit import fetch_justjoinit_pages
from poznan_it_market.ingest.validation import validate_offers

INSERT_OFFERS_QUERY = """
INSERT INTO raw.offers (source, source_offer_id, payload, fetched_at, run_id)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (source, source_offer_id, (raw.to_date_utc(fetched_at)))
DO UPDATE SET
    payload = EXCLUDED.payload,
    fetched_at = EXCLUDED.fetched_at,
    run_id = EXCLUDED.run_id;
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
    records = [(source, o["slug"], Jsonb(o), fetched_at, run_id) for o in offers]
    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(INSERT_OFFERS_QUERY, records)
            return cur.rowcount


def log_run_start(conn: psycopg.Connection, run_id: uuid.UUID, started_at: datetime) -> None:
    with conn.transaction():
        conn.execute(START_RUN_QUERY, (run_id, started_at))


def log_run_finish(
    conn: psycopg.Connection,
    run_id: uuid.UUID,
    finished_at: datetime,
    status: str,
    count: int = 0,
    rejected_count: int = 0,
) -> None:
    with conn.transaction():
        conn.execute(
            FINISH_RUN_QUERY,
            (finished_at, status, 1, count, rejected_count, run_id),
        )


def read_demo_offers(sample_file: Path) -> list[dict]:
    with sample_file.open(encoding="utf-8") as file:
        data = json.load(file)

    offers = data if isinstance(data, list) else data["data"]

    if not isinstance(offers, list):
        raise ValueError("Demo offers must be a list.")

    return offers


def read_live_offers() -> list[dict]:
    offers = []
    with get_http_client() as client:
        for page in fetch_justjoinit_pages(client):
            offers.extend(page["data"])
    return offers


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


def run_pipeline(mode: str = "demo") -> None:
    started_at = datetime.now(UTC)

    if mode == "demo":
        if not DEMO_DATABASE_URL:
            raise ValueError("DEMO_DATABASE_URL is required for demo import.")

        params = conninfo_to_dict(DEMO_DATABASE_URL)
        if params.get("host") not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("Demo import requires a local database.")
        if params.get("dbname") not in {
            "poznan_it_market_demo",
            "poznan_it_market_test",
        }:
            raise ValueError("Demo import requires a demo or test database.")

        database_url = DEMO_DATABASE_URL
        observed_at = datetime(2026, 8, 11, tzinfo=UTC)
        offers = read_demo_offers(Path("data/raw/sample/jjit_2026-08-11.json"))

    elif mode == "live":
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is required for live import.")

        database_url = DATABASE_URL
        observed_at = started_at
        offers = read_live_offers()

    else:
        raise ValueError("Mode must be demo or live.")

    run_id = uuid.uuid4()

    with get_connection(database_url) as conn:
        log_run_start(conn, run_id, started_at)
        try:
            accepted, rejected = validate_offers(offers)

            with conn.transaction():
                loaded_count = load_raw_offers(conn, accepted, "justjoin.it", run_id, observed_at)
                rejected_count = load_rejected_offers(conn, rejected, run_id)
                log_run_finish(
                    conn,
                    run_id,
                    datetime.now(UTC),
                    "success",
                    loaded_count,
                    rejected_count,
                )

            print(
                f"{mode.upper()}: Accepted {loaded_count}, "
                f"rejected {rejected_count}. Run ID: {run_id}"
            )
        except Exception:
            log_run_finish(conn, run_id, datetime.now(UTC), "failed", 0)
            raise


if __name__ == "__main__":
    raise SystemExit("Use: poznan-it-market --mode demo|live")

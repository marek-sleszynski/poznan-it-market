import argparse
import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

from psycopg.conninfo import conninfo_to_dict

from poznan_it_market.config import DATABASE_URL, DEMO_DATABASE_URL, LOG_LEVEL
from poznan_it_market.ingest import justjoinit, loader
from poznan_it_market.ingest.validation import validate_offers

logger = logging.getLogger(__name__)


def run_pipeline(mode: str = "demo") -> None:
    started_at = datetime.now(UTC)
    run_id = uuid.uuid4()

    database_url, observed_at = get_import_settings(mode, started_at)

    pages_fetched: int | None = None
    stage = "fetch"

    with loader.get_connection(database_url) as conn:
        loader.log_run_start(conn, run_id, started_at, mode, observed_at)
        try:
            logger.info("run_id=%s mode=%s stage=fetch", run_id, mode)
            if mode == "demo":
                offers = read_demo_offers(Path("data/raw/sample/jjit_2026-08-11.json"))
                pages_fetched = 1
            else:
                offers, pages_fetched = justjoinit.read_live_offers()

            stage = "validate"
            logger.info("run_id=%s stage=validate", run_id)
            accepted, rejected = validate_offers(offers)

            stage = "write"
            logger.info("run_id=%s stage=write", run_id)
            with conn.transaction():
                loaded_count = loader.load_raw_offers(
                    conn,
                    accepted,
                    "justjoin.it",
                    run_id,
                    observed_at,
                    data_mode=mode,
                )
                rejected_count = loader.load_rejected_offers(conn, rejected, run_id)
                loader.log_run_finish(
                    conn,
                    run_id,
                    datetime.now(UTC),
                    "success",
                    loaded_count,
                    rejected_count,
                    pages_fetched=pages_fetched,
                    stage="finished",
                )

            logger.info(
                "run_id=%s mode=%s accepted=%s rejected=%s pages=%s",
                run_id,
                mode,
                loaded_count,
                rejected_count,
                pages_fetched,
            )
        except Exception as error:
            logger.exception("run_id=%s stage=%s import failed", run_id, stage)
            try:
                loader.log_run_finish(
                    conn,
                    run_id,
                    datetime.now(UTC),
                    "failed",
                    pages_fetched=pages_fetched,
                    stage=stage,
                    error=error,
                )
            except Exception:
                logger.exception("run_id=%s failed status could not be saved", run_id)
            raise


def get_import_settings(mode: str, started_at: datetime) -> tuple[str, datetime]:
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
    elif mode == "live":
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is required for live import.")
        database_url = DATABASE_URL
        observed_at = started_at
    else:
        raise ValueError("Mode must be demo or live.")

    return database_url, observed_at


def read_demo_offers(sample_file: Path) -> list[dict]:
    with sample_file.open(encoding="utf-8") as file:
        data = json.load(file)

    offers = data if isinstance(data, list) else data["data"]

    if not isinstance(offers, list):
        raise ValueError("Demo offers must be a list.")

    return offers


def main() -> None:
    parser = argparse.ArgumentParser(description="Import job offers.")
    parser.add_argument(
        "--mode",
        choices=["demo", "live"],
        required=True,
        help="Choose the data source and target database.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=LOG_LEVEL.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    run_pipeline(mode=args.mode)


if __name__ == "__main__":
    main()

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict


def main():
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    test_url = os.environ["TEST_DATABASE_URL"]
    settings = conninfo_to_dict(test_url)
    if settings.get("dbname") != "poznan_it_market_test":
        raise ValueError("CI fixtures require poznan_it_market_test.")
    if settings.get("host") not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("CI fixtures require a local database.")

    os.environ["DATABASE_URL"] = test_url
    # The fixture uses local files and never requests the API.
    os.environ.setdefault("JJIT_API_URL", "")

    from poznan_it_market.ingest.loader import (
        get_connection,
        load_raw_offers,
        log_run_finish,
        log_run_start,
    )
    from poznan_it_market.ingest.validation import validate_offers

    fixture = json.loads(
        (project_root / "data/fixtures/ci_offers.json").read_text(encoding="utf-8")
    )
    batches = fixture["batches"]
    with get_connection(test_url) as conn:
        existing = conn.execute("""
            SELECT
                (SELECT count(*) FROM raw.offers)
                + (SELECT count(*) FROM raw.ingestion_runs)
                + (SELECT count(*) FROM raw.rejected_records);
        """).fetchone()[0]
        if existing:
            raise ValueError("Run the Python tests first to prepare an empty test database.")
        conn.commit()

        for batch in [*batches, batches[-1]]:
            observed_at = datetime.fromisoformat(batch["observed_at"])
            if observed_at.tzinfo is None or observed_at.utcoffset() is None:
                raise ValueError("Fixture observation timestamps must include a timezone.")
            accepted, rejected = validate_offers(batch["offers"])
            if rejected:
                raise ValueError("The CI fixture contains invalid offers.")

            run_id = uuid.uuid4()
            log_run_start(conn, run_id, datetime.now(UTC), "demo", observed_at)
            with conn.transaction():
                count = load_raw_offers(
                    conn,
                    accepted,
                    fixture["source"],
                    run_id,
                    observed_at,
                    data_mode="demo",
                )
                log_run_finish(
                    conn,
                    run_id,
                    datetime.now(UTC),
                    "success",
                    count,
                    pages_fetched=1,
                    stage="finished",
                )

        actual = conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0]
        if actual != 4:
            raise AssertionError(f"Expected 4 raw observations, got {actual}.")

    print("PASS: 4 synthetic observations; repeating the second day adds no duplicates.")


if __name__ == "__main__":
    main()

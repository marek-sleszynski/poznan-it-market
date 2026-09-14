import uuid
from datetime import UTC, datetime

import pytest

from poznan_it_market.ingest.loader import load_raw_offers, run_pipeline


def test_load_raw_offers_is_idempotent_on_same_day(db_conn, sample_offers):
    offers = sample_offers["data"][:5]
    now = datetime.now(UTC)

    load_raw_offers(db_conn, offers, "justjoin.it", uuid.uuid4(), now)
    load_raw_offers(db_conn, offers, "justjoin.it", uuid.uuid4(), now)

    assert db_conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0] == len(offers)


def test_pipeline_rollback_and_status_failed_on_error(db_conn, monkeypatch):
    def mock_failure(*args, **kwargs):
        raise RuntimeError("Simulated crash")

    monkeypatch.setattr("poznan_it_market.ingest.loader.load_raw_offers", mock_failure)

    with pytest.raises(RuntimeError):
        run_pipeline()

    assert db_conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0] == 0
    status = db_conn.execute("SELECT status FROM raw.ingestion_runs;").fetchone()[0]
    assert status == "failed"


def test_load_raw_offers_updates_payload_and_run_id_on_conflict(db_conn):
    now = datetime.now(UTC)
    offer_v1 = {"slug": "offer-1", "employmentTypes": [{"to": 15000}]}
    offer_v2 = {"slug": "offer-1", "employmentTypes": [{"to": 20000}]}

    load_raw_offers(db_conn, [offer_v1], "justjoin.it", uuid.uuid4(), now)
    run_id_2 = uuid.uuid4()
    load_raw_offers(db_conn, [offer_v2], "justjoin.it", run_id_2, now)

    assert db_conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0] == 1

    payload, db_run_id = db_conn.execute(
        "SELECT payload, run_id FROM raw.offers WHERE source_offer_id = 'offer-1';"
    ).fetchone()

    assert payload["employmentTypes"][0]["to"] == 20000
    assert db_run_id == run_id_2

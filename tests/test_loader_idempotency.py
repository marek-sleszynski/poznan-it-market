import uuid
from datetime import UTC, datetime

import pytest

from poznan_it_market import pipeline
from poznan_it_market.ingest import justjoinit, loader
from poznan_it_market.ingest.loader import load_raw_offers
from poznan_it_market.pipeline import run_pipeline


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


def test_demo_reads_sample_and_preserves_observation_date(db_conn, sample_offers, monkeypatch):
    sample_paths = []
    offer = sample_offers["data"][0]

    def fake_read_demo_offers(path):
        sample_paths.append(path)
        return [offer]

    monkeypatch.setattr(pipeline, "read_demo_offers", fake_read_demo_offers)

    pipeline.run_pipeline()

    assert sample_paths == [pipeline.config.DEMO_SAMPLE_PATH]

    rows = db_conn.execute("SELECT payload, fetched_at FROM raw.offers;").fetchall()

    assert len(rows) == 1
    assert rows[0][0] == offer
    assert rows[0][1] == datetime(2026, 8, 11, tzinfo=UTC)


def test_live_uses_api_data(db_conn, sample_offers, monkeypatch):
    offer = sample_offers["data"][0]

    def fake_read_live_offers():
        return [offer], 2

    def forbidden_demo_read(path):
        raise AssertionError("Live import must not read the demo sample.")

    monkeypatch.setattr(justjoinit, "read_live_offers", fake_read_live_offers)
    monkeypatch.setattr(pipeline, "read_demo_offers", forbidden_demo_read)

    before = datetime.now(UTC)
    pipeline.run_pipeline(mode="live")
    after = datetime.now(UTC)

    rows = db_conn.execute("SELECT payload, fetched_at FROM raw.offers;").fetchall()

    assert len(rows) == 1
    assert rows[0][0] == offer
    assert before <= rows[0][1] <= after
    assert db_conn.execute("SELECT pages_fetched FROM raw.ingestion_runs;").fetchone()[0] == 2


def test_saves_rejected_offer_with_error_and_run_id(db_conn):
    offer = {"slug": ""}
    run_id = uuid.uuid4()

    count = loader.load_rejected_offers(db_conn, [(offer, "slug must not be empty.")], run_id)

    row = db_conn.execute(
        """
        SELECT payload, error_type, error_message, run_id
        FROM raw.rejected_records;
        """
    ).fetchone()

    assert count == 1
    assert row == (
        offer,
        "validation_error",
        "slug must not be empty.",
        run_id,
    )


@pytest.mark.parametrize("mode", ["demo", "live"])
def test_pipeline_saves_valid_offer_and_rejection(db_conn, sample_offers, monkeypatch, mode):
    valid = {**sample_offers["data"][0], "extraField": "keep"}
    invalid = {**valid, "slug": ""}
    offers = [valid, invalid]

    if mode == "demo":
        monkeypatch.setattr(pipeline, "read_demo_offers", lambda path: offers)
    else:
        monkeypatch.setattr(justjoinit, "read_live_offers", lambda: ([valid, invalid], 1))
    pipeline.run_pipeline(mode=mode)

    accepted_row = db_conn.execute("SELECT payload, run_id, data_mode FROM raw.offers;").fetchone()
    rejected_row = db_conn.execute(
        """
        SELECT payload, error_type, error_message, run_id
        FROM raw.rejected_records;
        """
    ).fetchone()
    run_row = db_conn.execute(
        """
        SELECT run_id, status, records_accepted, records_rejected
        FROM raw.ingestion_runs;
        """
    ).fetchone()

    assert accepted_row is not None
    assert rejected_row is not None
    assert run_row is not None
    assert accepted_row[0] == valid
    assert accepted_row[2] == mode
    assert rejected_row[0] == invalid
    assert rejected_row[1] == "validation_error"
    assert "slug must not be empty" in rejected_row[2]
    assert accepted_row[1] == rejected_row[3] == run_row[0]
    assert run_row[1:] == ("success", 1, 1)


def test_pipeline_rolls_back_offer_when_rejection_write_fails(db_conn, sample_offers, monkeypatch):
    valid = sample_offers["data"][0]
    invalid = {**valid, "slug": ""}

    monkeypatch.setattr(justjoinit, "read_live_offers", lambda: ([valid, invalid], 1))

    def fail_rejection_write(conn, rejected, run_id):
        count = conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0]
        assert count == 1
        raise RuntimeError("Simulated rejection write failure")

    monkeypatch.setattr(loader, "load_rejected_offers", fail_rejection_write)

    with pytest.raises(RuntimeError, match="rejection write failure"):
        pipeline.run_pipeline(mode="live")

    assert db_conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0] == 0
    assert db_conn.execute("SELECT count(*) FROM raw.rejected_records;").fetchone()[0] == 0
    assert db_conn.execute("SELECT status FROM raw.ingestion_runs;").fetchone()[0] == "failed"


@pytest.mark.parametrize("mode", ["demo", "live"])
def test_fetch_failure_is_recorded(db_conn, monkeypatch, mode):
    def fail_fetch(*args):
        raise RuntimeError("Simulated fetch failure")

    monkeypatch.setattr(pipeline, "read_demo_offers", fail_fetch)
    monkeypatch.setattr(justjoinit, "read_live_offers", fail_fetch)

    with pytest.raises(RuntimeError, match="Simulated fetch failure"):
        pipeline.run_pipeline(mode=mode)

    row = db_conn.execute(
        """
        SELECT status, stage, error_type, error_message,
               pages_fetched, records_accepted, records_rejected,
               finished_at
        FROM raw.ingestion_runs;
        """
    ).fetchone()

    assert row is not None
    assert row[:7] == (
        "failed",
        "fetch",
        "RuntimeError",
        "Simulated fetch failure",
        None,
        0,
        0,
    )
    assert row[7] is not None
    assert db_conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0] == 0
    data_mode, observed_date, started_at = db_conn.execute(
        """
    SELECT data_mode, observed_date, started_at
    FROM raw.ingestion_runs;
    """
    ).fetchone()

    expected_date = (
        datetime(2026, 8, 11, tzinfo=UTC).date()
        if mode == "demo"
        else started_at.astimezone(UTC).date()
    )
    assert data_mode == mode
    assert observed_date == expected_date


def test_status_write_failure_preserves_original_error(db_conn, monkeypatch):
    def fail_fetch():
        raise RuntimeError("Original fetch failure")

    def fail_status_write(*args, **kwargs):
        raise OSError("Simulated status write failure")

    monkeypatch.setattr(justjoinit, "read_live_offers", fail_fetch)
    monkeypatch.setattr(loader, "log_run_finish", fail_status_write)

    with pytest.raises(RuntimeError, match="Original fetch failure"):
        pipeline.run_pipeline(mode="live")


def test_same_day_import_keeps_previously_seen_offers(db_conn):
    first_fetch = datetime(2026, 10, 8, 10, tzinfo=UTC)
    second_fetch = datetime(2026, 10, 8, 12, tzinfo=UTC)
    first_offers = [
        {"slug": "offer-a", "title": "Old title"},
        {"slug": "offer-b"},
    ]
    second_offers = [
        {"slug": "offer-a", "title": "New title"},
        {"slug": "offer-c"},
    ]

    load_raw_offers(
        db_conn,
        first_offers,
        "justjoin.it",
        uuid.uuid4(),
        first_fetch,
        data_mode="live",
    )
    load_raw_offers(
        db_conn,
        second_offers,
        "justjoin.it",
        uuid.uuid4(),
        second_fetch,
        data_mode="live",
    )

    rows = db_conn.execute(
        """
        SELECT source_offer_id, payload, fetched_at
        FROM raw.offers
        ORDER BY source_offer_id;
        """
    ).fetchall()

    assert [row[0] for row in rows] == ["offer-a", "offer-b", "offer-c"]
    assert rows[0][1]["title"] == "New title"
    assert rows[0][2] == second_fetch
    assert rows[1][2] == first_fetch


def test_next_day_import_creates_new_observation(db_conn):
    first_fetch = datetime(2026, 10, 8, 10, tzinfo=UTC)
    second_fetch = datetime(2026, 10, 9, 10, tzinfo=UTC)

    for fetched_at in (first_fetch, second_fetch):
        load_raw_offers(
            db_conn,
            [{"slug": "offer-a"}],
            "justjoin.it",
            uuid.uuid4(),
            fetched_at,
            data_mode="live",
        )

    rows = db_conn.execute(
        """
        SELECT fetched_at
        FROM raw.offers
        WHERE source_offer_id = 'offer-a'
        ORDER BY fetched_at;
        """
    ).fetchall()

    assert rows == [(first_fetch,), (second_fetch,)]

import uuid
from datetime import UTC, datetime

from poznan_it_market.ingest import loader
from poznan_it_market.ingest.loader import load_raw_offers


def test_load_raw_offers_updates_payload_and_run_id_on_conflict(db_conn):
    now = datetime.now(UTC)
    offer_v1 = {"slug": "offer-1", "employmentTypes": [{"toPerUnit": 15000}]}
    offer_v2 = {"slug": "offer-1", "employmentTypes": [{"toPerUnit": 20000}]}
    run_id_1, run_id_2, run_id_3 = [uuid.uuid4() for _ in range(3)]

    load_raw_offers(db_conn, [offer_v1], "justjoin.it", run_id_1, now)
    observation_id = db_conn.execute("SELECT id FROM raw.offers;").fetchone()[0]

    load_raw_offers(db_conn, [offer_v1], "justjoin.it", run_id_2, now)
    rows = db_conn.execute("SELECT id, payload, run_id FROM raw.offers;").fetchall()
    assert rows == [(observation_id, offer_v1, run_id_2)]

    load_raw_offers(db_conn, [offer_v2], "justjoin.it", run_id_3, now)
    rows = db_conn.execute("SELECT id, payload, run_id FROM raw.offers;").fetchall()
    assert rows == [(observation_id, offer_v2, run_id_3)]


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

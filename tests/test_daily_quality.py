import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from jinja2 import Environment, StrictUndefined


@pytest.fixture
def quality_db(db_conn):
    db_conn.execute("""
        CREATE TEMP TABLE quality_runs (
            run_id uuid,
            started_at timestamptz,
            finished_at timestamptz,
            pages_fetched int,
            records_accepted int,
            records_rejected int,
            status text,
            stage text,
            data_mode text,
            observed_date date
        );
        CREATE TEMP TABLE quality_offers (date_id date);
    """)
    return db_conn


def add_run(conn, *, day=8, mode="live", status="success", accepted=100, rejected=0, hour=12):
    started_at = datetime(2026, 10, day, hour, tzinfo=UTC)
    conn.execute(
        """
        INSERT INTO quality_runs VALUES (%s, %s, %s, 1, %s, %s, %s,
                                        'finished', %s, %s);
        """,
        (uuid.uuid4(), started_at, started_at, accepted, rejected, status, mode, started_at.date()),
    )


def add_offers(conn, count, *, day=8):
    conn.execute(
        "INSERT INTO quality_offers SELECT %s::date FROM generate_series(1, %s);",
        (datetime(2026, 10, day, tzinfo=UTC).date(), count),
    )


def run_check(conn, name):
    query_path = Path(__file__).resolve().parent.parent / "dbt/tests" / f"{name}.sql"
    settings = {"expected_date": "2026-10-08", "data_mode": "live"}

    def source(schema, table):
        assert (schema, table) == ("raw", "ingestion_runs")
        return "quality_runs"

    def ref(model):
        assert model == "fct_offer_snapshot"
        return "quality_offers"

    query = (
        Environment(undefined=StrictUndefined)
        .from_string(query_path.read_text(encoding="utf-8"))
        .render(
            var=lambda name, default=None: settings.get(name, default),
            source=source,
            ref=ref,
            run_started_at=datetime(2026, 10, 8, tzinfo=UTC),
        )
    )
    return conn.execute(query).fetchall()


@pytest.mark.parametrize(
    "has_run,accepted,offers,status,reason",
    [
        (False, 100, 0, "success", "missing_import"),
        (True, 0, 0, "success", "no_accepted_offers"),
        (True, 100, 0, "success", "no_report_offers"),
        (True, 100, 1, "failed", "unfinished_or_failed_import"),
        (True, 100, 1, "running", "unfinished_or_failed_import"),
        (True, None, 1, "success", "invalid_import_counters"),
        (True, 100, 1, "success", None),
    ],
)
def test_daily_completeness(quality_db, has_run, accepted, offers, status, reason):
    if has_run:
        add_run(quality_db, accepted=accepted, status=status)
    add_offers(quality_db, offers)

    rows = run_check(quality_db, "assert_daily_offers_completeness")

    assert [row[-1] for row in rows] == ([] if reason is None else [reason])


def test_later_failure_is_not_hidden_by_earlier_success(quality_db):
    add_run(quality_db)
    add_run(quality_db, status="failed", hour=13)
    add_offers(quality_db, 100)

    rows = run_check(quality_db, "assert_daily_offers_completeness")

    assert [row[-1] for row in rows] == ["unfinished_or_failed_import"]


@pytest.mark.parametrize("day,mode", [(7, "live"), (8, "demo")])
def test_other_day_or_mode_does_not_satisfy_completeness(quality_db, day, mode):
    add_run(quality_db, day=day, mode=mode)
    add_offers(quality_db, 100)

    rows = run_check(quality_db, "assert_daily_offers_completeness")

    assert [row[-1] for row in rows] == ["missing_import"]


@pytest.mark.parametrize("offers,should_fail", [(59, True), (60, False)])
def test_volume_threshold(quality_db, offers, should_fail):
    add_run(quality_db, day=7)
    add_offers(quality_db, 100, day=7)
    add_offers(quality_db, offers)

    rows = run_check(quality_db, "assert_daily_offer_volume")

    assert bool(rows) is should_fail
    if rows:
        assert rows[0][-1] == "offer_volume_drop"


def test_no_history_skips_only_volume_comparison(quality_db):
    add_offers(quality_db, 1)

    assert run_check(quality_db, "assert_daily_offer_volume") == []
    assert run_check(quality_db, "assert_daily_offers_completeness")


@pytest.mark.parametrize(
    "status,accepted,rejected",
    [
        ("failed", 100, 0),
        ("success", 89, 11),
    ],
)
def test_bad_import_is_excluded_from_volume_average(quality_db, status, accepted, rejected):
    add_run(quality_db, day=7, status=status, accepted=accepted, rejected=rejected)
    add_offers(quality_db, 100, day=7)
    add_offers(quality_db, 1)

    assert run_check(quality_db, "assert_daily_offer_volume") == []


@pytest.mark.parametrize(
    "accepted,rejected,should_fail",
    [
        (100, 0, False),
        (90, 10, False),
        (89, 11, True),
    ],
)
def test_rejection_threshold(quality_db, accepted, rejected, should_fail):
    add_run(quality_db, accepted=accepted, rejected=rejected)

    rows = run_check(quality_db, "assert_daily_rejection_rate")

    assert bool(rows) is should_fail
    if rows:
        assert rows[0][-1] == "high_rejection_rate"

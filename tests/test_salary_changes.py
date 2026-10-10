from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path


def test_salary_changes_detects_only_comparable_changes(db_conn):
    db_conn.execute(
        """
        CREATE TEMP TABLE offer_salary_history (
            raw_offer_id bigint,
            source text,
            source_offer_id text,
            employment_type text,
            currency text,
            salary_unit text,
            is_gross boolean,
            salary_from numeric,
            salary_to numeric,
            fetched_at timestamptz
        );
        """
    )

    amounts = [
        (None, None),
        (100, 200),
        (100, 200),
        (120, 200),
        (120, 250),
        (None, None),
    ]
    records = [
        (
            day,
            "source-a",
            "offer-1",
            "b2b",
            "pln",
            "hour",
            False,
            minimum,
            maximum,
            datetime(2026, 10, day, tzinfo=UTC),
        )
        for day, (minimum, maximum) in enumerate(amounts, start=1)
    ]

    other_variants = [
        ("source-b", "b2b", "pln", "hour", False),
        ("source-a", "b2b", "eur", "hour", False),
        ("source-a", "permanent", "pln", "hour", False),
        ("source-a", "b2b", "pln", "month", False),
        ("source-a", "b2b", "pln", "hour", True),
    ]
    for row_id, variant in enumerate(other_variants, start=100):
        source, contract, currency, unit, gross = variant
        records.append(
            (
                row_id,
                source,
                "offer-1",
                contract,
                currency,
                unit,
                gross,
                900,
                1000,
                datetime(2026, 10, 3, tzinfo=UTC),
            )
        )

    with db_conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO offer_salary_history
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            records,
        )

    query_path = Path(__file__).resolve().parent.parent / "sql/analysis/04_salary_changes.sql"
    query = query_path.read_text(encoding="utf-8")
    rows = db_conn.execute(query, {"start_date": None, "end_date": None}).fetchall()

    assert [row[6].day for row in rows] == [2, 4, 5, 6]
    assert [row[8:] for row in rows] == [
        (None, None, 100, 200),
        (100, 200, 120, 200),
        (120, 200, 120, 250),
        (120, 250, None, None),
    ]
    assert all(row[:6] == ("source-a", "offer-1", "b2b", "pln", "hour", False) for row in rows)
    # Date filters use UTC and must not remove the previous observation before LAG.
    db_conn.execute("SET LOCAL TIME ZONE 'Pacific/Honolulu';")
    cases = [
        (date(2026, 10, 1), date(2026, 10, 1), []),
        (date(2026, 10, 2), date(2026, 10, 2), [rows[0]]),
        (date(2026, 10, 4), date(2026, 10, 4), [rows[1]]),
        (None, date(2026, 10, 4), rows[:2]),
        (date(2026, 10, 5), None, rows[2:]),
        (date(2026, 10, 10), date(2026, 10, 10), []),
    ]
    for start_date, end_date, expected in cases:
        actual = db_conn.execute(query, {"start_date": start_date, "end_date": end_date}).fetchall()
        assert actual == expected, (start_date, end_date, actual)


def test_salary_average_weights_offers_equally(db_conn):
    db_conn.execute("""
        CREATE TEMP TABLE fct_offer_snapshot (
            raw_offer_id bigint,
            source text,
            source_offer_id text,
            date_id date,
            fetched_at timestamptz
        );
        CREATE TEMP TABLE offer_salary_history (
            raw_offer_id bigint,
            source text,
            source_offer_id text,
            experience_level text,
            employment_type text,
            currency text,
            salary_unit text,
            is_gross boolean,
            salary_from numeric
        );

        INSERT INTO fct_offer_snapshot VALUES
            (1, 'source-a', 'offer-a', '2026-10-09', '2026-10-09T12:00:00Z'),
            (2, 'source-a', 'offer-b', '2026-10-09', '2026-10-09T12:00:00Z');

        INSERT INTO offer_salary_history VALUES
            (1, 'source-a', 'offer-a', 'senior', 'b2b', 'pln', 'month', false, 10000),
            (1, 'source-a', 'offer-a', 'senior', 'b2b', 'pln', 'month', false, 20000),
            (2, 'source-a', 'offer-b', 'senior', 'b2b', 'pln', 'month', false, 30000);
    """)

    query_path = Path(__file__).resolve().parent.parent / "sql/analysis/05_salary_by_level.sql"
    query = query_path.read_text(encoding="utf-8")
    rows = db_conn.execute(query, {"start_date": None, "end_date": None}).fetchall()
    assert rows == [("senior", "b2b", "month", False, Decimal("22500.00"), 2)]

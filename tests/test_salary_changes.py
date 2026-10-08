from datetime import UTC, datetime
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
    rows = db_conn.execute(query_path.read_text(encoding="utf-8")).fetchall()

    assert [row[6].day for row in rows] == [2, 4, 5, 6]
    assert [row[8:] for row in rows] == [
        (None, None, 100, 200),
        (100, 200, 120, 200),
        (120, 200, 120, 250),
        (120, 250, None, None),
    ]
    assert all(row[:6] == ("source-a", "offer-1", "b2b", "pln", "hour", False) for row in rows)

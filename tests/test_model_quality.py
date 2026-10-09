import hashlib
from datetime import date
from pathlib import Path

import pytest
from jinja2 import Environment, StrictUndefined


@pytest.fixture
def model_db(db_conn):
    db_conn.execute("""
        CREATE TEMP TABLE quality_facts (
            raw_offer_id bigint,
            source text,
            source_offer_id text,
            date_id date
        );
        CREATE TEMP TABLE quality_skills (
            raw_offer_id bigint,
            source text,
            source_offer_id text,
            date_id date,
            skill_name text
        );
        CREATE TEMP TABLE quality_companies (
            company_key text,
            company_name text,
            company_name_normalized text
        );
        CREATE TEMP TABLE quality_salaries (
            raw_offer_id bigint,
            employment_type text,
            currency text,
            salary_unit text,
            salary_from numeric,
            salary_to numeric
        );
    """)
    return db_conn


def run_model_check(conn, name):
    tables = {
        "fct_offer_snapshot": "quality_facts",
        "fct_offer_skill": "quality_skills",
        "dim_company": "quality_companies",
        "offer_salary_history": "quality_salaries",
    }
    path = Path(__file__).resolve().parent.parent / "dbt/tests" / f"{name}.sql"
    query = (
        Environment(undefined=StrictUndefined)
        .from_string(path.read_text(encoding="utf-8"))
        .render(ref=lambda model: tables[model])
    )
    return conn.execute(query).fetchall()


@pytest.mark.parametrize("duplicate", [False, True])
def test_offer_day_uniqueness(model_db, duplicate):
    model_db.execute("""
        INSERT INTO quality_facts VALUES
            (1, 'source-a', 'offer-1', '2026-10-08'),
            (2, 'source-b', 'offer-1', '2026-10-08'),
            (3, 'source-a', 'offer-1', '2026-10-09');
    """)
    if duplicate:
        model_db.execute("""
            INSERT INTO quality_facts VALUES
                (4, 'source-a', 'offer-1', '2026-10-08');
        """)

    rows = run_model_check(model_db, "assert_offer_day_unique")

    assert rows == ([("source-a", "offer-1", date(2026, 10, 8), 2)] if duplicate else [])


@pytest.mark.parametrize("duplicate", [False, True])
def test_offer_day_skill_uniqueness(model_db, duplicate):
    model_db.execute("""
        INSERT INTO quality_skills VALUES
            (1, 'source-a', 'offer-1', '2026-10-08', 'python'),
            (1, 'source-a', 'offer-1', '2026-10-08', 'sql'),
            (2, 'source-b', 'offer-1', '2026-10-08', 'python'),
            (3, 'source-a', 'offer-1', '2026-10-09', 'python');
    """)
    if duplicate:
        model_db.execute("""
            INSERT INTO quality_skills VALUES
                (4, 'source-a', 'offer-1', '2026-10-08', 'python');
        """)

    rows = run_model_check(model_db, "assert_offer_day_skill_unique")

    assert rows == ([("source-a", "offer-1", date(2026, 10, 8), "python", 2)] if duplicate else [])


@pytest.mark.parametrize(
    "offer_id,source,slug,day,should_fail",
    [
        (1, "source-a", "offer-1", 8, False),
        (99, "source-a", "offer-1", 8, True),
        (1, "source-b", "offer-1", 8, True),
        (1, "source-a", "offer-2", 8, True),
        (1, "source-a", "offer-1", 9, True),
    ],
)
def test_skill_matches_its_offer(model_db, offer_id, source, slug, day, should_fail):
    model_db.execute("""
        INSERT INTO quality_facts VALUES
            (1, 'source-a', 'offer-1', '2026-10-08');
    """)
    model_db.execute(
        "INSERT INTO quality_skills VALUES (%s, %s, %s, %s, 'python');",
        (offer_id, source, slug, date(2026, 10, day)),
    )

    rows = run_model_check(model_db, "assert_skill_matches_offer")

    assert len(rows) == int(should_fail)


@pytest.mark.parametrize(
    "minimum,maximum,should_fail",
    [
        (100, 200, False),
        (None, None, False),
        (None, 200, False),
        (100, None, False),
        (200, 100, True),
        (-1, None, True),
        (None, -1, True),
        ("NaN", None, True),
        ("Infinity", None, True),
        (None, "-Infinity", True),
    ],
)
def test_salary_range_quality(model_db, minimum, maximum, should_fail):
    model_db.execute(
        "INSERT INTO quality_salaries VALUES (1, 'b2b', 'pln', 'hour', %s, %s);",
        (minimum, maximum),
    )

    rows = run_model_check(model_db, "assert_salary_range_valid")

    assert len(rows) == int(should_fail)


@pytest.mark.parametrize(
    "name,normalized,wrong_key,should_fail",
    [
        (" Example Company ", "example company", False, False),
        ("Example Company", "EXAMPLE COMPANY", False, True),
        ("Example Company", "example company", True, True),
        ("   ", "", False, True),
    ],
)
def test_company_normalization_quality(model_db, name, normalized, wrong_key, should_fail):
    key = (
        "wrong-key"
        if wrong_key
        else hashlib.md5(normalized.encode(), usedforsecurity=False).hexdigest()
    )
    model_db.execute(
        "INSERT INTO quality_companies VALUES (%s, %s, %s);",
        (key, name, normalized),
    )

    rows = run_model_check(model_db, "assert_company_normalization")

    assert len(rows) == int(should_fail)

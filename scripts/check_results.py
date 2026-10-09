import argparse
import json
import os
from datetime import date
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict

from poznan_it_market import config


def check_demo_results(conn, analysis):
    payload = json.loads(config.DEMO_SAMPLE_PATH.read_text(encoding="utf-8"))
    offers = payload if isinstance(payload, list) else payload["data"]
    expected = {offer["slug"]: offer for offer in offers}
    assert len(expected) == len(offers), "The sample must have unique offer IDs."

    observed_date = config.DEMO_DATE
    params = {"start_date": observed_date, "end_date": observed_date}
    stored = conn.execute(
        """
        SELECT source_offer_id, payload
        FROM raw.offers
        WHERE source = 'justjoin.it' AND data_mode = 'demo'
          AND (fetched_at AT TIME ZONE 'UTC')::date = %s
        """,
        (observed_date,),
    ).fetchall()
    assert len(stored) == len(expected), "Unexpected number of demo observations."
    assert dict(stored) == expected, "Demo observations must match the saved sample."
    assert conn.execute("SELECT DISTINCT data_mode FROM public.stg_offers").fetchall() == [
        ("demo",)
    ], "Build dbt in demo mode before checking results."

    reports = {}
    for filename in (
        "06_postings_over_time.sql",
        "07_junior_share.sql",
        "01_top_companies.sql",
        "03_top_skills.sql",
        "02_salary_disclosure.sql",
        "05_salary_by_level.sql",
        "04_salary_changes.sql",
    ):
        reports[filename] = analysis(conn, filename, params)

    city_offers = [offer for offer in offers if offer.get("city") in {"Poznań", "Poznan"}]
    assert city_offers, "The demo sample must contain offers matching the city filter."
    junior_count = sum(offer.get("experienceLevel") == "junior" for offer in city_offers)

    postings = reports["06_postings_over_time.sql"]
    assert len(postings) == 1, postings
    assert postings[0][:2] == (observed_date, len(city_offers)), postings
    assert reports["07_junior_share.sql"] == [(observed_date, len(city_offers), junior_count)], (
        reports["07_junior_share.sql"]
    )

    print(f"PASS: {len(stored)} raw demo observations match the saved sample.")
    print(f"PASS: {len(city_offers)} report offers, including {junior_count} juniors.")
    print(f"PASS: all shared reports executed for {observed_date}.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify CI or demo results.")
    parser.add_argument("--mode", choices=["ci", "demo"], default="ci")
    args = parser.parse_args(argv)
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    variable = "DEMO_DATABASE_URL" if args.mode == "demo" else "TEST_DATABASE_URL"
    test_url = os.environ.get(variable)
    if not test_url:
        raise ValueError(f"{variable} is required for result checks.")
    expected_database = "poznan_it_market_demo" if args.mode == "demo" else "poznan_it_market_test"
    settings = conninfo_to_dict(test_url)
    if settings.get("dbname") != expected_database:
        raise ValueError(f"Result checks require {expected_database}.")
    if settings.get("host") not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Result checks require a local database.")

    def analysis(conn, filename, params=None):
        query = (project_root / "sql/analysis" / filename).read_text(encoding="utf-8")
        return conn.execute(query, params).fetchall()

    if args.mode == "demo":
        with psycopg.connect(test_url, options="-c default_transaction_read_only=on") as conn:
            check_demo_results(conn, analysis)
        return

    all_history = {"start_date": None, "end_date": None}
    first_day = {"start_date": date(2026, 8, 10), "end_date": date(2026, 8, 10)}
    second_day = {"start_date": date(2026, 8, 11), "end_date": date(2026, 8, 11)}
    both_days = {"start_date": date(2026, 8, 10), "end_date": date(2026, 8, 11)}
    empty_period = {"start_date": date(2026, 8, 12), "end_date": date(2026, 8, 12)}

    with psycopg.connect(test_url) as conn:
        daily = analysis(conn, "07_junior_share.sql", all_history)
        assert daily == [(date(2026, 8, 10), 2, 1), (date(2026, 8, 11), 2, 1)], daily
        postings = analysis(conn, "06_postings_over_time.sql", all_history)
        assert postings == [(date(2026, 8, 10), 2, 1), (date(2026, 8, 11), 2, 1)], postings

        observation_count, unique_offer_count = conn.execute(
            """
            SELECT count(*), count(DISTINCT (source, source_offer_id))
            FROM public.fct_offer_snapshot;
            """
        ).fetchone()
        skill_count = conn.execute("SELECT count(*) FROM public.fct_offer_skill;").fetchone()[0]
        assert observation_count == 4, observation_count
        assert unique_offer_count == 2, unique_offer_count
        assert skill_count == 5, skill_count
        assert analysis(conn, "01_top_companies.sql", all_history) == [("CI Example", 2)]
        assert analysis(conn, "03_top_skills.sql", all_history) == [("python", 2)]

        disclosure = analysis(conn, "02_salary_disclosure.sql", all_history)
        assert [row[:5] for row in disclosure] == [
            ("junior", 1, 1, 1, 0),
            ("senior", 1, 0, 0, 0),
        ], disclosure
        assert [row[5] for row in disclosure] == [100, 0], disclosure

        changes = analysis(conn, "04_salary_changes.sql", all_history)
        assert len(changes) == 1, changes
        assert changes[0][1] == "ci-junior", changes
        assert changes[0][6].date() == date(2026, 8, 11), changes
        assert changes[0][8:] == (10000, 15000, 12000, 17000), changes

        salaries = analysis(conn, "05_salary_by_level.sql", all_history)
        assert salaries == [("junior", "b2b", "month", False, 12000, 1)], salaries

        # Select the latest observation inside each period, not the latest overall.
        assert analysis(conn, "03_top_skills.sql", first_day) == [("python", 2), ("sql", 1)]
        assert analysis(conn, "05_salary_by_level.sql", first_day) == [
            ("junior", "b2b", "month", False, 10000, 1)
        ]
        for period in [second_day, both_days]:
            assert analysis(conn, "03_top_skills.sql", period) == [("python", 2)]
            assert analysis(conn, "05_salary_by_level.sql", period) == [
                ("junior", "b2b", "month", False, 12000, 1)
            ]
        for period in [first_day, second_day, both_days]:
            assert analysis(conn, "01_top_companies.sql", period) == [("CI Example", 2)]
            assert analysis(conn, "02_salary_disclosure.sql", period) == disclosure
        assert analysis(conn, "04_salary_changes.sql", first_day) == []
        assert analysis(conn, "04_salary_changes.sql", second_day) == changes
        assert analysis(conn, "04_salary_changes.sql", both_days) == changes
        for filename in [
            "04_salary_changes.sql",
            "01_top_companies.sql",
            "02_salary_disclosure.sql",
            "03_top_skills.sql",
            "05_salary_by_level.sql",
            "06_postings_over_time.sql",
            "07_junior_share.sql",
        ]:
            assert analysis(conn, filename, empty_period) == [], filename

    print("PASS: 4 observations, 2 unique offers, 50% juniors per day, 5 skill rows.")
    print("PASS: latest skills, salary disclosure and the single salary change match the fixture.")
    print("PASS: report periods select matching observations; empty periods return no rows.")


if __name__ == "__main__":
    main()

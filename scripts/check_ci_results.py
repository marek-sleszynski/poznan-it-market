import os
from datetime import date
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict


def main():
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    test_url = os.environ["TEST_DATABASE_URL"]
    settings = conninfo_to_dict(test_url)
    if settings.get("dbname") != "poznan_it_market_test":
        raise ValueError("CI result checks require poznan_it_market_test.")
    if settings.get("host") not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("CI result checks require a local database.")

    def analysis(conn, filename):
        query = (project_root / "sql/analysis" / filename).read_text(encoding="utf-8")
        return conn.execute(query).fetchall()

    with psycopg.connect(test_url) as conn:
        daily = conn.execute("""
            SELECT date_id, count(*), count(*) FILTER (WHERE experience_level = 'junior')
            FROM public.fct_offer_snapshot
            GROUP BY date_id
            ORDER BY date_id;
        """).fetchall()
        assert daily == [(date(2026, 8, 10), 2, 1), (date(2026, 8, 11), 2, 1)], daily

        latest_count = conn.execute("SELECT count(*) FROM public.latest_offers;").fetchone()[0]
        skill_count = conn.execute("SELECT count(*) FROM public.fct_offer_skill;").fetchone()[0]
        assert latest_count == 2, latest_count
        assert skill_count == 5, skill_count
        assert analysis(conn, "01_top_companies.sql") == [("CI Example", 2)]
        assert analysis(conn, "03_top_skills.sql") == [("python", 2)]

        disclosure = analysis(conn, "02_salary_disclosure.sql")
        assert [row[:5] for row in disclosure] == [
            ("junior", 1, 1, 1, 0),
            ("senior", 1, 0, 0, 0),
        ], disclosure
        assert [row[5] for row in disclosure] == [100, 0], disclosure

        changes = analysis(conn, "04_salary_changes.sql")
        assert len(changes) == 1, changes
        assert changes[0][1] == "ci-junior", changes
        assert changes[0][6].date() == date(2026, 8, 11), changes
        assert changes[0][8:] == (10000, 15000, 12000, 17000), changes

        salaries = analysis(conn, "05_salary_by_level.sql")
        assert salaries == [("junior", "b2b", "month", False, 12000, 1)], salaries

    print("PASS: 4 observations, 2 unique offers, 50% juniors per day, 5 skill rows.")
    print("PASS: latest skills, salary disclosure and the single salary change match the fixture.")


if __name__ == "__main__":
    main()

import json
import os
import subprocess
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict


def main():
    root = Path.cwd()
    if not (root / "sql/analysis").is_dir():
        raise ValueError("Run this script from the project root.")
    load_dotenv(root / ".env")
    url = os.environ["DEMO_DATABASE_URL"]
    settings = conninfo_to_dict(url)
    if settings.get("dbname") != "poznan_it_market_demo" or settings.get("host") not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise ValueError("Report checks require the local demo database.")

    observed_date = date(2026, 8, 11)
    params = {"start_date": observed_date, "end_date": observed_date}
    sample_path = root / "data/raw/sample/jjit_2026-08-11.json"
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    offers = payload if isinstance(payload, list) else payload["data"]
    expected = {offer["slug"]: offer for offer in offers}
    assert len(expected) == len(offers), "The sample must have unique offer IDs."

    print("Report mode: demo")
    print(f"Period (UTC): {observed_date} to {observed_date}")
    print("Source: data/raw/sample/jjit_2026-08-11.json")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    print(f"Code commit: {commit}")

    with psycopg.connect(url, options="-c default_transaction_read_only=on") as conn:
        stored = conn.execute(
            """
            SELECT source_offer_id, payload
            FROM raw.offers
            WHERE source = 'justjoin.it' AND data_mode = 'demo'
              AND (fetched_at AT TIME ZONE 'UTC')::date = %s
            """,
            (observed_date,),
        ).fetchall()
        assert dict(stored) == expected, "Demo observations must match the saved sample."
        assert conn.execute("SELECT DISTINCT data_mode FROM public.stg_offers").fetchall() == [
            ("demo",)
        ], "Build dbt in demo mode before checking the report."
        print(f"PASS: {len(stored)} raw observations match the sample exactly.")

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
            query = (root / "sql/analysis" / filename).read_text(encoding="utf-8")
            results = conn.execute(query, params).fetchall()
            reports[filename] = results
            print(f"\n{filename}")
            if results:
                for row in results:
                    print(row)
            else:
                print("No rows.")

    assert reports["06_postings_over_time.sql"] == [(observed_date, 5, 1)]
    assert reports["07_junior_share.sql"] == [(observed_date, 5, 1)]
    assert reports["01_top_companies.sql"] == [
        ("Haleon", 2),
        ("Upvanta sp. z o.o.", 2),
        ("cerebre", 1),
    ]
    skills = reports["03_top_skills.sql"]
    assert len(skills) == 15 and all(count == 1 for _, count in skills)
    assert ("python", 1) in skills and ("cloud", 1) in skills
    assert reports["02_salary_disclosure.sql"] == [
        ("senior", 2, 1, 1, 0, Decimal("50")),
        ("junior", 1, 1, 1, 0, Decimal("100")),
        ("manager", 1, 1, 1, 0, Decimal("100")),
        ("mid", 1, 1, 1, 0, Decimal("100")),
    ]
    assert reports["05_salary_by_level.sql"] == [
        ("junior", "b2b", "hour", False, Decimal("31.40"), 1),
        ("manager", "permanent", "month", True, Decimal("26500"), 1),
        ("senior", "permanent", "month", True, Decimal("18500"), 1),
    ]
    assert reports["04_salary_changes.sql"] == []
    print("\nPASS: report results match the published demo numbers.")


if __name__ == "__main__":
    main()

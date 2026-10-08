import json
import os
import subprocess
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from psycopg.conninfo import conninfo_to_dict
from psycopg.types.json import Jsonb


@pytest.mark.parametrize(
    "age_hours,expected_status,expected_exit_code",
    [(1, "pass", 0), (28, "warn", 0), (49, "error", 1)],
)
def test_live_source_freshness(db_conn, tmp_path, age_hours, expected_status, expected_exit_code):
    project_root = Path(__file__).resolve().parent.parent
    settings = conninfo_to_dict(os.environ["TEST_DATABASE_URL"])
    assert settings["dbname"] == "poznan_it_market_test"
    assert settings["host"] in {"localhost", "127.0.0.1", "::1"}

    now = datetime.now(UTC)
    records = [
        (
            "freshness-test",
            f"offer-{mode}",
            Jsonb({"slug": f"offer-{mode}"}),
            now - timedelta(hours=age_hours) if mode == "live" else now,
            uuid.uuid4(),
            mode,
        )
        for mode in ("live", "demo", "legacy_demo", "unknown")
    ]
    with db_conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO raw.offers
                (source, source_offer_id, payload, fetched_at, run_id, data_mode)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            records,
        )
    db_conn.commit()

    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    profile = (project_root / "dbt/profiles.yml.example").read_text(encoding="utf-8")
    (profile_dir / "profiles.yml").write_text(profile, encoding="utf-8")

    env = os.environ.copy()
    env.update(
        DB_HOST=settings["host"],
        DB_PORT=settings.get("port", "5432"),
        POSTGRES_USER=settings["user"],
        POSTGRES_PASSWORD=settings.get("password", ""),
        POSTGRES_DB=settings["dbname"],
        DB_SSLMODE=settings.get("sslmode", "prefer"),
    )
    target_dir = tmp_path / "target"
    result = subprocess.run(
        [
            "uv",
            "run",
            "dbt",
            "source",
            "freshness",
            "--project-dir",
            str(project_root / "dbt"),
            "--profiles-dir",
            str(profile_dir),
            "--target-path",
            str(target_dir),
            "--select",
            "source:raw.offers",
        ],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == expected_exit_code, result.stdout + result.stderr
    report = json.loads((target_dir / "sources.json").read_text(encoding="utf-8"))
    assert len(report["results"]) == 1
    assert report["results"][0]["status"] == expected_status

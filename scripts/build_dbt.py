import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from poznan_it_market import config
from poznan_it_market.dbt_config import dbt_environment_from_url


def build_dbt(mode: str, expected_date: str | None = None) -> None:
    if mode not in {"live", "demo"}:
        raise ValueError("mode must be live or demo.")
    database_url = config.DEMO_DATABASE_URL if mode == "demo" else config.DATABASE_URL
    if mode == "demo" and not database_url:
        raise ValueError("DEMO_DATABASE_URL is required for demo builds.")
    settings = dbt_environment_from_url(database_url)
    if mode == "demo":
        if settings["DB_HOST"] not in {"localhost", "127.0.0.1", "::1"} or settings[
            "POSTGRES_DB"
        ] not in {"poznan_it_market_demo", "poznan_it_market_test"}:
            raise ValueError("Demo builds require a local demo or test database.")
        if expected_date is None:
            expected_date = config.DEMO_DATE.isoformat()

    variables = {"data_mode": mode}
    if expected_date is not None:
        variables["expected_date"] = date.fromisoformat(expected_date).isoformat()

    project_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.update(settings)
    print(
        f"dbt mode={mode} database={settings['POSTGRES_DB']} host={settings['DB_HOST']}",
        flush=True,
    )
    # Use the shared profile template without overwriting local profiles.
    with tempfile.TemporaryDirectory(prefix="poznan-dbt-") as profiles_dir:
        shutil.copyfile(
            project_root / "dbt/profiles.yml.example",
            Path(profiles_dir) / "profiles.yml",
        )
        subprocess.run(
            [
                "uv",
                "run",
                "--locked",
                "dbt",
                "build",
                "--project-dir",
                str(project_root / "dbt"),
                "--profiles-dir",
                profiles_dir,
                "--vars",
                json.dumps(variables),
            ],
            cwd=project_root,
            env=env,
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dbt models for the selected database.")
    parser.add_argument("--mode", choices=["live", "demo"], required=True)
    parser.add_argument("--expected-date", help="Observation date in YYYY-MM-DD format.")
    args = parser.parse_args()
    build_dbt(args.mode, args.expected_date)


if __name__ == "__main__":
    main()

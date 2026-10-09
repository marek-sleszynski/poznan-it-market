import os
import subprocess
import sys
from pathlib import Path

from psycopg.conninfo import conninfo_to_dict

from poznan_it_market import config


def main() -> None:
    url = config.DEMO_DATABASE_URL
    if not url:
        raise ValueError("DEMO_DATABASE_URL is required for demo charts.")
    settings = conninfo_to_dict(url)
    if (
        settings.get("host") not in {"localhost", "127.0.0.1", "::1"}
        or settings.get("dbname") != "poznan_it_market_demo"
    ):
        raise ValueError("Demo charts require the local poznan_it_market_demo database.")

    root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env["DATABASE_URL"] = url
    env["MPLBACKEND"] = "Agg"
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/make_charts.py"),
            "--start-date",
            "2026-08-11",
            "--end-date",
            "2026-08-11",
        ],
        cwd=root,
        env=env,
        check=True,
    )


if __name__ == "__main__":
    main()

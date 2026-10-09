import os
import subprocess
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

from scripts import make_demo_charts


def test_demo_charts_use_demo_database_and_fixed_period(monkeypatch):
    url = "postgresql://postgres:postgres@localhost:55432/poznan_it_market_demo"
    monkeypatch.setattr(make_demo_charts.config, "DEMO_DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/live")
    captured = {}

    def record_run(command, *, cwd, env, check):
        captured.update(command=command, cwd=cwd, env=env, check=check)

    monkeypatch.setattr(make_demo_charts.subprocess, "run", record_run)
    make_demo_charts.main()

    root = Path(make_demo_charts.__file__).resolve().parent.parent
    assert captured["command"] == [
        sys.executable,
        str(root / "scripts/make_charts.py"),
        "--start-date",
        "2026-08-11",
        "--end-date",
        "2026-08-11",
    ]
    assert captured["cwd"] == root
    assert captured["env"]["DATABASE_URL"] == url
    assert captured["env"]["MPLBACKEND"] == "Agg"
    assert captured["check"] is True


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        "postgresql://postgres:postgres@example.invalid/poznan_it_market_demo",
        "postgresql://postgres:postgres@localhost/poznan_it_market",
    ],
)
def test_demo_charts_reject_missing_or_wrong_database(monkeypatch, url):
    monkeypatch.setattr(make_demo_charts.config, "DEMO_DATABASE_URL", url)

    def forbidden_run(*args, **kwargs):
        raise AssertionError("Invalid demo settings must fail before running charts.")

    monkeypatch.setattr(make_demo_charts.subprocess, "run", forbidden_run)
    with pytest.raises(ValueError, match="demo|Demo"):
        make_demo_charts.main()


def test_demo_chart_failure_propagates(monkeypatch):
    monkeypatch.setattr(
        make_demo_charts.config,
        "DEMO_DATABASE_URL",
        "postgresql://postgres:postgres@localhost/poznan_it_market_demo",
    )

    def failed_run(command, **kwargs):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(make_demo_charts.subprocess, "run", failed_run)
    with pytest.raises(subprocess.CalledProcessError):
        make_demo_charts.main()


@pytest.mark.parametrize("port", [None, "55432"])
def test_example_database_urls_follow_local_port(monkeypatch, port):
    env = {} if port is None else {"POSTGRES_PORT": port}
    monkeypatch.setattr(os, "environ", env)
    root = Path(__file__).resolve().parent.parent
    load_dotenv(root / ".env.example")

    expected_port = port or "5432"
    for variable, database in (
        ("DATABASE_URL", "poznan_it_market"),
        ("DEMO_DATABASE_URL", "poznan_it_market_demo"),
        ("TEST_DATABASE_URL", "poznan_it_market_test"),
    ):
        assert (
            env[variable] == f"postgresql://postgres:postgres@localhost:{expected_port}/{database}"
        )

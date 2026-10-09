import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_without_settings(code, **settings):
    env = os.environ.copy()
    for name in ("DATABASE_URL", "DEMO_DATABASE_URL", "JJIT_API_URL"):
        env.pop(name, None)
    env.update(settings)
    setup = """
import dotenv
import psycopg

# Ignore the developer's .env only in this isolated test process.
dotenv.load_dotenv = lambda *args, **kwargs: False

def forbidden_connection(*args, **kwargs):
    raise AssertionError("This test must not connect to a database.")

psycopg.connect = forbidden_connection
"""
    result = subprocess.run(
        [sys.executable, "-c", setup + "\n" + code],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "module",
    [
        "poznan_it_market.ingest.justjoinit",
        "scripts.make_charts",
        "learning.python.load_scratch",
    ],
)
def test_import_does_not_require_database_or_api_settings(module):
    run_without_settings(f"import importlib; importlib.import_module({module!r})")


def test_api_uses_configured_url_without_database_settings():
    run_without_settings(
        """
import httpx
from poznan_it_market.ingest.justjoinit import fetch_justjoinit_pages

requests = []
payload = {"data": [], "meta": {"from": 0, "next": {"cursor": None}}}

def handler(request):
    requests.append(request)
    assert str(request.url).split("?")[0] == "https://example.test/custom-offers"
    return httpx.Response(200, json=payload)

with httpx.Client(transport=httpx.MockTransport(handler)) as client:
    assert list(fetch_justjoinit_pages(client)) == [payload]

assert len(requests) == 1
""",
        JJIT_API_URL="https://example.test/custom-offers",
    )


def test_loader_requires_database_before_connecting(monkeypatch):
    from poznan_it_market.ingest import loader

    def forbidden_connection(*args, **kwargs):
        raise AssertionError("Missing configuration must be detected before connecting.")

    monkeypatch.setattr(loader, "DATABASE_URL", "")
    monkeypatch.setattr(loader.psycopg, "connect", forbidden_connection)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        loader.get_connection()


def test_empty_explicit_url_does_not_use_default_database(monkeypatch):
    from poznan_it_market.ingest import loader

    def forbidden_connection(*args, **kwargs):
        raise AssertionError("An empty explicit URL must not select another database.")

    monkeypatch.setattr(loader, "DATABASE_URL", "postgresql://localhost/other_database")
    monkeypatch.setattr(loader.psycopg, "connect", forbidden_connection)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        loader.get_connection("")


@pytest.mark.parametrize(
    "function",
    [
        "get_postings_over_time_data",
        "get_junior_share_data",
        "get_top_skills_data",
        "get_salary_by_level_data",
    ],
)
def test_chart_queries_require_database_before_connecting(function):
    run_without_settings(
        f"""
from scripts import make_charts

try:
    getattr(make_charts, {function!r})()
except ValueError as error:
    assert "DATABASE_URL" in str(error)
else:
    raise AssertionError("Expected a missing database configuration error.")
"""
    )


def test_scratch_loader_requires_database_before_connecting():
    run_without_settings(
        """
import tempfile
from pathlib import Path
from learning.python import load_scratch

with tempfile.TemporaryDirectory() as directory:
    sample = Path(directory) / "sample.json"
    sample.write_text('{"data": []}', encoding="utf-8")
    load_scratch.SAMPLE_PATH = sample
    try:
        load_scratch.load_sample()
    except ValueError as error:
        assert "DATABASE_URL" in str(error)
    else:
        raise AssertionError("Expected a missing database configuration error.")
"""
    )

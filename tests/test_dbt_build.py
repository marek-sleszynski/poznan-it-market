import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts import build_dbt


@pytest.mark.parametrize("mode", ["live", "demo"])
def test_selected_mode_controls_database_and_models(monkeypatch, mode):
    monkeypatch.setattr(
        build_dbt.config,
        "DATABASE_URL",
        "postgresql://live_user:fake_password@cloud.example:5544/market?sslmode=require",
    )
    monkeypatch.setattr(
        build_dbt.config,
        "DEMO_DATABASE_URL",
        "postgresql://demo_user:fake_password@localhost:5566/poznan_it_market_demo?sslmode=disable",
    )
    monkeypatch.setenv("DB_HOST", "wrong.example")
    monkeypatch.setenv("POSTGRES_DB", "wrong_database")
    calls = []

    def capture_command(command, *, cwd, env, check):
        calls.append(command)
        assert check is True
        assert command[:5] == ["uv", "run", "--locked", "dbt", "build"]
        assert Path(command[command.index("--project-dir") + 1]) == cwd / "dbt"
        profile = Path(command[command.index("--profiles-dir") + 1]) / "profiles.yml"
        assert profile.read_text() == (cwd / "dbt/profiles.yml.example").read_text()
        variables = json.loads(command[command.index("--vars") + 1])
        assert variables == {"data_mode": mode, "expected_date": "2026-08-11"}
        if mode == "demo":
            assert env["DB_HOST"] == "localhost"
            assert env["DB_PORT"] == "5566"
            assert env["POSTGRES_DB"] == "poznan_it_market_demo"
            assert env["POSTGRES_USER"] == "demo_user"
            assert env["DB_SSLMODE"] == "disable"
        else:
            assert env["DB_HOST"] == "cloud.example"
            assert env["DB_PORT"] == "5544"
            assert env["POSTGRES_DB"] == "market"
            assert env["POSTGRES_USER"] == "live_user"
            assert env["DB_SSLMODE"] == "require"

    monkeypatch.setattr(build_dbt.subprocess, "run", capture_command)
    build_dbt.build_dbt(mode, "2026-08-11")
    assert len(calls) == 1


@pytest.mark.parametrize(
    ("url", "expected_date", "message"),
    [
        (
            "postgresql://user:fake_password@cloud.example/poznan_it_market_demo",
            "2026-08-11",
            "local demo or test database",
        ),
        (
            "postgresql://user:fake_password@localhost/production",
            "2026-08-11",
            "local demo or test database",
        ),
        (None, "2026-08-11", "DEMO_DATABASE_URL is required"),
        (
            "postgresql://user:fake_password@localhost/poznan_it_market_demo",
            "not-a-date",
            "Invalid isoformat string",
        ),
    ],
)
def test_invalid_demo_target_never_starts_dbt(monkeypatch, url, expected_date, message):
    monkeypatch.setattr(build_dbt.config, "DEMO_DATABASE_URL", url)

    def forbidden_command(*args, **kwargs):
        pytest.fail("Invalid demo settings must not start dbt.")

    monkeypatch.setattr(build_dbt.subprocess, "run", forbidden_command)
    with pytest.raises(ValueError, match=message):
        build_dbt.build_dbt("demo", expected_date)


def test_dbt_failure_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(
        build_dbt.config,
        "DEMO_DATABASE_URL",
        "postgresql://user:fake_password@localhost/poznan_it_market_demo",
    )
    failure = subprocess.CalledProcessError(1, ["dbt", "build"])

    def fail_build(*args, **kwargs):
        raise failure

    monkeypatch.setattr(build_dbt.subprocess, "run", fail_build)
    with pytest.raises(subprocess.CalledProcessError) as error:
        build_dbt.build_dbt("demo", "2026-08-11")
    assert error.value is failure


def test_demo_build_uses_shared_sample_date(monkeypatch):
    monkeypatch.setattr(
        build_dbt.config,
        "DEMO_DATABASE_URL",
        "postgresql://user:fake_password@localhost:55432/poznan_it_market_demo",
    )
    monkeypatch.setattr(build_dbt.config, "DEMO_DATE", date(2020, 2, 3))
    captured_variables = []

    def capture_command(command, **kwargs):
        assert kwargs["check"] is True
        captured_variables.append(json.loads(command[command.index("--vars") + 1]))

    monkeypatch.setattr(build_dbt.subprocess, "run", capture_command)

    build_dbt.build_dbt("demo")

    assert captured_variables == [{"data_mode": "demo", "expected_date": "2020-02-03"}]

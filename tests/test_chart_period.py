import os
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from dotenv import load_dotenv

from scripts import make_charts

REPORTS = [
    ("get_postings_over_time_data", "plot_postings_over_time"),
    ("get_junior_share_data", "plot_junior_share"),
    ("get_top_skills_data", "plot_top_skills"),
    ("get_salary_by_level_data", "plot_salary_by_level"),
]


@pytest.mark.parametrize(
    "arguments,expected_period",
    [
        ([], (None, None)),
        (
            ["--start-date", "2026-08-10", "--end-date", "2026-08-11"],
            (date(2026, 8, 10), date(2026, 8, 11)),
        ),
        (
            ["--start-date", "2026-08-09", "--end-date", "2026-08-12"],
            (date(2026, 8, 9), date(2026, 8, 12)),
        ),
        (["--start-date", "2026-08-10"], (date(2026, 8, 10), None)),
        (["--end-date", "2026-08-11"], (None, date(2026, 8, 11))),
    ],
)
def test_chart_cli_uses_same_period_for_all_reports(monkeypatch, arguments, expected_period):
    fetched = []
    plotted = []

    def fake_getter(name):
        def get_data(start_date, end_date):
            fetched.append((name, start_date, end_date))
            return [(date(2026, 8, 10), name), (date(2026, 8, 11), name)]

        return get_data

    def fake_plotter(name):
        def plot(rows, period):
            plotted.append((name, rows, period))

        return plot

    for getter, plotter in REPORTS:
        monkeypatch.setattr(make_charts, getter, fake_getter(getter))
        monkeypatch.setattr(make_charts, plotter, fake_plotter(plotter))

    make_charts.main(arguments)
    assert fetched == [(getter, *expected_period) for getter, _ in REPORTS]
    start = expected_period[0] or date(2026, 8, 10)
    end = expected_period[1] or date(2026, 8, 11)
    assert plotted == [
        (plotter, [(date(2026, 8, 10), getter), (date(2026, 8, 11), getter)], f"{start} to {end}")
        for getter, plotter in REPORTS
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--start-date", "2026-08-12", "--end-date", "2026-08-11"],
        ["--start-date", "2026-02-30"],
    ],
)
def test_chart_cli_rejects_bad_dates_before_database_access(monkeypatch, arguments):
    def forbidden_read(*args):
        raise AssertionError("Invalid dates must be rejected before database access.")

    for getter, _ in REPORTS:
        monkeypatch.setattr(make_charts, getter, forbidden_read)
    with pytest.raises(SystemExit) as error:
        make_charts.main(arguments)
    assert error.value.code == 2


def test_chart_cli_rejects_empty_period_before_plotting(monkeypatch):
    def empty_data(*args):
        return []

    def forbidden_plot(*args):
        raise AssertionError("An empty period must be rejected before plotting.")

    for getter, plotter in REPORTS:
        monkeypatch.setattr(make_charts, getter, empty_data)
        monkeypatch.setattr(make_charts, plotter, forbidden_plot)
    with pytest.raises(SystemExit) as error:
        make_charts.main(["--start-date", "2026-08-12", "--end-date", "2026-08-12"])
    assert error.value.code == 2


def test_demo_charts_use_demo_database_and_shared_date(monkeypatch):
    url = "postgresql://postgres:postgres@localhost:55432/poznan_it_market_demo"
    sample_date = date(2020, 2, 3)
    monkeypatch.setattr(make_charts.config, "DEMO_DATABASE_URL", url)
    monkeypatch.setattr(make_charts.config, "DEMO_DATE", sample_date)
    monkeypatch.setattr(make_charts, "DATABASE_URL", "postgresql://example.invalid/live")

    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.execute.return_value.fetchall.return_value = [(sample_date, 5, 1)]
    connected_urls = []

    def connect(database_url):
        connected_urls.append(database_url)
        return connection

    monkeypatch.setattr(make_charts.psycopg, "connect", connect)
    for _, plotter in REPORTS:
        monkeypatch.setattr(make_charts, plotter, lambda rows, period: None)

    make_charts.main(["--mode", "demo"])

    assert connected_urls == [url] * 4
    assert connection.execute.call_count == 4
    for call in connection.execute.call_args_list:
        assert call.args[1] == {"start_date": sample_date, "end_date": sample_date}


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
    monkeypatch.setattr(make_charts.config, "DEMO_DATABASE_URL", url)

    def forbidden_connection(*args, **kwargs):
        pytest.fail("Invalid demo settings must fail before database access.")

    monkeypatch.setattr(make_charts.psycopg, "connect", forbidden_connection)
    with pytest.raises(ValueError, match="demo|Demo"):
        make_charts.main(["--mode", "demo"])


def test_demo_chart_failure_propagates(monkeypatch):
    monkeypatch.setattr(
        make_charts.config,
        "DEMO_DATABASE_URL",
        "postgresql://postgres:postgres@localhost/poznan_it_market_demo",
    )
    failure = RuntimeError("Chart query failed.")

    def failed_connection(*args, **kwargs):
        raise failure

    monkeypatch.setattr(make_charts.psycopg, "connect", failed_connection)
    with pytest.raises(RuntimeError) as error:
        make_charts.main(["--mode", "demo"])
    assert error.value is failure


@pytest.mark.parametrize(
    "arguments",
    [
        ["--start-date", "2026-08-10"],
        ["--end-date", "2026-08-12"],
    ],
)
def test_demo_charts_reject_dates_outside_sample(monkeypatch, arguments):
    monkeypatch.setattr(
        make_charts.config,
        "DEMO_DATABASE_URL",
        "postgresql://postgres:postgres@localhost/poznan_it_market_demo",
    )
    monkeypatch.setattr(make_charts.config, "DEMO_DATE", date(2026, 8, 11))

    def forbidden_connection(*args, **kwargs):
        pytest.fail("Invalid demo dates must fail before database access.")

    monkeypatch.setattr(make_charts.psycopg, "connect", forbidden_connection)
    with pytest.raises(SystemExit) as error:
        make_charts.main(["--mode", "demo", *arguments])
    assert error.value.code == 2


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

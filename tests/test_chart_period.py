from datetime import date

import pytest

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
            return [(name,)]

        return get_data

    def fake_plotter(name):
        def plot(rows):
            plotted.append((name, rows))

        return plot

    for getter, plotter in REPORTS:
        monkeypatch.setattr(make_charts, getter, fake_getter(getter))
        monkeypatch.setattr(make_charts, plotter, fake_plotter(plotter))

    make_charts.main(arguments)
    assert fetched == [(getter, *expected_period) for getter, _ in REPORTS]
    assert plotted == [(plotter, [(getter,)]) for getter, plotter in REPORTS]


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

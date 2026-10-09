import math
from datetime import date
from decimal import Decimal

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure
from PIL import Image

from scripts import make_charts

PERIOD = "2026-08-10 to 2026-08-11"


@pytest.fixture
def saved_charts(monkeypatch, tmp_path):
    plt.switch_backend("Agg")
    output_dir = tmp_path / "nested" / "img"
    monkeypatch.setattr(make_charts, "OUTPUT_DIR", output_dir)
    figures = []
    original_save = Figure.savefig

    def record_save(fig, *args, **kwargs):
        original_save(fig, *args, **kwargs)
        figures.append(fig)

    monkeypatch.setattr(Figure, "savefig", record_save)
    yield output_dir, figures
    plt.close("all")


def chart_text(fig):
    return "\n".join(
        text.get_text() for text in [*fig.texts, *(text for ax in fig.axes for text in ax.texts)]
    )


@pytest.mark.parametrize(
    "plotter,filename,message",
    [
        ("plot_postings_over_time", "postings_over_time.png", "No offer observations"),
        ("plot_junior_share", "junior_share_over_time.png", "No junior observations"),
        ("plot_top_skills", "top_skills.png", "No skill data"),
        ("plot_salary_by_level", "salary_by_level.png", "No salary data"),
    ],
)
def test_empty_chart_creates_valid_image(saved_charts, plotter, filename, message):
    output_dir, figures = saved_charts
    getattr(make_charts, plotter)([], PERIOD)

    with Image.open(output_dir / filename) as picture:
        assert picture.format == "PNG"
        assert picture.width > 0 and picture.height > 0
        picture.verify()
    assert message in chart_text(figures[0])
    assert f"Period (UTC): {PERIOD}" in chart_text(figures[0])
    assert not any(ax.patches or ax.lines for ax in figures[0].axes)


def test_missing_salary_is_not_drawn_as_zero(saved_charts):
    _, figures = saved_charts
    make_charts.plot_salary_by_level([("junior", "b2b", "month", False, None, 1)], PERIOD)

    assert "No salary data" in chart_text(figures[0])
    assert not figures[0].axes[0].patches


def test_actual_zero_salary_remains_a_value(saved_charts):
    _, figures = saved_charts
    make_charts.plot_salary_by_level([("junior", "b2b", "month", False, Decimal("0"), 1)], PERIOD)

    assert len(figures[0].axes[0].patches) == 1
    assert figures[0].axes[0].patches[0].get_width() == 0
    assert "0.00 PLN/month" in chart_text(figures[0])
    assert "No salary data" not in chart_text(figures[0])


def test_daily_count_caption_describes_observations(saved_charts):
    _, figures = saved_charts
    make_charts.plot_postings_over_time(
        [(date(2026, 8, 10), 1, 0), (date(2026, 8, 11), 1, 1)], PERIOD
    )

    text = chart_text(figures[0])
    assert "N = 2 offer-day observations" in text
    assert "Without disclosed salary: 50.0%" in text
    assert figures[0].axes[0].get_ylabel() == "Offers per day"


def test_junior_share_does_not_turn_undefined_ratio_into_zero(saved_charts):
    _, figures = saved_charts
    make_charts.plot_junior_share([(date(2026, 8, 10), 0, 0), (date(2026, 8, 11), 1, 1)], PERIOD)

    ax = figures[0].axes[0]
    shares = ax.lines[0].get_ydata()
    assert math.isnan(shares[0])
    assert shares[1] == 100
    assert ax.get_ylim() == (0, 100)


def test_skill_caption_counts_offer_skill_pairs(saved_charts):
    _, figures = saved_charts
    make_charts.plot_top_skills([("python", 1), ("sql", 1)], PERIOD)

    assert "N = 2 offer-skill pairs in shown skills" in chart_text(figures[0])
    assert figures[0].axes[0].get_xlabel() == "Offers per skill"


def test_chart_output_does_not_depend_on_current_directory(saved_charts, monkeypatch, tmp_path):
    output_dir, _ = saved_charts
    other_directory = tmp_path / "other"
    other_directory.mkdir()
    monkeypatch.chdir(other_directory)

    make_charts.plot_top_skills([], PERIOD)

    assert (output_dir / "top_skills.png").exists()
    assert not (other_directory / "docs").exists()

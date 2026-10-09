import argparse
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import psycopg
from matplotlib.ticker import MaxNLocator
from psycopg.conninfo import conninfo_to_dict

from poznan_it_market import config
from poznan_it_market.config import DATABASE_URL, require_database_url

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs/img"


def get_analysis_data(
    filename: str, params: dict | None = None, *, database_url: str | None = None
):
    if params is not None:
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("start_date cannot be after end_date.")

    query_path = Path(__file__).resolve().parent.parent / "sql" / "analysis" / filename
    query = query_path.read_text(encoding="utf-8")

    url = DATABASE_URL if database_url is None else database_url

    with psycopg.connect(require_database_url(url)) as conn:
        return conn.execute(query, params).fetchall()


def get_postings_over_time_data(start_date=None, end_date=None, *, database_url: str | None = None):
    return get_analysis_data(
        "06_postings_over_time.sql",
        {"start_date": start_date, "end_date": end_date},
        database_url=database_url,
    )


def get_junior_share_data(start_date=None, end_date=None, *, database_url: str | None = None):
    return get_analysis_data(
        "07_junior_share.sql",
        {"start_date": start_date, "end_date": end_date},
        database_url=database_url,
    )


def get_top_skills_data(start_date=None, end_date=None, *, database_url: str | None = None):
    return get_analysis_data(
        "03_top_skills.sql",
        {"start_date": start_date, "end_date": end_date},
        database_url=database_url,
    )


def get_salary_by_level_data(start_date=None, end_date=None, *, database_url: str | None = None):
    return get_analysis_data(
        "05_salary_by_level.sql",
        {"start_date": start_date, "end_date": end_date},
        database_url=database_url,
    )


def save_chart(fig, filename, period, note):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.text(
        0.5,
        0.02,
        f"Period (UTC): {period}\n{note}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 0.94))
    try:
        fig.savefig(OUTPUT_DIR / filename, dpi=160, bbox_inches="tight")
    finally:
        plt.close(fig)


def show_no_data(ax, message):
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()


def format_date_axis(ax, dates):
    if len(dates) == 1:
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    else:
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def plot_postings_over_time(rows, period="Not specified"):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_title("Observed offers per day")
    total = sum(row[1] for row in rows)
    note = f"N = {total} offer-day observations"
    if not rows or total == 0:
        show_no_data(ax, "No offer observations")
    else:
        dates = [row[0] for row in rows]
        counts = [row[1] for row in rows]
        missing = sum(row[2] for row in rows)
        ax.plot(dates, counts, marker="o", color="#2563eb", linewidth=2)
        ax.set_xlabel("Date (UTC)")
        ax.set_ylabel("Offers per day")
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, linestyle="--", alpha=0.3)
        format_date_axis(ax, dates)
        note += f" · Without disclosed salary: {100 * missing / total:.1f}%"
    save_chart(fig, "postings_over_time.png", period, note)


def plot_junior_share(rows, period="Not specified"):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_title("Junior share per day")
    total = sum(row[1] for row in rows)
    note = f"N = {total} offer-day observations"
    if not rows or total == 0:
        show_no_data(ax, "No junior observations")
    else:
        dates = [row[0] for row in rows]
        shares = [100 * row[2] / row[1] if row[1] > 0 else float("nan") for row in rows]
        juniors = sum(row[2] for row in rows)
        ax.plot(dates, shares, marker="s", color="#16a34a", linewidth=2)
        ax.set_ylim(0, 100)
        ax.set_xlabel("Date (UTC)")
        ax.set_ylabel("Junior offers (%)")
        ax.grid(True, linestyle="--", alpha=0.3)
        format_date_axis(ax, dates)
        note += f" · Junior share across observations: {100 * juniors / total:.1f}%"
    save_chart(fig, "junior_share_over_time.png", period, note)


def plot_top_skills(rows, period="Not specified"):
    fig, ax = plt.subplots(figsize=(10, max(4, 0.33 * len(rows) + 1.6)))
    ax.set_title("Top 15 skills")
    total = sum(row[1] for row in rows)
    if not rows:
        show_no_data(ax, "No skill data")
    else:
        skills = [row[0] for row in rows]
        counts = [row[1] for row in rows]
        bars = ax.barh(skills, counts, color="#0284c7")
        ax.invert_yaxis()
        ax.bar_label(bars, padding=3)
        ax.set_xlim(0, max(max(counts) * 1.3, 1))
        ax.set_xlabel("Offers per skill")
        ax.set_ylabel("Skill")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_axisbelow(True)
        ax.grid(axis="x", linestyle="--", alpha=0.3)
    note = f"N = {total} offer-skill pairs in shown skills · Latest observation per offer in period"
    save_chart(fig, "top_skills.png", period, note)


def plot_salary_by_level(rows, period="Not specified"):
    groups = {}
    for level, contract, unit, is_gross, average, count in rows:
        if average is None or count <= 0:
            continue
        groups.setdefault((contract, unit, is_gross), []).append((level, average, count))

    panel_count = max(1, len(groups))
    fig, axes = plt.subplots(panel_count, 1, figsize=(9, 3 * panel_count), squeeze=False)
    if not groups:
        show_no_data(axes[0, 0], "No salary data")
    else:
        for ax, (key, values) in zip(axes[:, 0], groups.items(), strict=True):
            contract, unit, is_gross = key
            values = sorted(values, key=lambda row: row[1], reverse=True)
            labels = [f"{level} (n={count})" for level, average, count in values]
            salaries = [float(average) for level, average, count in values]
            positions = range(len(values))
            contract_label = {
                "b2b": "B2B",
                "permanent": "Employment contract",
            }.get(contract, contract)
            basis = "gross" if is_gross else "net"
            bars = ax.barh(positions, salaries, height=0.4, color="#0284c7")
            ax.set_yticks(positions, labels)
            ax.invert_yaxis()
            ax.bar_label(
                bars,
                labels=[f"{salary:,.2f} PLN/{unit}" for salary in salaries],
                padding=6,
            )
            ax.set_xlim(0, max(max(salaries) * 1.3, 1))
            ax.set_ylim(len(values) - 0.5, -0.5)
            unit_label = "Hourly" if unit == "hour" else "Monthly"
            ax.set_title(
                f"{unit_label} pay · {contract_label} · {basis}",
                loc="left",
                fontweight="bold",
            )
            ax.set_xlabel(f"PLN per {unit}")
            ax.set_axisbelow(True)
            ax.grid(axis="x", linestyle="--", alpha=0.3)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    fig.suptitle("Mean advertised minimum pay", fontsize=15)
    note = (
        "Original PLN · n = offers with a disclosed minimum"
        " · Latest observation per offer in period"
    )
    save_chart(fig, "salary_by_level.png", period, note)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate charts for an observation period.")
    parser.add_argument("--mode", choices=["live", "demo"], default="live")
    parser.add_argument("--start-date", type=date.fromisoformat, help="First UTC date, YYYY-MM-DD.")
    parser.add_argument("--end-date", type=date.fromisoformat, help="Last UTC date, YYYY-MM-DD.")
    args = parser.parse_args(argv)
    if args.start_date is not None and args.end_date is not None:
        if args.start_date > args.end_date:
            parser.error("start-date cannot be after end-date.")

    database_args = {}
    if args.mode == "demo":
        url = config.DEMO_DATABASE_URL
        if not url:
            raise ValueError("DEMO_DATABASE_URL is required for demo charts.")
        settings = conninfo_to_dict(url)
        if (
            settings.get("host") not in {"localhost", "127.0.0.1", "::1"}
            or settings.get("dbname") != "poznan_it_market_demo"
        ):
            raise ValueError("Demo charts require the local poznan_it_market_demo database.")
        for supplied_date in (args.start_date, args.end_date):
            if supplied_date is not None and supplied_date != config.DEMO_DATE:
                parser.error("Demo charts must use the saved sample date.")
        args.start_date = config.DEMO_DATE
        args.end_date = config.DEMO_DATE
        database_args["database_url"] = url

    plt.switch_backend("Agg")

    reports = [
        ("Postings over time", get_postings_over_time_data, plot_postings_over_time),
        ("Junior share", get_junior_share_data, plot_junior_share),
        ("Top skills", get_top_skills_data, plot_top_skills),
        ("Salary by level", get_salary_by_level_data, plot_salary_by_level),
    ]
    datasets = [
        get_data(args.start_date, args.end_date, **database_args) for _, get_data, _ in reports
    ]
    if not datasets[0]:
        parser.error("No offer observations in the selected period.")

    dates = [row[0] for row in datasets[0]]
    start = args.start_date or min(dates)
    end = args.end_date or max(dates)
    period = f"{start} to {end}"
    print(f"Report period (UTC): {start} to {end}")
    for (name, _, plot), rows in zip(reports, datasets, strict=True):
        print(f"Generating chart: {name}...")
        plot(rows, period)
    print("All charts generated successfully in docs/img/!")


if __name__ == "__main__":
    main()

from pathlib import Path

import matplotlib.pyplot as plt
import psycopg

from poznan_it_market.config import DATABASE_URL


def get_postings_over_time_data():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    date_id, 
                    COUNT(*), 
                    COUNT(*) FILTER (WHERE salary_from IS NULL) 
                FROM fct_offer_snapshot  
                GROUP BY date_id 
                ORDER BY date_id ASC;
                """
            )
            rows = cur.fetchall()
    return rows


def plot_postings_over_time(rows):
    dates = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    no_salaries = [r[2] for r in rows]

    total_n = sum(counts)
    total_no_salaries = sum(no_salaries)
    missing_pct = (total_no_salaries / total_n * 100) if total_n > 0 else 0.0

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(dates, counts, marker="o", color="#2563eb", linewidth=2)
    ax.set_title(f"Volume Trend (N={total_n}, Missing Salary={missing_pct:.1f}%)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Postings")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.savefig("docs/img/postings_over_time.png", bbox_inches="tight")
    plt.close(fig)


def get_junior_share_data():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    date_id, 
                    COUNT(*), 
                    COUNT(*) FILTER (WHERE experience_level = 'junior') 
                FROM fct_offer_snapshot  
                GROUP BY date_id 
                ORDER BY date_id ASC;
                """
            )
            rows = cur.fetchall()
    return rows


def plot_junior_share(rows):
    dates = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    no_juniors = [r[2] for r in rows]

    total_n = sum(counts)
    total_no_juniors = sum(no_juniors)
    daily_shares = [
        (j / c * 100) if c > 0 else 0.0 for j, c in zip(no_juniors, counts, strict=True)
    ]
    overall_share = (total_no_juniors / total_n * 100) if total_n > 0 else 0.0

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(dates, daily_shares, marker="s", color="#16a34a", linewidth=2)
    ax.set_ylim(bottom=0, top=max(daily_shares) * 1.2 if max(daily_shares) > 0 else 10)
    ax.set_title(f"Junior Postings Share Over Time (N={total_n}, Overall={overall_share:.1f}%)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Share of Postings (%)")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.savefig("docs/img/junior_share_over_time.png", bbox_inches="tight")
    plt.close(fig)


def get_top_skills_data():
    query_path = Path(__file__).resolve().parent.parent / "sql" / "analysis" / "03_top_skills.sql"
    query = query_path.read_text(encoding="utf-8")

    with psycopg.connect(DATABASE_URL) as conn:
        return conn.execute(query).fetchall()


def plot_top_skills(rows):
    skills = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    total_mentions = sum(counts)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(skills, counts, color="#0284c7")
    ax.invert_yaxis()
    ax.set_title(f"Top 15 Technologies (Offer-skill pairs in top 15={total_mentions})")
    ax.set_xlabel("Unique offers (latest observation)")
    ax.set_ylabel("Technology")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    fig.savefig("docs/img/top_skills.png", bbox_inches="tight")
    plt.close(fig)


def get_salary_by_level_data():
    query_path = (
        Path(__file__).resolve().parent.parent / "sql" / "analysis" / "05_salary_by_level.sql"
    )
    query = query_path.read_text(encoding="utf-8")

    with psycopg.connect(DATABASE_URL) as conn:
        return conn.execute(query).fetchall()


def plot_salary_by_level(rows):
    groups = {}
    for level, contract, unit, is_gross, average, count in rows:
        groups.setdefault((contract, unit, is_gross), []).append((level, average, count))

    panel_count = max(1, len(groups))
    fig, axes = plt.subplots(
        panel_count,
        1,
        figsize=(9, 3 * panel_count),
        squeeze=False,
    )

    if not groups:
        ax = axes[0, 0]
        ax.text(
            0.5,
            0.5,
            "No comparable salary data",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_axis_off()
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
            period = "Hourly" if unit == "hour" else "Monthly"
            ax.set_title(
                f"{period} pay · {contract_label} · {basis}",
                loc="left",
                fontweight="bold",
            )
            ax.set_xlabel(f"PLN per {unit}")
            ax.set_axisbelow(True)
            ax.grid(axis="x", linestyle="--", alpha=0.3)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    fig.suptitle("Mean advertised minimum pay", fontsize=15)
    fig.text(
        0.5,
        0.015,
        "Latest observation per offer · Original PLN amounts · n = offers with a minimum",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))

    output_path = Path(__file__).resolve().parent.parent / "docs/img/salary_by_level.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    print("Generating chart 1: Postings over time...")
    plot_postings_over_time(get_postings_over_time_data())

    print("Generating chart 2: Junior share over time...")
    plot_junior_share(get_junior_share_data())

    print("Generating chart 3: Top 15 skills...")
    plot_top_skills(get_top_skills_data())

    print("Generating chart 4: Salary by level...")
    plot_salary_by_level(get_salary_by_level_data())

    print("All charts generated successfully in docs/img/!")

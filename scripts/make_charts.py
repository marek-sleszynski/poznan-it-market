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
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    experience_level,
                    ROUND(AVG(salary_from)) AS avg_salary_from,
                    COUNT(*) AS total_postings,
                    COUNT(*) FILTER (WHERE salary_from IS NULL) AS missing_salaries
                FROM fct_offer_snapshot
                WHERE experience_level IS NOT NULL
                GROUP BY experience_level
                ORDER BY avg_salary_from ASC NULLS FIRST;
                """
            )
            rows = cur.fetchall()
    return rows


def plot_salary_by_level(rows):
    levels = [r[0] for r in rows]
    salaries = [float(r[1]) if r[1] is not None else 0.0 for r in rows]
    total_n = sum(r[2] for r in rows)
    total_missing = sum(r[3] for r in rows)
    missing_pct = (total_missing / total_n * 100) if total_n > 0 else 0.0

    fig, ax = plt.subplots(figsize=(8, 5))
    x_positions = range(len(levels))
    ax.bar(x_positions, salaries, color="#059669", width=0.5)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(levels)
    ax.set_title(
        f"Average Base Salary by Seniority (N={total_n}, Missing Salary={missing_pct:.1f}%)"
    )
    ax.set_xlabel("Seniority Level")
    ax.set_ylabel("Average Minimum Salary (PLN)")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.savefig("docs/img/salary_by_level.png", bbox_inches="tight")
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

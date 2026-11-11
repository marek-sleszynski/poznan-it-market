# Poznań IT Market

![CI](https://github.com/marek-sleszynski/poznan-it-market/actions/workflows/ci.yml/badge.svg)

A Python and SQL project that collects JustJoinIT offers and builds reports for Poznań.

## How it works

```mermaid
flowchart LR
    A[API or saved sample] --> B[Python: fetch and validate]
    B --> C[(PostgreSQL: JSON and import status)]
    C --> D[dbt: models and tests]
    D --> E[SQL reports]
    E --> F[Charts]
```

Stack: Python 3.14, PostgreSQL 16, dbt, Docker Compose and GitHub Actions.

## Where things are

| What | Where |
|---|---|
| Import entry point | `src/poznan_it_market/pipeline.py` (`main`) |
| API fetch and pagination | `src/poznan_it_market/ingest/justjoinit.py` (`fetch_justjoinit_pages`), `ingest/client.py` (retries) |
| Offer validation | `src/poznan_it_market/ingest/models.py` (`RawOffer`), `ingest/validation.py` (`validate_offers`) |
| Database writes | `src/poznan_it_market/ingest/loader.py` (`raw.offers`, `raw.rejected_records`, `raw.ingestion_runs`) |
| Database schema | `sql/ddl/` |
| dbt models | `dbt/models/staging/` (`stg_offers`), `dbt/models/marts/` |
| dbt data tests | `dbt/tests/` (SQL tests), `.yml` files in `dbt/models/` (column tests) |
| SQL reports | `sql/analysis/` |
| Charts | `scripts/make_charts.py`, published daily to the `charts` branch |
| CI result checks | `scripts/load_ci_fixture.py` loads `data/fixtures/ci_offers.json`, `scripts/check_results.py` compares report results |
| Daily workflow and CI | `.github/workflows/daily.yml` (daily import), `.github/workflows/ci.yml` (checks every PR) |
| Configuration | `src/poznan_it_market/config.py`, `.env.example`, `dbt/profiles.yml` |

## Local setup

You need uv, Docker Compose and Make.
On Windows, use WSL with Docker Desktop integration.

For a new setup, keep the local settings from `.env.example`:

```bash
cp .env.example .env
make install
make db-prepare
make demo
```

`make demo` loads the saved sample, builds models and creates charts in `docs/img/`.
It uses a separate local demo database. No API or Neon access is needed.
The sample date and path are defined in `src/poznan_it_market/config.py`.

For another local port, change `POSTGRES_PORT` in `.env`.

## Checks

```bash
make lint
uv run --locked mypy src
make test
```

Tests use a separate database through `TEST_DATABASE_URL`.
Use `make format` to fix formatting.

## Live collection

With the local database settings:

```bash
make migrate
make ingest
make dbt
make charts
```

These commands use `DATABASE_URL`.
GitHub Actions runs the live pipeline daily at **04:00 UTC**.
Charts are uploaded as `market-charts` after the checks pass.

## Example

[Demo chart](docs/img/demo-2026-08-11/postings_over_time.png)

The [sample](data/raw/sample/jjit_2026-08-11.json) is dated **2026-08-11**.
It contains 10 offers. The city filter keeps **5**, including **1 junior offer (20%)**.
Run `make demo` to repeat this example.

One day is not a trend. The demo image is a saved example.
Live observations start on **2026-10-09**. Old sample imports are excluded from live reports.

## Live results

![Live: daily offers](https://raw.githubusercontent.com/marek-sleszynski/poznan-it-market/charts/postings_over_time.png)

![Live: junior share over time](https://raw.githubusercontent.com/marek-sleszynski/poznan-it-market/charts/junior_share_over_time.png)

![Live: mean advertised minimum pay by level](https://raw.githubusercontent.com/marek-sleszynski/poznan-it-market/charts/salary_by_level.png)

![Live: top 15 skills](https://raw.githubusercontent.com/marek-sleszynski/poznan-it-market/charts/top_skills.png)

These charts come from the latest successful daily run.
The report period is shown below each plot.

## What the reports mean

- Daily counts show offers seen on each UTC day.
- Company, skill and salary summaries use each offer's latest observation within the selected period.
- Juniors have `experienceLevel = 'junior'`. Skills count offers mentioning each skill.
- Salaries use original PLN amounts, grouped by contract, hour/month and gross/net.
  The salary chart shows the mean advertised minimum. Missing salary is not zero.

## Limits

There is one source. Reports include top-level `city` equal to `Poznań` or `Poznan`,
including remote jobs. Other location fields are not checked.

A saved offer may no longer be active.
Salary changes show differences between observations, not the exact time of a change.

## Documentation

- [Data model](docs/data-model.md)
- [Source](docs/sources.md)
- [Data quality](docs/data-quality.md)
- [Decisions](docs/decisions.md)

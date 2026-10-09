# Lessons learned

## Starting point - 2026-08-03

I knew basic Python and university SQL, and had solved about 125 LeetCode Easy problems.
This was my first portfolio project. I had no Docker or data pipeline experience.

## Earlier version - 2026-10-06

The earlier version used incremental facts and SCD2 snapshots. Those designs were simplified
during the review. Some early imports reused the demo sample; the matching cloud observations
are marked `legacy_demo` and excluded from reports.

## What I learned

- Demo data needs a separate database and a clear observation date.
- Pagination must finish before an import is treated as complete.
- Tests should check failures, repeats and exact report results.
- Daily observations and unique offers are different counts.
- Salary comparisons need the same currency, contract, unit and gross/net basis.
- A simpler full rebuild is useful when the dataset is small.
- Documentation should describe the code that actually runs.

## Current scope

Python handles API requests, validation and database writes. dbt builds models and tests.
SQL reports share their queries with the charts. GitHub Actions runs CI and defines the daily workflow.

I have not built streaming, Spark or Airflow systems. This project uses daily batch processing.

## Next steps

Finish the walkthrough, report and clean-clone demo check. Then use the project in applications
for data internships. A second source or dashboard can be a later extension.

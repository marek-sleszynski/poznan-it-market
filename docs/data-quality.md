# Data quality

| Check | Where | Result on failure |
|---|---|---|
| API format and complete pagination | Python | Import fails before offer writes |
| API field names, ISO dates with a timezone and nonempty IDs/skills | Pydantic | Record is rejected |
| Salaries are numbers ≥ 0 with min ≤ max, and `gross` is true or false | Pydantic | Record is rejected |
| Unique offer-day and offer-day-skill rows | Database and dbt | Error |
| Required keys, company links and matching skill observations | dbt | Error |
| Salary ranges and company normalization | dbt | Error |
| Successful import for the expected day/mode, with valid counters | dbt | Error |
| At least one report offer for the expected day | dbt | Error |
| Volume below 60% of the previous seven-day average | dbt | Error |
| More than 10% rejected records | dbt | Error |
| Live data older than 26 hours | dbt freshness | Warning |
| Live data older than 48 hours, or no live data | dbt freshness | Error |
| Exact report results and date filters | `scripts/check_results.py` | Error |

The 7-day average uses only good days: the import succeeded,
the counters are valid, there are report offers and the rejection rate is 10% or less.
If there are no good days yet, only this check is skipped.

Accepted offers and rejections are saved in one transaction.
If a later write fails, the earlier writes are undone.
Failed imports save their stage and error when the database is available.
If saving the status also fails, the original error is still shown.

The daily workflow checks live freshness before the dbt build.
A warning does not stop the workflow. An error stops it, so charts are not published.

CI checks exact reports from synthetic data and runs the real demo command.
`scripts/check_results.py` checks CI and demo results.
Demo uses the sample date from Python configuration.

Tests cover retries, pagination, validation, repeat imports, rollback, reports and charts.
Database tests require `TEST_DATABASE_URL` and check the database name before clearing tables.

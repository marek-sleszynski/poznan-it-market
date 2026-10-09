# Data quality

| Check | Where | Result on failure |
|---|---|---|
| API format and complete pagination | Python | Import fails before offer writes |
| Required fields, aware dates and nonempty IDs/skills | Pydantic | Record is rejected |
| Finite, nonnegative, ordered salaries and boolean `gross` | Pydantic | Record is rejected |
| Unique offer-day and offer-day-skill rows | Database and dbt | Error |
| Required keys, company/date links and matching skill observations | dbt | Error |
| Salary ranges and company normalization | dbt | Error |
| Successful import for the expected day/mode, with valid counters | dbt | Error |
| At least one report offer for the expected day | dbt | Error |
| Volume below 60% of the previous seven-day average | dbt | Error |
| More than 10% rejected records | dbt | Error |
| Live data older than 26 hours | dbt freshness | Warning |
| Live data older than 48 hours, or no live data | dbt freshness | Error |
| Exact report results and date filters | Shared integration checker | Error |

The volume baseline uses days with successful imports, valid counters, report offers
and an acceptable rejection rate. Without a baseline, only that comparison is skipped.
Other checks still run. Thresholds can be changed through dbt variables.

Accepted offers and rejections share one transaction.
A later write failure rolls back earlier offer writes.
Failed imports save their stage and error when the database is available.
A failure while saving status must not hide the original error.

The daily workflow checks live freshness before the dbt build.
Warnings allow it to continue; errors block chart publication.

CI checks exact reports from synthetic data and runs the real demo command.
`scripts/check_results.py` checks CI and demo results.
Demo uses the sample date from Python configuration.

Tests cover retries, pagination, validation, repeat imports, rollback, reports and charts.
Database tests require `TEST_DATABASE_URL` and check the database name before clearing tables.

On 2026-09-02, a code bug caused a 94% drop in collected offers.
That was a collection failure, not a market change.

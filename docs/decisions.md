# Architecture decisions

Updated on 2026-10-09 to describe the current implementation. Original decision dates are kept.

## ADR-001 - Keep original offer JSON

**Date:** 2026-08-20 · **Status:** Accepted

**Context**
The API format can change. Raw fields are useful for debugging and rebuilding models.

**Decision**
Validate offers and keep their original JSON in `raw.offers.payload`. Save rejected records separately.

**Consequences**
- (+) Models can be rebuilt from retained observations.
- (+) Original fields remain available for debugging.
- (-) Raw history needs storage.

## ADR-002 - Use timezone-aware timestamps and UTC days

**Date:** 2026-09-06 · **Status:** Accepted

**Context**
Local dates can differ near midnight. A timestamp without a timezone can be ambiguous.

**Decision**
Require timezone-aware input and use `timestamptz` for timestamps. Use UTC for observation days.
Derive model dates with `(fetched_at AT TIME ZONE 'UTC')::date`.

**Consequences**
- (+) Raw keys and report dates use the same day.
- (+) Timestamps represent a clear point in time.
- (-) Displayed timestamps still depend on the database session timezone.

PostgreSQL stores `timestamptz` values as UTC and displays them in the session timezone.
It does not retain the original timezone name.

## ADR-003 - City filter and remote offers

**Date:** 2026-09-09 · **Status:** Accepted

**Context**
The API city filter can return listings with another top-level city.

**Decision**
Reports include top-level `city` equal to `Poznań` or `Poznan`. Keep remote offers that match.
Keep accepted offers in raw before applying this report filter.

**Consequences**
- (+) The filter is clear and matches the SQL.
- (+) Raw data remains available for other analyses.
- (-) Offers listing Poznań only in other location fields are excluded.

## ADR-004 - Same-day repeats

**Date:** 2026-09-14 · **Status:** Accepted

**Context**
An import can run more than once a day. Repeating it should not create duplicate observations.

**Decision**
Update an existing offer for the same source, offer ID and UTC day. Keep offers seen earlier that
day even if a later import does not return them. Write the full import in one transaction.

**Consequences**
- (+) Repeats are safe and do not create duplicates.
- (+) A day contains offers seen during any successful import that day.
- (-) Earlier versions from the same day are replaced.
- (-) A daily count is not the exact result of the last import.

## ADR-005 - Simple company and skill models

**Date:** 2026-09-18 · **Status:** Accepted

**Context**
The reports need company groups and skill counts. Extra dimension tables add complexity.

**Decision**
Group company names with `lower(trim(company_name))`. Store one normalized skill per offer
observation in `fct_offer_skill`. Keep the city filter in staging.

**Consequences**
- (+) Reports use simple joins and grouping.
- (+) One observation can have several deduplicated skills.
- (-) Different spellings or legal suffixes can remain separate company names.

## ADR-006 - Rebuild daily offer facts

**Date:** 2026-10-08 · **Status:** Accepted

**Context**
The incremental time filter can skip late observations and fails when the existing table is empty.
Full rebuilds were fast on the small demo dataset.

**Decision**
Use `materialized='table'` to rebuild offer facts from all retained observations.
Measure rebuild time again as the history grows.

**Consequences**
- (+) Late observations and corrections are included.
- (+) The model is simpler and matches stored source data.
- (-) Rebuild time may increase as history grows.

## ADR-007 - Keep raw history

**Date:** 2026-10-08 · **Status:** Accepted

**Context**
Models are rebuilt from raw data. Deleting observations would remove history from those models.
Cloud storage is limited.

**Decision**
Keep `raw.offers` and `raw.rejected_records`. Check size with `sql/maintenance/check_storage.sql`.
Before deleting history, create an archive and test restoring it.

**Consequences**
- (+) Models can be rebuilt from stored history.
- (+) Old observations remain available for analysis.
- (-) Storage grows and must be monitored.

## ADR-008 - GitHub Actions for daily runs

**Date:** 2026-10-02 · **Status:** Accepted

**Context**
The project needs a daily batch run and a simple place to inspect failures.

**Decision**
Use GitHub Actions for import, quality checks, dbt and charts. Queue runs for the same live
database. Upload charts only after success and keep diagnostic logs after failures.

**Consequences**
- (+) Workflow steps and logs are visible in GitHub.
- (+) One live workflow runs at a time.
- (-) Missing days cannot be reconstructed without saved observations.
- (-) Notifications depend on account settings and need to be checked.

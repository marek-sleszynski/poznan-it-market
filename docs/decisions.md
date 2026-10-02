# Architecture decisions

## ADR-01 - Why I use timestamptz for all colums 

**Date:** 2026-09-06 · **Status:** Accepted

**Context**
Having dates without timezones can lead to bugs when e.g. if someone create an offer at "14:00" in Poland, the database cannot tell in which country it's time

**Decision**
Always use 'timestamptz' instead of 'timestamp' across all database tables.

**Consequences**
- (+) SQL standardizes for all timestamps to UTC.
- (+) Eliminates misses when converting to local timezones. 

## ADR-02 - Primary location and remote offers

**Date:** 2026-09-09 · **Status:** Accepted

**Context**
Searching for 'city=Poznan' can return postings outside of Poznań, not just local. In my sample 50% of offers are from other city, and 70% are remote. Without the primary location filter it would falsify the statistic.

**Decision** 
Filter job postings by primary location `locations[0].city == 'Poznań'`. Keep postings only if primary location is Poznań (even if remote).

**Consequences**
- (+) Eliminates misleading information from other city postings.
- (+) Gives more reliable market information in Poznań.
- (-) Throws away around 50% of postings returned by raw API during staging.

## ADR-003 - Same-day re-run strategy

**Date:** 2026-09-14 · **Status:** Accepted

**Context**
Pipeline can run more than once a day. If a network issue causes pipeline to stop, I might need to rerun it manually. Table raw.offers does not allow duplicates. We need to decide what to do if we see the same offer- reject the new offer or update it.

**Decision**
Overwrite existing records.

**Consequences**
- (+) Updated version is the latest version and the most accurate.
- (+) If pipeline goes wrong I can rerun it easly to update the data.
- (-) Updating it (in larger numbers) is less efficient than ignoring duplicates.
- (-) We lose data from the primary unupdated offer (date and id).

## ADR-004 - Updating daily snapshot tables

**Date:** 2026-09-26 · **Status:** Accepted

**Context**
Rebuilding fully fact table is too slow and expensive.

**Decision**
Add new data each day only using a date filter `materialized='incremental'` with key on `unique_key=['date_id', 'raw_offer_id']` with filtering on `fetched_at`. 

**Consequences**
- (+) Much faster performance and lower costs for the table growing over time
- (-) Risks of missing data or older rows not matching with updated structure so we need to fully rebuild once a week with `--full-refresh` to fix data. 

## ADR-005 - Keeping raw data under 0.5gb cloud storage limit

**Date:** 2026-09-29 · **Status:** Accepted

**Context**
Cloud- Neon's free plan gives us 0.5gb of storage. Daily raw data takes up to 1,2 mb. Neon's space will run out out in about 400 days.

**Decision**
Keeping raw data for 30 days from `raw.offers` and `raw.rejected_records` using `sql/maintenance/prune_raw.sql` can allow us enough time to turn it into business logic we're interested in and catch bugs.

**Consequences**
- (+) Cloud size limit stays in the free limit.
- (+) We have access to data from the last 30 days.
- (-) Raw data older than 30 days cannot be turned into data business logic if buisness logic chaned.

## ADR-006 - Github Actons for pipeline automation

**Date:** 2026-10-02 · **Status:** Accepted

**Context**
I need to run pipeline daily in order to keep offers updated (~300 offers per day). I need to decide whether to use Airflow, Github Actions or cron.

**Decision**
Github actions is the most suitable for the project. I run it only ~3 minutes per day. It is costless, simple and does not need to run on servers in comparision to other options.

**Consequences**
- (+) Zero cost
- (+) Simpler because of lack of servers
- (+) Emails in case of malfunction
- (-) No backfill
- (-) No task-level retries in case of malfunction
- (-) No DAG

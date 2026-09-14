# Architecture decisions

### ADR-1 - Why I use timestamptz for all colums 

**Date:** 2026-09-06 · **Status:** Accepted

**Context**
Having dates without timezones can lead to bugs when e.g. if someone create an offer at "14:00" in Poland, the database cannot tell in which country it's time

**Decision**
Always use 'timestamptz' instead of 'timestamp' across all database tables.

**Consequences**
- (+) SQL standardizes for all timestamps to UTC.
- (+) Eliminates misses when converting to local timezones. 

### ADR-2 - Primary location and remote offers

**Date:** 2026-09-09 · **Status:** Accepted

**Context**
Searching for 'city=Poznan' can return postings outside of Poznań, not just local. In my sample 50% of offers are from other city, and 70% are remote. Without the primary location filter it would falsify the statistic.

**Decision** 
Filter job postings by primary location `locations[0].city == 'Poznań'`. Keep postings only if primary location is Poznań (even if remote).

**Consequences**
- (+) Eliminates misleading information from other city postings.
- (+) Gives more reliable market information in Poznań.
- (-) Throws away around 50% of postings returned by raw API during staging.

### ADR-3 - Same-day re-run strategy

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

# Architecture decisions

### ADR-1- Why I use timestamptz for all colums 

**Date: 2026-09-06** · **Status:** Accepted

**Context**
Having dates without timezones can lead to bugs when e.g. if someone create an offer at "14:00" in Poland, the database cannot tell in which country it's time

**Decision**
Always use 'timestamptz' instead of 'timestamp' across all database tables.

**Consequences**
- (+) SQL standardizes for all timestamps to UTC.
- (+) Eliminates misses when converting to local timezones. 

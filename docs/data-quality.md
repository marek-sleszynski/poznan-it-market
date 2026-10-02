# Data Quality

## Tests & Rationale

| Test | Layer | Rule | Action | Why |
|---|---|---|---|---|
| Freshness | `raw` | `max(fetched_at)` < 26h | warn | Data is delayed or stopped loading |
| Completeness | `marts` | Daily count > 60% of 7d avg | **halt (error)** | Catch API format changes or empty loads |
| Uniqueness | `staging` | Unique `(source, source_offer_id, date)` | error | Prevent duplicates and keeps idempotency |
| Integrity | `marts` | Company exists in `dim_company` | error | Prevents broken links between tables |

## Warn vs Error Policy

Rule: **Halt the pipeline only when data would be misleading.**

* **Warning (`warn`):** Data is incomplete or delayed, but reports are still useful.
* **Error (`halt`):** Structural corruption or massive data loss (>40% drop). Publishing this would show a fake market crash on the dashboard.

## Past incidents

| Date | Incident | Caught By | Resolution |
|---|---|---|---|
| 2026-09-02 | Postings dropped by 94% | Completeness test | API payload format changed- updated the parser |

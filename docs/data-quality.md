# Data quality

## Import checks

The import checks API structure, pagination and offer fields before writing data.
Rejected records are saved with their errors. Accepted offers and rejections are written in one
transaction. Failed imports record their stage and error when the database is available.

## Report checks

| Check | Rule | Result |
|---|---|---|
| Live freshness | Latest live observation is older than 26 hours | Warning |
| Live freshness | Latest live observation is older than 48 hours, or none exists | Error |
| Daily import | Latest attempt for the expected UTC day and mode must finish successfully with valid counters and accepted offers | Error |
| Daily report | At least one report offer must exist for the expected day | Error |
| Offer volume | Daily count below 60% of the previous seven-day average | Error |
| Rejections | More than 10% of fetched records are rejected | Error |
| Offer grain | Unique `(source, source_offer_id, date_id)` in offer facts | Error |
| Skill grain | Unique offer-day-skill; required fields and valid observation links | Error |
| Company and date links | Fact keys must exist in their dimensions | Error |
| Salaries | No negative, non-finite or reversed salary ranges | Error |
| Companies | Normalized name and hash must match the model rule | Error |

The volume baseline uses only days whose latest import finished successfully, with valid counters,
report offers and an acceptable rejection rate. If no valid baseline exists, that comparison is skipped.
The other checks still run. Thresholds can be changed through dbt variables.

## When reports are published

The daily workflow runs live freshness separately, then builds models and runs dbt tests.
Warnings allow the workflow to continue. Errors block chart publication.
Generated charts are uploaded only after a successful run.

Demo and CI builds use an explicit expected date. CI loads synthetic data before the dbt build
and checks the exact report results.

## Past incident

On 2026-09-02, a bug in my code caused a 94% drop in the number of offers.
The drop came from my code and should not be read as a change in the market.

# Data source

The project uses job offers from JustJoinIT.

## API and pagination

API response checked on 2026-10-09.

Endpoint: `https://justjoin.it/api/candidate-api/offers`

- Start with `city=Poznań`, `cityRadius=0` and `from=0`.
- Read offers from `data` and send `meta.next.cursor` as the next `from` value.
- Stop when `meta.from + len(data)` reaches `meta.totalItems`. The API may return a non-null cursor at the end.
- If `totalItems` is missing, stop when the next cursor is `null`.
- Wait two seconds between pages. Use the shared HTTP client and retries.
- Fail on an invalid response, repeated cursor or incomplete download at the 500-page limit.

## Report scope

- Raw data keeps accepted offers before the city filter.
- Reports include top-level `city` equal to `Poznań` or `Poznan`, including remote jobs.
- All experience levels are included. The junior measure counts only `experienceLevel = 'junior'`.
- Titles are not used to detect internships or trainee roles.
- Offers are identified by `(source, source_offer_id)`, where `source_offer_id` is the slug.
- Different slugs are separate offers; similar job titles are not merged.

## Important details

- Missing salary is not zero. Salary reports use original PLN variants.
- Keep timezone information in timestamps. Observation days use UTC.
- JSON keys such as `from` use aliases in Python models.
- Demo data uses a saved sample and its original observation date.

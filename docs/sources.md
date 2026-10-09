# Source

JustJoinIT endpoint: `https://justjoin.it/api/candidate-api/offers`.

The response format was checked on 2026-10-09. It may change.

## Pagination

- Start with `city=Poznań`, `cityRadius=0` and `from=0`.
- Read `data`; use `meta.next.cursor` as the next `from`.
- Stop when `meta.from + len(data)` reaches `meta.totalItems`.
- Without `totalItems`, stop when the next cursor is `null`.
- Wait two seconds between pages. The HTTP client retries temporary failures.
- Invalid responses, repeated cursors or an incomplete download at 500 pages fail the import.

All pages must finish before offers are saved.

## Scope and limits

Accepted raw offers are kept before the city filter.
Reports include top-level `city` equal to `Poznań` or `Poznan`, including remote jobs.
Offers listing Poznań only in other location fields are excluded.

Juniors require `experienceLevel = 'junior'`. Titles are not used to detect trainee roles.
Source and slug identify an offer. Different slugs remain separate offers.

This is one provider's listings, not the whole local job market.
A saved observation does not prove that an offer is still active.

Observation days use UTC. Publication dates must include a timezone.
Salary reports use original PLN variants and keep missing values.
The demo uses the saved sample dated 2026-08-11, not current market data.

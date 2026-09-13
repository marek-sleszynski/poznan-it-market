## First observations
- Offers `candidate-api/offers` has a city filter, but still returns remote jobs. I will need to filter by primary city later.
- I only use "city", "cityRadius", "sortBy", "orderBy" in my requests. I skip 'isPromoted=true' because it returns only paid listings, not the full set of postings.
- `publishedAt` is in UTC. The format is `YYYY-MM-DDTHH:MM:SS.ffffffZ`- I will need to change timezone conversion for local-time reporting.

## Gotchas
**The city filter returns companies outside of Poznań**
- 50% postings are primarly in other cities. To only get local offers `locations[0].city` must be used.
**Paging past the end causes a 500 error**
- Requesting pages beyond last result (from=99999) crashes the server with an 500 error insted of returning an empty list. Always stop the loop when meta.next.cursor is null or meta.next.itemsCount == 0.
**No rate limit warnings**
- The api does not return rare limit headers like. To avoid IP bans, slow down request to 1 every 2 seconds and set cutom User-Agent.

## First observations
- Minimum and maximum wages are often null.
- `publishedAt` include "Z", python will raise an error.
- API uses `from` as a important phrase in python. It will raise an error.

## Gotchas
**Null in salary ranges**
- Always check `is not None` before using them to avoid error.
**ISO timestamps**
- Always use `datetime.now(timezone.utc)` when using from `publishedAt`.
**Reserved word in python**
- Always use `validation_alias="from"` to avoid `from` conflicts with python.

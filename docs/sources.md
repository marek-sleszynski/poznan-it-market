## First observations
- Offers `candidate-api/offers` has a city filter, but still returns remote jobs. I will need to filter by primary city later.
- I only use "city", "cityRadius", "sortBy", "orderBy" in my requests. I skip 'isPromoted=true' because it returns only paid listings, not the full set of postings.
- `publishedAt` is in UTC. The format is `YYYY-MM-DDTHH:MM:SS.ffffffZ`- I will need to change timezone conversion for local-time reporting.

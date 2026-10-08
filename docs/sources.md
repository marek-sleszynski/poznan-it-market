# Data source

The project uses job offers from Just Join IT.

## API and pagination

Checked on 2026-10-06.

Endpoint: `https://justjoin.it/api/candidate-api/offers`

- Use `city=Poznań`, `cityRadius=0` and `from=0` for the first request.
- Offers are in the `data` array.
- Send `meta.next.cursor` as `from` to get the next page.
- Stop when the next cursor is `null`.
- Wait two seconds between requests and use a custom User-Agent.
- Fail on an invalid response, a repeated cursor or the page limit.
- The default limit is 500 pages. Reaching it with more pages available means the import is incomplete.

## Data limits

- Includes jobs where the primary city is Poznań (or Poznan), including remote roles.
- Excludes jobs where Poznań is only listed as an additional or secondary location.
- Counts raw job posts, without removing duplicates across cities.
- Only tracks offers tagged as "junior" (it does not detect internships written in job titles).
- Includes offers from all experience levels.
- Salary values can be `null`. Missing salary is not zero.
- A timestamp ending in `Z` uses UTC. Keep timezone information when parsing it.
- JSON can use the key `from`. In Python models, use another field name with an alias.
- Demo data comes from a saved sample. Loading it today does not make it current market data.

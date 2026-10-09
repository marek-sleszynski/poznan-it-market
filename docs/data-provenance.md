# Data sources

Each raw offer has a `data_mode`:

- `live`: data from the API.
- `demo`: data from the saved sample.
- `legacy_demo`: old imports of the sample.
- `unknown`: the source is not confirmed.

We checked 30 historical rows in Neon. All matched the saved sample, so we marked them as `legacy_demo`. We kept the rows and their timestamps.

The staging model uses only `live` data by default. To use sample data, set `data_mode` to `demo`.

Local checks passed: staging returned 0 live rows and 5 demo rows.

Existing tables built from the old data still need to be checked before publishing results.

## Repeated imports

We keep one observation per offer per UTC day.

Another import on the same day updates the offer with the latest fetched data. Offers missing from that import stay in the database.

An import on the next day creates a new observation.

Daily counts show offers seen during the day. They do not show how many offers were active at the same time.

## Offer counts

Daily charts count offers seen on each UTC day.

Company, skill and salary disclosure summaries count unique offers across the stored history, using each offer's latest observation. An offer is identified by its source and source offer ID.

The latest observation does not mean the offer is still active.

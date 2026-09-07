DROP TABLE IF EXISTS raw.offers;

CREATE OR REPLACE FUNCTION raw.to_date_utc(timestamptz) 
RETURNS date AS $$
    SELECT ($1 AT TIME ZONE 'UTC')::date;
$$ LANGUAGE sql IMMUTABLE;

CREATE TABLE raw.offers (
    id bigserial PRIMARY KEY,
    source text NOT NULL,
    source_offer_id text NOT NULL,
    payload jsonb NOT NULL,
    fetched_at timestamptz NOT NULL,
    run_id uuid NOT NULL
);

-- one posting per calendar day.
CREATE UNIQUE INDEX offers_natural_key 
ON raw.offers (source, source_offer_id, (raw.to_date_utc(fetched_at)));

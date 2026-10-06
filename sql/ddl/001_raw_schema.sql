CREATE SCHEMA IF NOT EXISTS raw;

CREATE OR REPLACE FUNCTION raw.to_date_utc(timestamptz)
RETURNS date AS $$
    SELECT ($1 AT TIME ZONE 'UTC')::date;
$$ LANGUAGE sql IMMUTABLE;

CREATE TABLE IF NOT EXISTS raw.offers (
    id bigserial PRIMARY KEY,
    source text NOT NULL,
    source_offer_id text NOT NULL,
    payload jsonb NOT NULL,
    fetched_at timestamptz NOT NULL,
    run_id uuid NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS offers_natural_key
ON raw.offers (source, source_offer_id, (raw.to_date_utc(fetched_at)));

ALTER TABLE raw.ingestion_runs
    ADD COLUMN IF NOT EXISTS data_mode text NOT NULL DEFAULT 'unknown'
        CHECK (data_mode IN ('unknown', 'demo', 'live')),
    ADD COLUMN IF NOT EXISTS observed_date date;

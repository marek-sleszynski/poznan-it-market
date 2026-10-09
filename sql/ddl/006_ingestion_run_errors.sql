ALTER TABLE raw.ingestion_runs
    ADD COLUMN IF NOT EXISTS stage text,
    ADD COLUMN IF NOT EXISTS error_type text,
    ADD COLUMN IF NOT EXISTS error_message text;

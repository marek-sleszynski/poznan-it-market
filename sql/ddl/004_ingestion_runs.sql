CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
    run_id uuid PRIMARY KEY,
    started_at timestamptz NOT NULL,
    finished_at timestamptz,
    pages_fetched int,
    records_accepted int,
    records_rejected int,
    status text NOT NULL,
    stage text,
    error_type text,
    error_message text,
    data_mode text NOT NULL DEFAULT 'unknown'
        CHECK (data_mode IN ('unknown', 'demo', 'live')),
    observed_date date
);

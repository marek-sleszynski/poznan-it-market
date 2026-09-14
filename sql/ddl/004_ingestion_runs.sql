CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
    run_id uuid PRIMARY KEY,
    started_at timestamptz NOT NULL,
    finished_at timestamptz,
    pages_fetched int,
    records_accepted int,
    records_rejected int,
    status text NOT NULL
);

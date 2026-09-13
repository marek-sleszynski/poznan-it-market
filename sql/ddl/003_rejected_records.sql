CREATE TABLE IF NOT EXISTS raw.rejected_records (
    id bigserial PRIMARY KEY,
    payload jsonb NOT NULL,
    error_type text NOT NULL,
    error_message text NOT NULL,
    rejected_at timestamptz NOT NULL DEFAULT now(),
    run_id uuid NOT NULL
);

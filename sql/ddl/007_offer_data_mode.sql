ALTER TABLE raw.offers
    ADD COLUMN IF NOT EXISTS data_mode text NOT NULL DEFAULT 'unknown'
    CHECK (data_mode IN ('unknown', 'live', 'demo', 'legacy_demo'));

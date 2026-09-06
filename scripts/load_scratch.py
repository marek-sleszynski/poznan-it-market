import json
import os

import psycopg
from psycopg.types.json import Jsonb

SAMPLE_PATH = "data/raw/sample/jjit_2026-08-11.json"
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://poznan_it_market:Marek3cc@localhost:5432/poznan_it_market"
)


def load_sample():
    print(f"Reading sample from {SAMPLE_PATH}...")
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        raw_data = json.load(f)

    offers = raw_data.get("data", [])
    print(f"Found {len(offers)} offers in sample.")
    print("Connecting to database...")

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # 1. Tworzymy schemat i tabelę roboczą
            cur.execute("""
                CREATE SCHEMA IF NOT EXISTS scratch;
                CREATE TABLE IF NOT EXISTS scratch.offers_sample (
                    id serial PRIMARY KEY,
                    payload jsonb NOT NULL,
                    fetched_at timestamptz NOT NULL DEFAULT now()
                );
            """)

            # 2. Hurtowe wstawianie ofert
            if offers:
                records = [(Jsonb(offer),) for offer in offers]
                cur.executemany("INSERT INTO scratch.offers_sample (payload) VALUES (%s);", records)

    print("Done! Data successfully loaded into scratch.offers_sample.")


if __name__ == "__main__":
    load_sample()

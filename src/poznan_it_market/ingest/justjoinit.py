import json
import time
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import httpx

from poznan_it_market.ingest.client import fetch_url_with_retry, get_http_client

JUSTJOINIT_API_URL = "https://api.justjoin.it/v2/user-panel/offers"


def fetch_justjoinit_pages(
    client: httpx.Client, city: str = "poznan", max_pages: int | None = None
) -> Iterator[dict]:
    page = 1
    while True:
        params = {"page": page, "perPage": 100, "city": city}
        response = fetch_url_with_retry(client, JUSTJOINIT_API_URL, params=params)
        payload = response.json()

        offers = payload.get("data", [])
        if not offers:
            break

        yield payload

        meta = payload.get("meta", {})
        total_pages = meta.get("totalPages", 1)

        if page >= total_pages:
            break
        if max_pages is not None and page >= max_pages:
            break

        time.sleep(2.0)
        page += 1


def save_raw_pages(pages: Iterator[dict], target_date: str | None = None) -> list[Path]:
    if target_date is None:
        target_date = date.today().isoformat()

    output_dir = Path("data/raw") / target_date
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    for page_num, page_data in enumerate(pages, start=1):
        file_path = output_dir / f"page_{page_num:03d}.json"
        file_path.write_text(
            json.dumps(page_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        saved_paths.append(file_path)

    return saved_paths


def fetch_and_save(city: str = "poznan", max_pages: int | None = None) -> list[Path]:
    client = get_http_client()
    pages = fetch_justjoinit_pages(client=client, city=city, max_pages=max_pages)
    return save_raw_pages(pages)

if __name__ == "__main__":
    fetch_and_save()

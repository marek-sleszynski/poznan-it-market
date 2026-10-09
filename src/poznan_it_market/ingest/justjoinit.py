import json
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import httpx

from poznan_it_market.config import JJIT_API_URL
from poznan_it_market.ingest.client import fetch_url_with_retry, get_http_client


def fetch_justjoinit_pages(
    client: httpx.Client, city: str = "Poznań", max_pages: int = 500
) -> Iterator[dict]:
    if max_pages < 1:
        raise ValueError("max_pages must be positive.")

    cursor = 0
    seen_cursors = {cursor}

    for page_number in range(1, max_pages + 1):
        params = {"city": city, "cityRadius": 0, "from": cursor}
        response = fetch_url_with_retry(client, JJIT_API_URL, params=params)
        payload = response.json()

        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ValueError("Invalid API response: data must be a list.")

        meta = payload.get("meta")
        if not isinstance(meta, dict) or meta.get("from") != cursor:
            raise ValueError("Invalid API response: unexpected page position.")

        next_page = meta.get("next")
        if not isinstance(next_page, dict) or "cursor" not in next_page:
            raise ValueError("Invalid API response: missing next cursor.")

        next_cursor = next_page["cursor"]
        if next_cursor is not None:
            if type(next_cursor) is not int or next_cursor < 0:
                raise ValueError("Invalid API response: unsupported cursor.")
            if next_cursor in seen_cursors:
                raise ValueError("API returned a repeated cursor.")
            if page_number == max_pages:
                raise RuntimeError("Page limit reached before import completed.")

        yield payload

        if next_cursor is None:
            return

        seen_cursors.add(next_cursor)
        cursor = next_cursor
        time.sleep(2.0)


def save_raw_pages(pages: Iterator[dict], target_date: str | None = None) -> list[Path]:
    if target_date is None:
        target_date = datetime.now(UTC).date().isoformat()

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


def fetch_and_save(city: str = "Poznań", max_pages: int = 500) -> list[Path]:
    with get_http_client() as client:
        pages = fetch_justjoinit_pages(client, city=city, max_pages=max_pages)
        return save_raw_pages(pages)


if __name__ == "__main__":
    fetch_and_save()

import time
from collections.abc import Iterator

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

        page_end = cursor + len(payload["data"])
        reached_end = False
        has_total = "totalItems" in meta
        if has_total:
            total_items = meta["totalItems"]
            if type(total_items) is not int or total_items < 0:
                raise ValueError("Invalid API response: unsupported totalItems.")
            if page_end > total_items:
                raise ValueError("Invalid API response: page exceeds totalItems.")
            reached_end = page_end == total_items
            if not payload["data"] and not reached_end:
                raise ValueError("Invalid API response: empty page before totalItems.")

        next_cursor = next_page["cursor"]
        if next_cursor is not None:
            if type(next_cursor) is not int or next_cursor < 0:
                raise ValueError("Invalid API response: unsupported cursor.")
            # The API repeats the cursor on an empty page at the end.
            empty_end = reached_end and not payload["data"] and next_cursor == cursor
            if next_cursor in seen_cursors and not empty_end:
                raise ValueError("API returned a repeated cursor.")
            if has_total and next_cursor != page_end:
                raise ValueError("Invalid API response: unexpected next cursor.")
        elif has_total and not reached_end:
            raise ValueError("API ended before totalItems was reached.")

        if not reached_end and next_cursor is not None and page_number == max_pages:
            raise RuntimeError("Page limit reached before import completed.")

        yield payload

        if reached_end or next_cursor is None:
            return

        seen_cursors.add(next_cursor)
        cursor = next_cursor
        time.sleep(2.0)


def read_live_offers() -> tuple[list[dict], int]:
    offers: list[dict] = []
    pages_fetched = 0

    with get_http_client() as client:
        for page in fetch_justjoinit_pages(client):
            offers.extend(page["data"])
            pages_fetched += 1

    return offers, pages_fetched

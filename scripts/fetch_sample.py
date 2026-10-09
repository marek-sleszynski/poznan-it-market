import json
from datetime import UTC, datetime
from pathlib import Path

from poznan_it_market.ingest.client import get_http_client
from poznan_it_market.ingest.justjoinit import fetch_justjoinit_pages


def main():
    # Save the first page after checking its response structure.
    with get_http_client() as client:
        data = next(fetch_justjoinit_pages(client))

    current_date = datetime.now(UTC).date().isoformat()
    file_path = Path("data/raw/sample") / f"jjit_{current_date}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

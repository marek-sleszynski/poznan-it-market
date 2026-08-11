import datetime
import json

import httpx

from poznan_it_market.config import JJIT_API_URL


def main():
    header = {"User-Agent": "marek-portfolio-bot (kontakt: mareksles@gmail.com)"}
    params = {"city": "Poznań", "cityRadius": 0, "sortBy": "publishedAt", "orderBy": "descending"}
    response = httpx.get(JJIT_API_URL, headers=header, params=params)

    response.raise_for_status()

    data = response.json()

    current_date = datetime.date.today().strftime("%Y-%m-%d")
    file_name = f"data/raw/sample/jjit_{current_date}.json"

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()

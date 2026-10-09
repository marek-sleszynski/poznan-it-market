def remove_polish_diacritics(normalized: str) -> str:
    characters = {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
    }
    new_normalized = ""

    for char in normalized.lower():
        if char in characters:
            new_normalized += characters[char]
        else:
            new_normalized += char

    return new_normalized


def normalize_company_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    normalized = name.lower()
    normalized = normalized.replace(" ", "")
    normalized = normalized.replace(",", "")
    normalized = normalized.replace(".", "")
    normalized = normalized.removesuffix("spzoo")
    normalized = normalized.removesuffix("sa").strip()
    return normalized


def parse_salary(employment_types: list) -> tuple[int | None, int | None, str | None]:
    if not employment_types:
        return None, None, None
    for element in employment_types:
        if element["currency"] == "PLN":
            return element["from"], element["to"], element["type"]
    return employment_types[0]["from"], employment_types[0]["to"], employment_types[0]["type"]


def is_main_location(offer: dict, city: str) -> bool:
    normalized_offer = remove_polish_diacritics(offer["city"]).strip()
    normalized_city = remove_polish_diacritics(city).strip()
    return normalized_offer == normalized_city

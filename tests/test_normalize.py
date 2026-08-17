import pytest

from poznan_it_market.transform.normalize import (
    is_main_location,
    normalize_company_name,
    parse_salary,
    remove_polish_diacritics,
)


@pytest.mark.parametrize(
    "company_name, expected",
    [("Allegro sp. z o.o.", "allegro"), ("PGE S.A.", "pge"), ("", ""), (None, "")],
)
def test_normalize_company_name(company_name, expected):
    assert normalize_company_name(company_name) == expected


@pytest.mark.parametrize(
    "employment_types, expected",
    [
        (
            [{"from": 10000, "to": 15000, "type": "permanent", "currency": "PLN"}],
            (10000, 15000, "permanent"),
        ),
        ([{"from": None, "to": None, "type": "b2b", "currency": "CHF"}], (None, None, "b2b")),
        ([], (None, None, None)),
        (None, (None, None, None)),
    ],
)
def test_parse_salary(employment_types, expected):
    assert parse_salary(employment_types) == expected


@pytest.mark.parametrize(
    "city_name, expected", [("Poznań", "poznan"), ("Łódź", "lodz"), ("poznan", "poznan")]
)
def test_remove_polish_diacritics(city_name, expected):
    assert remove_polish_diacritics(city_name) == expected


@pytest.mark.parametrize(
    "offer, city, expected",
    [
        ({"city": "Poznań"}, "poznan", True),
        ({"city": "Poznań"}, "Poznań", True),
        ({"city": "Poznań"}, "poznań", True),
        ({"city": "Warszawa"}, "Poznań", False),
    ],
)
def test_is_main_location(offer, city, expected):
    assert is_main_location(offer, city) == expected

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from poznan_it_market.ingest.models import EmploymentType, RawOffer


@pytest.fixture
def offer_payload():
    return {
        "slug": "dev",
        "title": "Python Developer",
        "companyName": "Corp",
        "city": "Poznań",
        "publishedAt": "2026-08-11T10:00:00.000Z",
        "employmentTypes": [
            {
                "fromPerUnit": 10000,
                "toPerUnit": 18000,
                "gross": False,
                "unit": "month",
                "currency": "PLN",
                "currencySource": "original",
                "type": "b2b",
            }
        ],
    }


def test_raw_offer_valid(offer_payload):
    offer = RawOffer.model_validate(offer_payload)

    assert offer.slug == "dev"
    assert offer.company_name == "Corp"
    assert len(offer.employment_types) == 1
    employment = offer.employment_types[0]
    assert employment.salary_from_per_unit == Decimal("10000")
    assert employment.salary_to_per_unit == Decimal("18000")
    assert employment.gross is False
    assert employment.unit == "month"
    assert employment.currency == "PLN"
    assert employment.currency_source == "original"
    assert employment.type == "b2b"


def test_raw_offer_requires_api_company_name(offer_payload):
    offer_payload["company_name"] = offer_payload.pop("companyName")

    with pytest.raises(ValidationError, match="companyName"):
        RawOffer.model_validate(offer_payload)


def test_raw_offer_future_date_rejected(offer_payload):
    offer_payload["publishedAt"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    with pytest.raises(ValidationError):
        RawOffer.model_validate(offer_payload)


def test_employment_type_salary_order():
    with pytest.raises(ValidationError):
        EmploymentType.model_validate({"fromPerUnit": 25000, "toPerUnit": 15000})


@pytest.mark.parametrize("field", ["fromPerUnit", "toPerUnit"])
@pytest.mark.parametrize(
    "value",
    [
        -1,
        float("inf"),
        float("-inf"),
        float("nan"),
        "not-a-number",
        "",
        "12_000",
        "١٢٣",
        True,
        False,
    ],
)
def test_employment_type_rejects_invalid_salary(field, value):
    with pytest.raises(ValidationError):
        EmploymentType.model_validate({field: value})


@pytest.mark.parametrize(
    "payload, expected_from, expected_to",
    [
        ({}, None, None),
        ({"fromPerUnit": None, "toPerUnit": None}, None, None),
        ({"fromPerUnit": 0}, Decimal("0"), None),
        ({"toPerUnit": 18000}, None, Decimal("18000")),
        (
            {"fromPerUnit": 12345.67, "toPerUnit": 18000},
            Decimal("12345.67"),
            Decimal("18000"),
        ),
        (
            {"fromPerUnit": "12345.67", "toPerUnit": "18000"},
            Decimal("12345.67"),
            Decimal("18000"),
        ),
        (
            {"fromPerUnit": 10000, "toPerUnit": 10000},
            Decimal("10000"),
            Decimal("10000"),
        ),
    ],
)
def test_employment_type_accepts_per_unit_salary(payload, expected_from, expected_to):
    employment = EmploymentType.model_validate(payload)

    assert employment.salary_from_per_unit == expected_from
    assert employment.salary_to_per_unit == expected_to


@pytest.mark.parametrize("value", [True, False, None])
def test_employment_type_accepts_gross(value):
    employment = EmploymentType.model_validate({"gross": value})
    assert employment.gross is value


@pytest.mark.parametrize("value", ["true", "false", "unknown", "", 0, 1, [], {}])
def test_employment_type_rejects_invalid_gross(value):
    with pytest.raises(ValidationError):
        EmploymentType.model_validate({"gross": value})


def test_employment_type_accepts_missing_salary():
    employment = EmploymentType.model_validate({})

    assert employment.salary_from_per_unit is None
    assert employment.salary_to_per_unit is None
    assert employment.gross is None


def test_employment_type_accepts_foreign_currency():
    employment = EmploymentType.model_validate({"fromPerUnit": 500, "currency": "USD"})

    assert employment.salary_from_per_unit == Decimal("500")
    assert employment.currency == "USD"


@pytest.mark.parametrize("slug", ["", " ", "\t", None])
def test_raw_offer_rejects_empty_slug(offer_payload, slug):
    offer_payload["slug"] = slug

    with pytest.raises(ValidationError):
        RawOffer.model_validate(offer_payload)


@pytest.mark.parametrize(
    "skills",
    [{}, ["Python"], [{}], [{"name": ""}], [{"name": " "}]],
)
def test_raw_offer_rejects_invalid_skills(offer_payload, skills):
    offer_payload["requiredSkills"] = skills

    with pytest.raises(ValidationError):
        RawOffer.model_validate(offer_payload)


@pytest.mark.parametrize(
    "published_at",
    ["2026-08-11T10:00:00", 1700000000, "1700000000"],
)
def test_raw_offer_rejects_invalid_publication_date(offer_payload, published_at):
    offer_payload["publishedAt"] = published_at

    with pytest.raises(ValidationError, match="timezone"):
        RawOffer.model_validate(offer_payload)


def test_raw_offer_accepts_date_with_offset(offer_payload):
    offer_payload["publishedAt"] = "2026-08-11T10:00:00+02:00"

    offer = RawOffer.model_validate(offer_payload)

    assert offer.published_at.astimezone(UTC) == datetime(2026, 8, 11, 8, tzinfo=UTC)


def test_raw_offer_accepts_missing_salary(offer_payload):
    offer_payload.pop("employmentTypes")

    offer = RawOffer.model_validate(offer_payload)

    assert offer.employment_types == []

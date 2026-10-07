from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from poznan_it_market.ingest.models import EmploymentType, RawOffer


def test_raw_offer_valid():
    payload = {
        "slug": "dev",
        "title": "Python Developer",
        "companyName": "Corp",
        "city": "Poznań",
        "publishedAt": "2026-08-11T10:00:00.000Z",
        "employmentTypes": [{"from": 10000, "to": 18000, "type": "b2b"}],
    }
    offer = RawOffer.model_validate(payload)

    assert offer.slug == "dev"
    assert offer.company_name == "Corp"
    assert len(offer.employment_types) == 1
    assert offer.employment_types[0].salary_from == 10000


def test_raw_offer_future_date_rejected():
    payload = {
        "slug": "test",
        "title": "Dev",
        "companyName": "Corpo",
        "publishedAt": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
    }

    with pytest.raises(ValidationError):
        RawOffer.model_validate(payload)


def test_employment_type_salary_order():
    with pytest.raises(ValidationError):
        EmploymentType.model_validate({"from": 25000, "to": 15000})


def test_employment_type_rejects_negative_salary():
    with pytest.raises(ValidationError):
        EmploymentType.model_validate({"from": -1})


@pytest.mark.parametrize("slug", ["", " ", "\t", None])
def test_raw_offer_rejects_empty_slug(slug):
    payload = {
        "slug": slug,
        "title": "Python Developer",
        "companyName": "Example",
        "publishedAt": "2026-08-11T10:00:00Z",
    }

    with pytest.raises(ValidationError):
        RawOffer.model_validate(payload)


@pytest.mark.parametrize(
    "skills",
    [{}, ["Python"], [{}], [{"name": ""}], [{"name": " "}]],
)
def test_raw_offer_rejects_invalid_skills(skills):
    payload = {
        "slug": "example-offer",
        "title": "Python Developer",
        "companyName": "Example",
        "publishedAt": "2026-08-11T10:00:00Z",
        "requiredSkills": skills,
    }

    with pytest.raises(ValidationError):
        RawOffer.model_validate(payload)


def test_employment_type_accepts_fractional_salary():
    employment = EmploymentType.model_validate({"from": 12345.67})
    assert employment.salary_from == Decimal("12345.67")


def test_employment_type_accepts_foreign_currency():
    employment = EmploymentType.model_validate({"from": 500, "currency": "USD"})
    assert employment.salary_from == Decimal("500")
    assert employment.currency == "USD"


def test_employment_type_accepts_missing_salary():
    employment = EmploymentType.model_validate({})
    assert employment.salary_from is None
    assert employment.salary_to is None


def test_raw_offer_rejects_date_without_timezone():
    payload = {
        "slug": "example-offer",
        "title": "Python Developer",
        "companyName": "Example",
        "publishedAt": "2026-08-11T10:00:00",
    }

    with pytest.raises(ValidationError, match="timezone"):
        RawOffer.model_validate(payload)


def test_raw_offer_accepts_date_with_offset():
    payload = {
        "slug": "example-offer",
        "title": "Python Developer",
        "companyName": "Example",
        "publishedAt": "2026-08-11T10:00:00+02:00",
    }

    offer = RawOffer.model_validate(payload)

    assert offer.published_at.astimezone(UTC) == datetime(2026, 8, 11, 8, tzinfo=UTC)

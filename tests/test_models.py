from datetime import UTC, datetime, timedelta

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


def test_employment_type_salary_too_low():
    with pytest.raises(ValidationError):
        EmploymentType.model_validate({"from": 500})

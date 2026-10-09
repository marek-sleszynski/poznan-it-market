from __future__ import annotations

import re
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
    StrictBool,
    field_validator,
    model_validator,
)


class EmploymentType(BaseModel):
    salary_from_per_unit: Decimal | None = Field(
        default=None, validation_alias="fromPerUnit", ge=0, allow_inf_nan=False
    )
    salary_to_per_unit: Decimal | None = Field(
        default=None, validation_alias="toPerUnit", ge=0, allow_inf_nan=False
    )
    gross: StrictBool | None = None
    unit: str | None = None
    currency: str | None = None
    currency_source: str | None = Field(default=None, validation_alias="currencySource")
    type: str | None = None

    @field_validator(
        "salary_from_per_unit",
        "salary_to_per_unit",
        mode="before",
    )
    @classmethod
    def check_salary_input(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("Salary must not be a boolean.")

        if isinstance(value, str):
            numeric_pattern = (
                r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
                r"(?:[eE][+-]?[0-9]+)?"
            )
            if re.fullmatch(numeric_pattern, value.strip()) is None:
                raise ValueError("Salary must be a valid numeric value.")

        return value

    @model_validator(mode="after")
    def check_order(self) -> EmploymentType:
        if (
            self.salary_from_per_unit is not None
            and self.salary_to_per_unit is not None
            and self.salary_from_per_unit > self.salary_to_per_unit
        ):
            raise ValueError("salary_from_per_unit cannot exceed salary_to_per_unit")

        return self


class Skill(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Skill name must not be empty.")
        return value


class RawOffer(BaseModel):
    slug: str = Field(validation_alias="slug")
    title: str = Field(validation_alias="title")
    company_name: str = Field(validation_alias="companyName")
    city: str | None = None
    published_at: AwareDatetime = Field(validation_alias="publishedAt")
    employment_types: list[EmploymentType] = Field(
        default_factory=list, validation_alias="employmentTypes"
    )
    required_skills: list[Skill] = Field(default_factory=list, validation_alias="requiredSkills")

    @field_validator("slug")
    @classmethod
    def check_slug(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("slug must not be empty.")
        return value

    @field_validator("published_at", mode="before")
    @classmethod
    def check_publication_format(cls, value: object) -> str:
        message = "publishedAt must be an ISO 8601 string with a timezone."
        if not isinstance(value, str):
            raise ValueError(message)

        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(message) from None

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError(message)

        return value

    @field_validator("published_at")
    @classmethod
    def check_realistic(cls, v: datetime) -> datetime:
        if v > datetime.now(UTC):
            raise ValueError("data after current date")
        return v

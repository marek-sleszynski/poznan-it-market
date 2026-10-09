from datetime import UTC, datetime
from decimal import Decimal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator


class EmploymentType(BaseModel):
    salary_from: Decimal | None = Field(
        default=None, validation_alias="from", ge=0, allow_inf_nan=False
    )
    salary_to: Decimal | None = Field(
        default=None, validation_alias="to", ge=0, allow_inf_nan=False
    )
    currency: str | None = None
    type: str | None = None

    @model_validator(mode="after")
    def check_order(self) -> EmploymentType:
        if (
            self.salary_from is not None
            and self.salary_to is not None
            and self.salary_from > self.salary_to
        ):
            raise ValueError("salary_from cannot exceed salary_to")
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
    model_config = ConfigDict(populate_by_name=True)
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

    @field_validator("published_at")
    @classmethod
    def check_realistic(cls, v: datetime) -> datetime:
        if v > datetime.now(UTC):
            raise ValueError("data after current date")
        return v

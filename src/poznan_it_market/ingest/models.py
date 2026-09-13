from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime, timezone

class EmploymentType(BaseModel):
    salary_from: int | None = Field(default=None, validation_alias="from")
    salary_to: int | None = Field(default=None, validation_alias="to")
    currency: str | None = None
    type: str | None = None

    @field_validator("salary_from", "salary_to")
    @classmethod
    def check_realistic(cls, v: int | None) -> int | None:
      if v is None:
        return v
      if v < 1000 or v > 200000:
        raise ValueError("Salary must be between 1,000 and 200,000 PLN")
      return v

    @model_validator(mode="after")
    def check_order(self) -> "SalaryRange":
        if (self.salary_from is not None and self.salary_to is not None and self.salary_from > self.salary_to):
          raise ValueError("salary_from cannot exceed salary_to")
        return self

class RawOffer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    slug: str = Field(validation_alias="slug")
    title: str = Field(validation_alias="title")
    company_name: str = Field(validation_alias="companyName")
    city: str | None = None
    published_at: datetime = Field(validation_alias="publishedAt")
    employment_types: list[EmploymentType] = Field(default_factory=list, validation_alias="employmentTypes")

    @field_validator("published_at")
    @classmethod

    def check_realistic(cls, v: datetime) -> datetime:
      if v > datetime.now(timezone.utc):
          raise ValueError("data after current date")
      return v

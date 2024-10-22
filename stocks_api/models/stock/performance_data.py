from pydantic import BaseModel, Field


class PerformanceData(BaseModel):
    five_days: float | None = Field(None)
    one_month: float | None = Field(None)
    three_months: float | None = Field(None)
    year_to_date: float | None = Field(None)
    one_year: float | None = Field(None)

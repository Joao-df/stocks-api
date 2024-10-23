from pydantic import BaseModel, Field


class PerformanceData(BaseModel):
    five_days: float | None = Field(None, validation_alias="5 Day")
    one_month: float | None = Field(None, validation_alias="1 Month")
    three_months: float | None = Field(None, validation_alias="3 Month")
    year_to_date: float | None = Field(None, validation_alias="YTD")
    one_year: float | None = Field(None, validation_alias="1 Year")

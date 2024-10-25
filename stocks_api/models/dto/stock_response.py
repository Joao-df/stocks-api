from datetime import date

from pydantic import BaseModel, Field


class MarketCapData(BaseModel):
    currency: str
    value: float


class CompetitorData(BaseModel):
    name: str
    market_cap: MarketCapData


class PerformanceData(BaseModel):
    five_days: float = Field(validation_alias="5 Day")
    one_month: float = Field(validation_alias="1 Month")
    three_months: float = Field(validation_alias="3 Month")
    year_to_date: float = Field(validation_alias="YTD")
    one_year: float = Field(validation_alias="1 Year")


class StockValuesData(BaseModel):
    open: float = Field()
    high: float = Field()
    low: float = Field()
    close: float = Field()


class StockData(BaseModel):
    status: str = Field()
    purchased_amount: int | None = Field(None)
    purchased_status: str | None = Field(None)
    request_data: date = Field()
    company_code: str = Field()
    company_name: str = Field()
    stock_values: StockValuesData = Field()
    performance_data: PerformanceData = Field()
    competitors: list[CompetitorData] = Field(default_factory=list)

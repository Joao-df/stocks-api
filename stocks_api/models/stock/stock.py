from datetime import date

from pydantic import BaseModel, Field

from stocks_api.models.stock.competitor import Competitor
from stocks_api.models.stock.performance_data import PerformanceData
from stocks_api.models.stock.stock_values import StockValues


class Stock(BaseModel):
    status: str | None = Field(None)
    purchased_amount: int | None = Field(None)
    purchased_status: str | None = Field(None)
    request_data: date | None = Field(None)
    company_code: str | None = Field(None)
    company_name: str | None = Field(None)
    stock_values: StockValues | None = Field(None)
    performance_data: PerformanceData | None = Field(None)
    competitors: list[Competitor] = Field(default_factory=list)

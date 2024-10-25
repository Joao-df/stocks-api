from pydantic import BaseModel, Field


class DailyOpenCloseStock(BaseModel):
    status: str
    date: str = Field(validation_alias="from")
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    after_hours: float = Field(validation_alias="afterHours")
    pre_market: float = Field(validation_alias="preMarket")

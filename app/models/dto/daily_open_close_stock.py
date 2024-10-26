from pydantic import AliasChoices, BaseModel, Field


class DailyOpenCloseStock(BaseModel):
    status: str
    date: str = Field(validation_alias=AliasChoices("from", "date"))
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    after_hours: float = Field(validation_alias=AliasChoices("afterHours", "after_hours"))
    pre_market: float = Field(validation_alias=AliasChoices("preMarket", "pre_market"))

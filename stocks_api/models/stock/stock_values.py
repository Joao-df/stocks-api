from pydantic import BaseModel, Field


class StockValues(BaseModel):
    open: float | None = Field(None)
    high: float | None = Field(None)
    low: float | None = Field(None)
    close: float | None = Field(None)

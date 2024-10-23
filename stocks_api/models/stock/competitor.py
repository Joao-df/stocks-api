from pydantic import BaseModel


class MarketCap(BaseModel):
    currency: str
    value: float


class Competitor(BaseModel):
    name: str
    market_cap: MarketCap

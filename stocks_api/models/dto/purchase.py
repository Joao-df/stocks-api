from pydantic import BaseModel


class PurchaseAmount(BaseModel):
    amount: float


class PurchaseStockAmount(PurchaseAmount):
    company_code: str

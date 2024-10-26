from pydantic import BaseModel


class PurchaseRequestBody(BaseModel):
    amount: float


class PurchaseStockAmount(PurchaseRequestBody):
    company_code: str


class PurchaseResponse(BaseModel):
    message: str

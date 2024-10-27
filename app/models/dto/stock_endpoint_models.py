from pydantic import BaseModel


class PurchaseRequestBody(BaseModel):
    amount: int


class PurchaseStockAmount(PurchaseRequestBody):
    company_code: str


class PurchaseResponse(BaseModel):
    message: str

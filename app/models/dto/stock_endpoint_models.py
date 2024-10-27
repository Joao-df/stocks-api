from pydantic import BaseModel


class PurchaseRequestBody(BaseModel):
    amount: int


class PurchaseResponse(BaseModel):
    message: str

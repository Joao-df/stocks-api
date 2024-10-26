from datetime import date

from pydantic import BaseModel, Field

from app.common.datetime_utils import get_yesterday


class GetStockQueryParams(BaseModel):
    request_date: date = Field(alias="date", default_factory=get_yesterday)


class PurchaseRequestBody(BaseModel):
    amount: float


class PurchaseStockAmount(PurchaseRequestBody):
    company_code: str


class PurchaseResponse(BaseModel):
    message: str

from datetime import date, datetime, timedelta

from fastapi import APIRouter

from stocks_api.app_config import SettingsDep
from stocks_api.cache import default_cache
from stocks_api.database import SessionDep
from stocks_api.models.dto.purchase import PurchaseRequestBody, PurchaseResponse
from stocks_api.models.dto.stock_response import StockData
from stocks_api.service.stock import StockService

router = APIRouter(prefix="/stock", tags=["stock"])


def get_yesterday() -> date:
    return (datetime.now() - timedelta(1)).date()


@router.get("/{stock_symbol}")
@default_cache()
async def get_stock(
    stock_symbol: str,
    session: SessionDep,
    settings: SettingsDep,
    date: date = get_yesterday(),
) -> StockData:
    return await StockService(
        settings,
        session,
    ).get_stock_by_symbol(stock_symbol=stock_symbol, date=date)


@router.post("/{stock_symbol}", status_code=201)
async def purchase_stock(
    purchase_amount: PurchaseRequestBody,
    stock_symbol: str,
    session: SessionDep,
    settings: SettingsDep,
) -> PurchaseResponse:
    await StockService(settings, session).purchase_stock(
        stock_symbol=stock_symbol, purchase_amount=purchase_amount
    )

    return PurchaseResponse(
        message=f"{purchase_amount.amount} units of stock {stock_symbol} were added to your stock record."
    )

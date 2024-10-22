from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends

from stocks_api.app_config import Settings, get_settings
from stocks_api.models.stock.stock import Stock
from stocks_api.service.stock import StockService

router = APIRouter(prefix="/stock", tags=["stock"])


def get_yesterday() -> date:
    return (datetime.now() - timedelta(1)).date()


@router.get("/{stock_symbol}")
def get_stock(
    settings: Annotated[Settings, Depends(get_settings)],
    stock_symbol: str,
    date: date = get_yesterday(),
) -> Stock:
    return StockService(
        polygon_api_key=settings.polygon_api_key,
        polygon_base_url=settings.polygon_base_url,
    ).get_stock_by_symbol(stock_symbol=stock_symbol, date=date)

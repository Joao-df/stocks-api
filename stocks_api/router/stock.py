from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends

from stocks_api.models.stock.stock import Stock
from stocks_api.repository.stock import CompositeStockRepository
from stocks_api.service.stock import StockService

router = APIRouter(prefix="/stock", tags=["stock"])


def get_yesterday() -> date:
    return (datetime.now() - timedelta(1)).date()


@router.get("/{stock_symbol}")
def get_stock(
    stock_symbol: str,
    date: date = get_yesterday(),
    stock_repository: CompositeStockRepository = Depends(),
) -> Stock:
    return StockService(
        stock_repository=stock_repository,
    ).get_stock_by_symbol(stock_symbol=stock_symbol, date=date)

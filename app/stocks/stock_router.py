from typing import Annotated

from fastapi import APIRouter, Body, Query

from app.app_config import SettingsDep
from app.cache import default_cache
from app.database import SessionDep
from app.models.dto.stock_endpoint_models import GetStockQueryParams, PurchaseRequestBody, PurchaseResponse
from app.models.dto.stock_response import StockData
from app.stocks.stock_service import StockService

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/{stock_symbol}")
@default_cache()
async def get_stock(
    stock_symbol: str,
    query_params: Annotated[GetStockQueryParams, Query()],
    session: SessionDep,
    settings: SettingsDep,
) -> StockData:
    """Get stock data for a specific stock symbol.

    Parameters:
    - stock_symbol (str): The symbol of the stock to retrieve data for.
    - session (AsyncSession): The database session dependency.
    - settings (Settings): The application settings dependency.
    - date (date): The date for which to retrieve the stock data. Defaults to yesterday.

    Returns:
    - StockData: The stock data for the specified symbol.
    """
    return await StockService(
        settings,
        session,
    ).get_stock_by_symbol(stock_symbol=stock_symbol, date=query_params.request_date)


@router.post("/{stock_symbol}", status_code=201)
async def purchase_stock(
    request_body: Annotated[PurchaseRequestBody, Body()],
    stock_symbol: str,
    session: SessionDep,
    settings: SettingsDep,
) -> PurchaseResponse:
    """Endpoint to purchase a specified amount of a stock.

    Parameters:
    - purchase_amount: The amount of the stock to purchase.
    - stock_symbol: The symbol of the stock to purchase.
    - session: The database session dependency.
    - settings: The application settings dependency.

    Returns:
    - PurchaseResponse: A message confirming the purchase of the stock.
    """
    await StockService(settings, session).purchase_stock(stock_symbol=stock_symbol, amount=request_body.amount)

    return PurchaseResponse(
        message=f"{request_body.amount} units of stock {stock_symbol} were added to your stock record."
    )

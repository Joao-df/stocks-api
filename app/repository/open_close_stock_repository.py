import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import httpx
from fastapi import HTTPException

from app.app_config import Settings
from app.models.dto.daily_open_close_stock import DailyOpenCloseStock

logger: logging.Logger = logging.getLogger()
OPEN_CLOSE_ENDPOINT = "/v1/open-close/{stock_symbol}/{date}?adjusted=true&apiKey={api_key}"
STOCK_DETAILS_ENDPOINT = "/investing/stock/{stock_symbol}"
executor = ThreadPoolExecutor(max_workers=5)


class OpenCloseStockRepositoryInterface(ABC):
    @abstractmethod
    async def get_daily_open_close_sotck(self, stock_symbol: str, date: date) -> DailyOpenCloseStock: ...


class OpenCloseStockRepository(OpenCloseStockRepositoryInterface):
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings

    async def get_daily_open_close_sotck(self, stock_symbol: str, date: date) -> DailyOpenCloseStock:
        uri: str = f"{self.settings.polygon_base_url}{OPEN_CLOSE_ENDPOINT.format(stock_symbol=stock_symbol, date=date, api_key=self.settings.polygon_api_key)}"
        async with httpx.AsyncClient() as client:
            try:
                response_data: httpx.Response = await client.get(uri)
            except httpx.RequestError as exp:
                logger.error("Failed to request data: %s", exp)
                raise HTTPException(status_code=500, detail="Internal error. Please contact support.")
        match response_data.status_code:
            case 200:
                return DailyOpenCloseStock.model_validate(response_data.json())
            case 404:
                detail = f"Stock {stock_symbol} not found"
                logger.warning(detail)
                raise HTTPException(status_code=404, detail=detail)
            case _:
                logger.error(
                    "Request failed for %s. Returned data: %s",
                    stock_symbol,
                    response_data.json(),
                )
                raise HTTPException(status_code=500, detail="Internal error. Please contact support.")

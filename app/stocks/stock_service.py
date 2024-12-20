from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.app_config import Settings
from app.models.dto.daily_open_close_stock import DailyOpenCloseStock
from app.models.dto.stock_response import (
    CompetitorData,
    PerformanceData,
    StockData,
    StockValuesData,
)
from app.repository.marketwatch_repository import MarketWatchRepository
from app.repository.open_close_stock_repository import OpenCloseStockRepository
from app.repository.purchases_repository import PurchasesRepository


class StockService:
    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.open_close_stock_repository: OpenCloseStockRepository = OpenCloseStockRepository(settings=settings)
        self.marketwatch_repository: MarketWatchRepository = MarketWatchRepository(settings=settings)
        self.purchases_repository: PurchasesRepository = PurchasesRepository(settings=settings, session=session)

    async def get_stock_by_symbol(self, stock_symbol: str, date: date) -> StockData:
        """Retrieves stock data for a given stock symbol and date.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve data for.
            date (date): The date for which to retrieve the stock data.

        Returns:
            StockData: An object containing various data points related to the stock, including stock values, performance data, and competitors.
        """
        daily_open_close_data: DailyOpenCloseStock = await self.open_close_stock_repository.get_daily_open_close_sotck(
            stock_symbol, date
        )

        stock_values: StockValuesData = StockValuesData.model_validate(daily_open_close_data.model_dump())
        performance_data: PerformanceData = await self.marketwatch_repository.get_stock_performance_by_symbol(
            stock_symbol
        )
        competitors: list[CompetitorData] = await self.marketwatch_repository.get_stock_competitors_by_symbol(
            stock_symbol=stock_symbol
        )

        company_name: str = await self.marketwatch_repository.get_company_name_by_symbol(stock_symbol=stock_symbol)

        purchased_amount: float = await self.purchases_repository.get_purchases_total_amount_by_symbol(stock_symbol)

        return_data: dict[str, Any] = {
            "status": daily_open_close_data.status,
            "purchased_amount": purchased_amount,
            "purchased_status": daily_open_close_data.status,
            "request_data": daily_open_close_data.date,
            "company_code": daily_open_close_data.symbol,
            "company_name": company_name,
            "stock_values": stock_values,
            "performance_data": performance_data,
            "competitors": competitors,
        }

        return StockData.model_validate(return_data)

    async def purchase_stock(self, stock_symbol: str, amount: int) -> None:
        """Purchase a specific amount of stock for a given stock symbol.

        Args:
            stock_symbol (str): The symbol of the stock to purchase.
            amount (float): The amount of stock to purchase.

        Returns:
            None
        """
        await self.purchases_repository.purchase_stock(company_code=stock_symbol, amount=amount)

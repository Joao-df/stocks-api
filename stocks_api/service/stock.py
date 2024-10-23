from datetime import date

from stocks_api.models.stock.stock import Stock
from stocks_api.repository.stock import CompositeStockRepository


class StockService:
    def __init__(self, stock_repository: CompositeStockRepository) -> None:
        self.stock_repository: CompositeStockRepository = stock_repository

    async def get_stock_by_symbol(self, stock_symbol: str, date: date) -> Stock:
        return await self.stock_repository.get_stock_by_symbol(stock_symbol, date)

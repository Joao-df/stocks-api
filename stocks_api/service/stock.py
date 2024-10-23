from datetime import date

from stocks_api.models.stock.stock import Stock
from stocks_api.repository.stock import ApiStockRepository


class StockService:
    def __init__(self, stock_repository: ApiStockRepository) -> None:
        self.stock_repository = stock_repository

    def get_stock_by_symbol(self, stock_symbol: str, date: date) -> Stock:
        return self.stock_repository.get_stock_by_symbol(stock_symbol, date)

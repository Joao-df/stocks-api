from datetime import date

from sqlalchemy.orm import Session

from stocks_api.app_config import Settings
from stocks_api.models.dto.purchase import PurchaseRequestBody, PurchaseStockAmount
from stocks_api.models.dto.stock_response import StockData
from stocks_api.repository.stock import CompositeStockRepository


class StockService:
    def __init__(self, settings: Settings, session: Session) -> None:
        self.stock_repository: CompositeStockRepository = CompositeStockRepository(
            settings, session
        )

    async def get_stock_by_symbol(self, stock_symbol: str, date: date) -> StockData:
        return await self.stock_repository.get_stock_by_symbol(stock_symbol, date)

    async def purchase_stock(
        self, stock_symbol: str, purchase_amount: PurchaseRequestBody
    ) -> None:
        purchase_stock_amount: PurchaseStockAmount = PurchaseStockAmount.model_validate(
            purchase_amount.model_dump() | {"company_code": stock_symbol}
        )
        print(purchase_stock_amount)
        await self.stock_repository.purchase_stock(purchase_stock_amount)

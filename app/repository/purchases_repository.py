from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_config import Settings
from app.models.dto.stock_endpoint_models import PurchaseStockAmount
from app.models.tables.purchases import Purchases


class PurchasesRepositoryInterface(ABC):
    @abstractmethod
    async def purchase_stock(self, purchase_amount: PurchaseStockAmount) -> None:
        """
        Add a purchase record to the database.

        Parameters:
        - purchase_amount: An instance of PurchaseStockAmount representing the purchase amount details.

        Returns:
        - None
        """

    @abstractmethod
    async def get_purchases_total_amount_by_symbol(self, stock_symbol: str) -> float:
        """Get the total purchase amount for a specific stock symbol.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve the total purchase amount for.

        Returns:
            float: The total purchase amount for the specified stock symbol. Returns 0.0 if no amount is found.
        """


class PurchasesRepository(PurchasesRepositoryInterface):
    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.settings: Settings = settings
        self.session: AsyncSession = session

    async def purchase_stock(self, purchase_amount: PurchaseStockAmount) -> None:
        purchases = Purchases(**purchase_amount.model_dump())
        self.session.add(purchases)
        await self.session.commit()

    async def get_purchases_total_amount_by_symbol(self, stock_symbol: str) -> float:
        total_amount: float | None = await self.session.scalar(
            select(func.sum(Purchases.amount)).where(Purchases.company_code == stock_symbol)
        )
        return total_amount if total_amount is not None else 0.0

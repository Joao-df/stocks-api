from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_config import Settings
from app.models.tables.purchases import Purchases


class PurchasesRepositoryInterface(ABC):
    @abstractmethod
    async def purchase_stock(self, company_code: str, amount: int) -> None:
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
            company_code (str): The code of the company for which the stock is being purchased.
            amount (int): The quantity of stock being purchased.

        Returns:
            float: The total purchase amount for the specified stock symbol. Returns 0.0 if no amount is found.
        """


class PurchasesRepository(PurchasesRepositoryInterface):
    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.settings: Settings = settings
        self.session: AsyncSession = session

    async def purchase_stock(self, company_code: str, amount: int) -> None:
        purchases = Purchases(company_code=company_code, amount=amount)
        self.session.add(purchases)
        await self.session.commit()

    async def get_purchases_total_amount_by_symbol(self, stock_symbol: str) -> int:
        total_amount: int | None = await self.session.scalar(
            select(func.sum(Purchases.amount)).where(Purchases.company_code == stock_symbol)
        )
        return total_amount if total_amount is not None else 0

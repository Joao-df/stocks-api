from sqlalchemy import func
from sqlalchemy.orm import Session

from app.app_config import Settings
from app.models.dto.purchase import PurchaseStockAmount
from app.models.tables.purchases import Purchases


class PurchasesRepository:
    def __init__(self, settings: Settings, session: Session) -> None:
        self.settings: Settings = settings
        self.session: Session = session

    async def purchase_stock(self, purchase_amount: PurchaseStockAmount) -> None:
        purchases = Purchases(**purchase_amount.model_dump())
        self.session.add(purchases)
        self.session.commit()

    async def get_purchases_total_amount_by_symbol(self, stock_symbol: str) -> float:
        total_amount: float | None = (
            self.session.query(func.sum(Purchases.amount))
            .filter(Purchases.company_code == stock_symbol)
            .scalar()
        )
        return total_amount if total_amount is not None else 0.0

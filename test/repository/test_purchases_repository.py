from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_config import Settings
from app.models.tables.purchases import Purchases
from app.repository.purchases_repository import PurchasesRepository


class TestPurchasesRepository:
    @pytest.mark.asyncio
    async def test_add_purchase_record(self) -> None:
        amount = 100.0
        mock_session = MagicMock(spec=AsyncSession)
        repo = PurchasesRepository(Settings(), mock_session)

        await repo.purchase_stock(company_code="AAPL", amount=amount)

        mock_session.add.assert_called_once()
        added_purchase = mock_session.add.call_args[0][0]
        assert isinstance(added_purchase, Purchases)
        assert added_purchase.company_code == "AAPL"
        assert added_purchase.amount == amount
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_total_amount(self) -> None:
        amount = 150.0
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.scalar.return_value = amount
        repo = PurchasesRepository(Settings(), mock_session)

        total_amount = await repo.get_purchases_total_amount_by_symbol("AAPL")

        assert total_amount == amount

    @pytest.mark.asyncio
    async def test_return_zero_for_no_purchases(self) -> None:
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.scalar.return_value = None
        repo = PurchasesRepository(Settings(), mock_session)

        total_amount = await repo.get_purchases_total_amount_by_symbol("AAPL")

        assert total_amount == 0

    @pytest.mark.asyncio
    async def test_handle_commit_exception(self) -> None:
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit.side_effect = Exception("DB error")
        repo = PurchasesRepository(Settings(), mock_session)

        with pytest.raises(Exception, match="DB error"):
            await repo.purchase_stock(company_code="AAPL", amount=100)

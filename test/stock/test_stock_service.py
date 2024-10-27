from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from app.models.dto.daily_open_close_stock import DailyOpenCloseStock
from app.models.dto.stock_response import CompetitorData, PerformanceData, StockData
from app.stocks.stock_service import StockService
from test.constants import (
    AAPL_COMPANY_NAME,
    AAPL_COMPETITORS,
    AAPL_DAILY_OPEN_CLOSE_STOCK,
    AAPL_EXPECTED_STOCK,
    AAPL_PERFORMANCE_DATA,
    AAPL_PURCHASES_AMOUNT,
    GE_COMPANY_NAME,
    GE_COMPETITORS,
    GE_DAILY_OPEN_CLOSE_STOCK,
    GE_EXPECTED_STOCK,
    GE_PERFORMANCE_DATA,
    GE_PURCHASES_AMOUNT,
)


class MockValues(BaseModel):
    get_daily_open_close_sotck: DailyOpenCloseStock
    get_stock_performance_by_symbol: PerformanceData
    get_stock_competitors_by_symbol: list[CompetitorData]
    get_company_name_by_symbol: str
    get_purchases_total_amount_by_symbol: float


AAPL_MOCK_VALUES: MockValues = MockValues.model_validate(
    {
        "get_daily_open_close_sotck": AAPL_DAILY_OPEN_CLOSE_STOCK,
        "get_stock_performance_by_symbol": AAPL_PERFORMANCE_DATA,
        "get_stock_competitors_by_symbol": AAPL_COMPETITORS,
        "get_company_name_by_symbol": AAPL_COMPANY_NAME,
        "get_purchases_total_amount_by_symbol": AAPL_PURCHASES_AMOUNT,
    }
)

GE_MOCK_VALUES: MockValues = MockValues.model_validate(
    {
        "get_daily_open_close_sotck": GE_DAILY_OPEN_CLOSE_STOCK,
        "get_stock_performance_by_symbol": GE_PERFORMANCE_DATA,
        "get_stock_competitors_by_symbol": GE_COMPETITORS,
        "get_company_name_by_symbol": GE_COMPANY_NAME,
        "get_purchases_total_amount_by_symbol": GE_PURCHASES_AMOUNT,
    }
)


class TestStockService:
    @pytest.mark.parametrize(
        "mock_values, expected_stock",
        [
            pytest.param(
                AAPL_MOCK_VALUES,
                AAPL_EXPECTED_STOCK,
                id="AAPL",
            ),
            pytest.param(
                GE_MOCK_VALUES,
                GE_EXPECTED_STOCK,
                id="GE",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_retrieve_stock_data_success(
        self,
        mock_values: MockValues,
        expected_stock: StockData,
        mock_open_close_stock_repository: dict[str, MagicMock | AsyncMock],
        mock_marketwatch_repository: dict[str, MagicMock | AsyncMock],
        mock_purchases_repository: dict[str, MagicMock | AsyncMock],
    ) -> None:
        mock_open_close_stock_repository[
            "get_daily_open_close_sotck"
        ].return_value = mock_values.get_daily_open_close_sotck
        mock_marketwatch_repository[
            "get_stock_performance_by_symbol"
        ].return_value = mock_values.get_stock_performance_by_symbol
        mock_marketwatch_repository[
            "get_stock_competitors_by_symbol"
        ].return_value = mock_values.get_stock_competitors_by_symbol
        mock_marketwatch_repository["get_company_name_by_symbol"].return_value = mock_values.get_company_name_by_symbol
        mock_purchases_repository[
            "get_purchases_total_amount_by_symbol"
        ].return_value = mock_values.get_purchases_total_amount_by_symbol

        stock_service = StockService(settings=MagicMock(), session=MagicMock())
        stock_data: StockData = await stock_service.get_stock_by_symbol(
            mock_values.get_daily_open_close_sotck.symbol, mock_values.get_daily_open_close_sotck.date
        )

        assert expected_stock.model_dump() == stock_data.model_dump()

    @pytest.mark.parametrize(
        "symbol, amount",
        [
            pytest.param("AAPL", 50, id="AAPL-50"),
            pytest.param("GE", 100, id="GE-100"),
        ],
    )
    @pytest.mark.asyncio
    async def test_purchase_stock_success(
        self,
        symbol: str,
        amount: float,
        mock_purchases_repository: dict[str, MagicMock | AsyncMock],
    ) -> None:
        mock_purchase_stock: MagicMock | AsyncMock = mock_purchases_repository["purchase_stock"]

        stock_service = StockService(settings=MagicMock(), session=MagicMock())
        await stock_service.purchase_stock(symbol, amount)

        mock_purchase_stock.assert_called_once_with(company_code=symbol, amount=amount)

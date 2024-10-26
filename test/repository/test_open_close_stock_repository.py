from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException

from app.app_config import Settings
from app.models.dto.daily_open_close_stock import DailyOpenCloseStock
from app.repository.open_close_stock_repository import OpenCloseStockRepository
from test.constants import (
    AAPL_DAILY_OPEN_CLOSE_STOCK,
    AAPL_DAILY_OPEN_CLOSE_STOCK_DATA,
    GE_DAILY_OPEN_CLOSE_STOCK,
    GE_DAILY_OPEN_CLOSE_STOCK_DATA,
)


class TestOpenCloseStockRepository:
    @pytest.mark.parametrize(
        "api_response, expected_result",
        [
            pytest.param(AAPL_DAILY_OPEN_CLOSE_STOCK_DATA, AAPL_DAILY_OPEN_CLOSE_STOCK, id="AAPL"),
            pytest.param(GE_DAILY_OPEN_CLOSE_STOCK_DATA, GE_DAILY_OPEN_CLOSE_STOCK, id="GE"),
        ],
    )
    @pytest.mark.asyncio
    async def test_retrieve_valid_stock_data(
        self,
        api_response: dict[str, Any],
        expected_result: DailyOpenCloseStock,
        mock_httpx_async_client: dict[str, MagicMock | AsyncMock],
    ) -> None:
        settings = Settings(polygon_api_key="test_key")
        repository = OpenCloseStockRepository(settings)
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = api_response
        mock_httpx_async_client["get"].return_value = mock_response
        result: DailyOpenCloseStock = await repository.get_daily_open_close_sotck("AAPL", date(2023, 10, 1))
        assert result.model_dump() == expected_result.model_dump()

    @pytest.mark.asyncio
    async def test_handle_404_error(self, mock_httpx_async_client: dict[str, MagicMock | AsyncMock]) -> None:
        settings = Settings(polygon_api_key="test_key")
        repository = OpenCloseStockRepository(settings)
        mock_response = MagicMock(spec=httpx.Response, status_code=404)
        mock_response.json.return_value = {}
        mock_httpx_async_client["get"].return_value = mock_response
        with pytest.raises(HTTPException) as excinfo:
            await repository.get_daily_open_close_sotck("INVALID", date(2023, 10, 1))
        error_status_code = 404
        assert excinfo.value.status_code == error_status_code

    @pytest.mark.asyncio
    async def test_handle_unexpected_500_error(
        self,
        mock_httpx_async_client: dict[str, MagicMock | AsyncMock],
    ) -> None:
        settings = Settings(polygon_api_key="test_key")
        repository = OpenCloseStockRepository(settings)
        mock_response = MagicMock(spec=httpx.Response, status_code=500)
        mock_response.json.return_value = {}
        mock_httpx_async_client["get"].return_value = mock_response
        with pytest.raises(HTTPException) as excinfo:
            await repository.get_daily_open_close_sotck("AAPL", date(2023, 10, 1))
        error_status_code = 500
        assert excinfo.value.status_code == error_status_code

    @pytest.mark.asyncio
    async def test_manage_network_failures(
        self,
        mock_httpx_async_client: dict[str, MagicMock | AsyncMock],
    ) -> None:
        settings = Settings(polygon_api_key="test_key")
        repository = OpenCloseStockRepository(settings)
        mock_httpx_async_client["get"].side_effect = httpx.RequestError("Network error")
        with pytest.raises(HTTPException) as excinfo:
            await repository.get_daily_open_close_sotck("AAPL", date(2023, 10, 1))
        error_status_code = 500
        assert excinfo.value.status_code == error_status_code

from datetime import date
from typing import Any, Generator
from unittest.mock import DEFAULT, AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from app.stocks.stock_router import router
from app.stocks.stock_service import StockService
from test.constants import AAPL_EXPECTED_STOCK

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture(scope="function")
def mock_stock_service() -> Generator[dict[str, AsyncMock | MagicMock], Any, None]:
    with patch.multiple(StockService, get_stock_by_symbol=DEFAULT, purchase_stock=DEFAULT) as mock:
        yield mock


@pytest.mark.asyncio
def test_get_stock(mock_stock_service: dict[str, AsyncMock | MagicMock]) -> None:
    mock_stock_service["get_stock_by_symbol"].return_value = AAPL_EXPECTED_STOCK
    _ = client.get("/stock/AAPL", params={"date": "2024-10-10"})
    mock_stock_service["get_stock_by_symbol"].assert_called_once_with(
        stock_symbol="AAPL", date=date(year=2024, month=10, day=10)
    )


@pytest.mark.asyncio
def test_purchase_stock(mock_stock_service: dict[str, AsyncMock | MagicMock]) -> None:
    response: Response = client.post("/stock/AAPL", json={"amount": 10})
    mock_stock_service["purchase_stock"].assert_called_once_with(stock_symbol="AAPL", amount=10)
    assert response.json() == {"message": "10.0 units of stock AAPL were added to your stock record."}

from typing import Any, Generator
from unittest.mock import DEFAULT, AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.repository.marketwatch_repository import MarketWatchRepository
from app.repository.open_close_stock_repository import OpenCloseStockRepository
from app.repository.purchases_repository import PurchasesRepository


@pytest.fixture(scope="function")
def mock_open_close_stock_repository() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(OpenCloseStockRepository, get_daily_open_close_sotck=DEFAULT) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_marketwatch_repository() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(
        MarketWatchRepository,
        get_stock_performance_by_symbol=DEFAULT,
        get_company_name_by_symbol=DEFAULT,
        get_stock_competitors_by_symbol=DEFAULT,
        _async_get_stock_page_html=DEFAULT,
    ) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_purchases_repository() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(
        PurchasesRepository, get_purchases_total_amount_by_symbol=DEFAULT, purchase_stock=DEFAULT
    ) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_httpx_async_client() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(AsyncClient, get=DEFAULT, post=DEFAULT, put=DEFAULT, patch=DEFAULT) as mock:
        yield mock


patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

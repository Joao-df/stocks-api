from typing import Any, Generator
from unittest.mock import DEFAULT, AsyncMock, MagicMock, patch

import pytest

from app.repository.marketwatch_repository import MarketWatchRepository
from app.repository.open_close_stock_repository import OpenCloseStockRepository
from app.repository.purchases_repository import PurchasesRepository


@pytest.fixture
def mock_open_close_stock_repository() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(OpenCloseStockRepository, get_daily_open_close_sotck=DEFAULT) as mock:
        yield mock


@pytest.fixture
def mock_marketwatch_repository() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(
        MarketWatchRepository,
        get_stock_performance_by_symbol=DEFAULT,
        get_company_name_by_symbol=DEFAULT,
        get_stock_competitors_by_symbol=DEFAULT,
    ) as mock:
        yield mock


@pytest.fixture
def mock_purchases_repository() -> Generator[dict[str, MagicMock | AsyncMock], Any, None]:
    with patch.multiple(
        PurchasesRepository, get_purchases_total_amount_by_symbol=DEFAULT, purchase_stock=DEFAULT
    ) as mock:
        yield mock

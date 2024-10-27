from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from pytest import FixtureRequest
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from app.app_config import Settings
from app.models.dto.stock_response import CompetitorData, PerformanceData
from app.repository.marketwatch_repository import MarketWatchRepository


@pytest.fixture(params=["stock_page.html"], scope="function")
def mock_get_stock_page_html(request: FixtureRequest) -> Generator[MagicMock | AsyncMock, Any, None]:
    filename = request.param
    with patch.object(MarketWatchRepository, "_async_get_stock_page_html") as mock:
        with open(f"./test/repository/marketwatch_html/{filename}", "r") as arq:
            mock.return_value = BeautifulSoup(arq, "html.parser")
        yield mock


class TestMarketWatchRepository:
    @pytest.mark.asyncio
    async def test_get_stock_performance_by_symbol_success(self, mock_get_stock_page_html: AsyncMock) -> None:
        repo = MarketWatchRepository(Settings(polygon_api_key=""))
        result: PerformanceData = await repo.get_stock_performance_by_symbol("AAPL")
        assert result.model_dump() == {
            "five_days": -1.53,
            "one_month": 1.59,
            "three_months": 6.17,
            "year_to_date": 20.19,
            "one_year": 37.56,
        }

    @pytest.mark.asyncio
    async def test_get_stock_competitors_by_symbol_success(self, mock_get_stock_page_html: AsyncMock) -> None:
        repo = MarketWatchRepository(Settings(polygon_api_key=""))
        result: list[CompetitorData] = await repo.get_stock_competitors_by_symbol("AAPL")

        assert result[0].model_dump() == {
            "name": "Microsoft Corp.",
            "market_cap": {"currency": "$", "value": 3160000000000.0},
        }
        assert result[1].model_dump() == {
            "name": "Alphabet Inc. Cl C",
            "market_cap": {"currency": "$", "value": 2010000000000.0},
        }

    @pytest.mark.asyncio
    async def test_get_company_name_by_symbol_success(self, mock_get_stock_page_html: AsyncMock) -> None:
        repo = MarketWatchRepository(Settings(polygon_api_key=""))
        result = await repo.get_company_name_by_symbol("AAPL")
        assert result == "Apple Inc."

    @pytest.mark.asyncio
    async def test_returns_true_when_captcha_present(self) -> None:
        driver = MagicMock()
        driver.find_elements.return_value = [MagicMock()]
        result = MarketWatchRepository(Settings(polygon_api_key=""))._is_captcha_open(driver)
        assert result is True

    @pytest.mark.asyncio
    async def test_closes_banner_if_displayed(self) -> None:
        driver = MagicMock(spec=webdriver.Chrome)
        banner = MagicMock(spec=WebElement)
        close_btn = MagicMock(spec=WebElement)
        driver.find_element.return_value = banner
        banner.is_displayed.return_value = True
        banner.find_element.return_value = close_btn
        close_btn.is_displayed.return_value = True

        MarketWatchRepository(Settings(polygon_api_key=""))._close_subscriber_banner(driver)

        close_btn.click.assert_called_once()

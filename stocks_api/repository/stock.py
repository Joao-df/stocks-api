import logging
from datetime import date
from functools import lru_cache
from typing import Any, List

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from fastapi import Depends, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random,
)

from stocks_api.app_config import Settings, get_settings
from stocks_api.common.currency_utils import convert_currency_string
from stocks_api.models.stock.competitor import Competitor
from stocks_api.models.stock.performance_data import PerformanceData
from stocks_api.models.stock.stock import Stock
from stocks_api.models.stock.stock_values import StockValues

logger: logging.Logger = logging.getLogger()
OPEN_CLOSE_ENDPOINT = (
    "/v1/open-close/{stock_symbol}/{date}?adjusted=true&apiKey={api_key}"
)
STOCK_DETAILS_ENDPOINT = "/investing/stock/{stock_symbol}"


class CatchByBotDetectionError(Exception): ...


class ScrapingStockRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings

    @property
    def _chrome_options(self) -> Options:
        options = webdriver.ChromeOptions()
        # run in headless mode
        options.add_argument("--headless=new")

        # run in incognito mode
        options.add_argument("--incognito")

        # adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        # exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)

        # Add random user agent
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f"--user-agent={user_agent}")

        return options

    def _close_subscriber_banner(self, driver: webdriver.Chrome) -> None:
        banner: WebElement = driver.find_element(By.ID, "cx-scrim-wrapper")
        if banner.is_displayed():
            close_banner_btn: WebElement = banner.find_element(
                By.CLASS_NAME, "close-btn"
            )
            if close_banner_btn.is_displayed():
                close_banner_btn.click()

    def _is_captcha_open(self, driver: webdriver.Chrome) -> bool:
        captcha_scripts: List[WebElement] = driver.find_elements(
            By.XPATH, '/html/body/script[@src="https://ct.captcha-delivery.com/c.js"]'
        )
        return bool(captcha_scripts)

    @lru_cache
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random(min=1, max=2),
        retry=retry_if_exception_type(CatchByBotDetectionError),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
    )
    def _get_stock_page_html(self, stock_symbol: str) -> BeautifulSoup:
        driver = webdriver.Chrome(self._chrome_options)
        try:
            # Navigate to the URL
            uri: str = f"{self.settings.marketwatch_base_url}{STOCK_DETAILS_ENDPOINT.format(stock_symbol=stock_symbol)}"
            driver.get(uri)

            if self._is_captcha_open(driver):
                logger.warning("Catch by bot detection.")
                raise CatchByBotDetectionError()

            self._close_subscriber_banner(driver)
            page_html: str = driver.page_source
            return BeautifulSoup(page_html, "html.parser")
        finally:
            driver.quit()

    def get_stock_performance_by_symbol(self, stock_symbol: str) -> PerformanceData:
        stock_page: BeautifulSoup = self._get_stock_page_html(stock_symbol)
        performance_div = stock_page.find("div", class_="performance")
        table_rows = performance_div.find_all("tr", class_="table__row")

        performance_data = {
            table_row.find("td").text: table_row.find("li").text.replace("%", "")
            for table_row in table_rows
        }

        return PerformanceData.model_validate(performance_data)

    def get_stock_competitors_by_symbol(self, stock_symbol: str) -> list[Competitor]:
        stock_page: BeautifulSoup = self._get_stock_page_html(stock_symbol)
        competitors_div = stock_page.find("div", class_="Competitors")
        table_rows = competitors_div.find("tbody").find_all("tr")
        return [
            Competitor.model_validate(
                {
                    "name": table_row.find("a", class_="link").text,
                    "market_cap": convert_currency_string(
                        table_row.find_all("td")[2].text
                    ),
                }
            )
            for table_row in table_rows
        ]

    def get_company_name_by_symbol(self, stock_symbol: str) -> str:
        stock_page: BeautifulSoup = self._get_stock_page_html(stock_symbol)
        return stock_page.find("h1", class_="company__name").text


class ApiStockRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings

    def get_daily_open_close_sotck(
        self, stock_symbol: str, date: date
    ) -> dict[str, Any]:
        uri: str = f"{self.settings.polygon_base_url}{OPEN_CLOSE_ENDPOINT.format(stock_symbol=stock_symbol, date=date, api_key=self.settings.polygon_api_key)}"
        response_data: requests.Response = requests.get(uri)
        match response_data.status_code:
            case 200:
                return response_data.json()
            case 404:
                detail = f"Stock {stock_symbol} not found"
                logger.warning(detail)
                raise HTTPException(status_code=404, detail=detail)
            case _:
                logger.error(
                    "Request failed for %s. Returned data: %s",
                    stock_symbol,
                    response_data.json(),
                )
                raise HTTPException(
                    status_code=500, detail="Internal error. Please contact support."
                )


class CompositeStockRepository:
    def __init__(
        self,
        api_stock_repository: ApiStockRepository = Depends(
            lambda: ApiStockRepository(get_settings())
        ),
        scraping_stock_repository: ScrapingStockRepository = Depends(
            lambda: ScrapingStockRepository(get_settings())
        ),
    ) -> None:
        self.api_stock_repository: ApiStockRepository = api_stock_repository
        self.scraping_stock_repository: ScrapingStockRepository = (
            scraping_stock_repository
        )

    def get_stock_by_symbol(self, stock_symbol: str, date: date) -> Stock:
        daily_open_close_data = self.api_stock_repository.get_daily_open_close_sotck(
            stock_symbol, date
        )

        stock_values: StockValues = StockValues.model_validate(daily_open_close_data)
        performance_data: PerformanceData = (
            self.scraping_stock_repository.get_stock_performance_by_symbol(stock_symbol)
        )
        competitors = self.scraping_stock_repository.get_stock_competitors_by_symbol(
            stock_symbol=stock_symbol
        )

        return_data = {
            "status": daily_open_close_data.get("status"),
            "request_data": daily_open_close_data.get("from"),
            "company_code": daily_open_close_data.get("symbol"),
            "company_name": self.scraping_stock_repository.get_company_name_by_symbol(
                stock_symbol=stock_symbol
            ),
            "stock_values": stock_values,
            "performance_data": performance_data,
            "competitors": competitors,
        }

        return return_data

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import List

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
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

from app.app_config import Settings
from app.common.currency_utils import convert_currency_string
from app.models.dto.stock_response import (
    CompetitorData,
    PerformanceData,
)

logger: logging.Logger = logging.getLogger()
OPEN_CLOSE_ENDPOINT = (
    "/v1/open-close/{stock_symbol}/{date}?adjusted=true&apiKey={api_key}"
)
STOCK_DETAILS_ENDPOINT = "/investing/stock/{stock_symbol}"
executor = ThreadPoolExecutor(max_workers=5)


class CatchByBotDetectionError(Exception): ...


class MarketWatchRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings

    @property
    def _chrome_options(self) -> Options:
        options = webdriver.ChromeOptions()
        if self.settings.selenium_headless_mode:
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
        driver = webdriver.Remote(
            command_executor=self.settings.remote_chrome_webdriver_address,
            options=self._chrome_options,
        )
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

    async def _async_get_stock_page_html(self, stock_symbol: str) -> BeautifulSoup:
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor, self._get_stock_page_html, stock_symbol
        )

    async def get_stock_performance_by_symbol(
        self, stock_symbol: str
    ) -> PerformanceData:
        stock_page: BeautifulSoup = await self._async_get_stock_page_html(stock_symbol)
        performance_div = stock_page.find("div", class_="performance")
        table_rows = performance_div.find_all("tr", class_="table__row")

        performance_data = {
            table_row.find("td").text: table_row.find("li").text.replace("%", "")
            for table_row in table_rows
        }

        return PerformanceData.model_validate(performance_data)

    async def get_stock_competitors_by_symbol(
        self, stock_symbol: str
    ) -> list[CompetitorData]:
        stock_page: BeautifulSoup = await self._async_get_stock_page_html(stock_symbol)
        competitors_div = stock_page.find("div", class_="Competitors")
        table_rows = competitors_div.find("tbody").find_all("tr")
        return [
            CompetitorData.model_validate(
                {
                    "name": table_row.find("a", class_="link").text,
                    "market_cap": convert_currency_string(
                        table_row.find_all("td")[2].text
                    ),
                }
            )
            for table_row in table_rows
        ]

    async def get_company_name_by_symbol(self, stock_symbol: str) -> str:
        stock_page: BeautifulSoup = await self._async_get_stock_page_html(stock_symbol)
        return stock_page.find("h1", class_="company__name").text

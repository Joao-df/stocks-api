import asyncio
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Any, ClassVar, List

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
OPEN_CLOSE_ENDPOINT = "/v1/open-close/{stock_symbol}/{date}?adjusted=true&apiKey={api_key}"
STOCK_DETAILS_ENDPOINT = "/investing/stock/{stock_symbol}"
INITIAL_COOKIES_VALUE: list[dict[str, Any]] = [
    {
        "domain": ".marketwatch.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "datadome",
        "path": "/",
        "sameSite": "Lax",
        "secure": True,
        "session": False,
        "storeId": "0",
        "value": "Zx~2lSVM4otlHRuJdSmuaWEFopnrcmo5f58eaqgvFdj3iSVkbdNzEuaVjIVPpZoiAR_n3obvgc7vzjrDTaJs163lH5vb2Pz6qlOWA0PXuuZ4wvL3z8QZplcsCZwUGAaV",
    },
]


class CatchByBotDetectionError(Exception): ...


class MarketWatchRepositoryInterface(ABC):
    @abstractmethod
    async def get_stock_performance_by_symbol(self, stock_symbol: str) -> PerformanceData:
        """
        Retrieves the performance data for a stock symbol.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve performance data for.

        Returns:
            PerformanceData: An object containing performance data for the stock symbol.
        """

    @abstractmethod
    async def get_stock_competitors_by_symbol(self, stock_symbol: str) -> list[CompetitorData]:
        """Retrieve a list of competitor data for a given stock symbol.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve competitors for.

        Returns:
            list[CompetitorData]: A list of CompetitorData objects containing competitor names and market capitalizations.
        """

    @abstractmethod
    async def get_company_name_by_symbol(self, stock_symbol: str) -> str:
        """
        Retrieve the company name associated with the given stock symbol.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve the company name for.

        Returns:
            str: The company name.
        """


class MarketWatchRepository(MarketWatchRepositoryInterface):
    cookies: ClassVar[list[dict[str, Any]] | None] = INITIAL_COOKIES_VALUE

    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings

    @property
    def _chrome_options(self) -> Options:
        """
        Returns the Chrome options based on the settings configuration.
        Includes arguments for headless mode, incognito mode, user agent, and automation control.
        Utilized by the MarketWatchRepository class for web scraping operations.
        """
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
        logger.debug("User agent: %s", user_agent)
        options.add_argument(f"--user-agent={user_agent}")

        return options

    def _close_subscriber_banner(self, driver: webdriver.Chrome) -> None:
        """
        Closes the subscriber banner if it is displayed on the webpage.

        Args:
            driver (webdriver.Chrome): The Chrome driver instance used to access the webpage.
        """
        try:
            banner: WebElement = driver.find_element(By.ID, "cx-scrim-wrapper")
        except NoSuchElementException:
            return
        else:
            if banner.is_displayed():
                close_banner_btn: WebElement = banner.find_element(By.CLASS_NAME, "close-btn")
                if close_banner_btn.is_displayed():
                    close_banner_btn.click()

    def _is_captcha_open(self, driver: webdriver.Chrome) -> bool:
        """
        Checks if a CAPTCHA script is present on the webpage loaded by the provided Chrome driver.

        Args:
            driver (webdriver.Chrome): The Chrome driver instance used to access the webpage.

        Returns:
            bool: True if a CAPTCHA script is found, False otherwise.
        """
        return "captcha-delivery" in driver.page_source

    def _set_cookies(self, driver: webdriver.Chrome) -> None:
        """
        Sets cookies for the provided Chrome driver by adding cookies from the MarketWatchRepository class if available.

        Args:
            driver (webdriver.Chrome): The Chrome driver instance to set cookies for.
        """
        driver.get(self.settings.marketwatch_base_url)
        if (cookies := MarketWatchRepository.cookies) is not None:
            for cookie in cookies:
                driver.add_cookie(cookie)

    def _save_cookies(self, driver: webdriver.Chrome) -> None:
        """
        Save the cookies from the WebDriver to the MarketWatchRepository class variable.

        Args:
            driver (webdriver.Chrome): The Chrome WebDriver instance.
        """
        MarketWatchRepository.cookies = driver.get_cookies()

    @lru_cache
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random(min=1, max=2),
        retry=retry_if_exception_type(CatchByBotDetectionError),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
    )
    def _get_stock_page_html(self, stock_symbol: str) -> BeautifulSoup:
        """
        Retrieves the HTML content of a stock page using the provided stock symbol.
        Utilizes caching and retry mechanisms with a maximum of 10 attempts.
        Handles bot detection errors and closes subscriber banners if necessary.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve the page for.

        Returns:
            BeautifulSoup: The parsed HTML content of the stock page.
        """
        with webdriver.Remote(
            command_executor=self.settings.remote_chrome_webdriver_address,
            options=self._chrome_options,
        ) as driver:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.maximize_window()
            driver.set_page_load_timeout(60)
            self._set_cookies(driver)
            uri: str = f"{self.settings.marketwatch_base_url}{STOCK_DETAILS_ENDPOINT.format(stock_symbol=stock_symbol)}"
            driver.get(uri)

            if self._is_captcha_open(driver):
                logger.warning("Catch by bot detection.")
                raise CatchByBotDetectionError()

            self._close_subscriber_banner(driver)
            page_html: str = driver.page_source
            self._save_cookies(driver)
            return BeautifulSoup(page_html, "html.parser")

    async def _async_get_stock_page_html(self, stock_symbol: str) -> BeautifulSoup:
        """Asynchronously retrieves the HTML content of a stock page using a provided stock symbol.

        Args:
            stock_symbol (str): The symbol of the stock to retrieve the page for.

        Returns:
            BeautifulSoup: The parsed HTML content of the stock page.
        """
        executor = ThreadPoolExecutor(max_workers=5)
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(executor, self._get_stock_page_html, stock_symbol)
        finally:
            executor.shutdown(wait=True)

    async def get_stock_performance_by_symbol(self, stock_symbol: str) -> PerformanceData:
        stock_page: BeautifulSoup = await self._async_get_stock_page_html(stock_symbol)
        performance_div = stock_page.find("div", class_="performance")
        table_rows = performance_div.find_all("tr", class_="table__row")

        performance_data = {
            table_row.find("td").text: table_row.find("li").text.replace("%", "") for table_row in table_rows
        }

        return PerformanceData.model_validate(performance_data)

    async def get_stock_competitors_by_symbol(self, stock_symbol: str) -> list[CompetitorData]:
        competitors_class = "Competitors"
        logger.info(f"Retrieving competitors for stock symbol: {stock_symbol}")
        stock_page: BeautifulSoup = await self._async_get_stock_page_html(stock_symbol)
        competitors_div = stock_page.find("div", class_=competitors_class)
        table_rows = competitors_div.find("tbody").find_all("tr")
        competitors_data: List[CompetitorData] = [
            CompetitorData.model_validate(
                {
                    "name": table_row.find("a", class_="link").text,
                    "market_cap": convert_currency_string(table_row.find_all("td")[2].text),
                }
            )
            for table_row in table_rows
        ]
        logger.info(f"Retrieved {len(competitors_data)} competitors for stock symbol: {stock_symbol}")
        return competitors_data

    async def get_company_name_by_symbol(self, stock_symbol: str) -> str:
        stock_page: BeautifulSoup = await self._async_get_stock_page_html(stock_symbol)
        return stock_page.find("h1", class_="company__name").text

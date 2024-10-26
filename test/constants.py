from datetime import date

from app.models.dto.daily_open_close_stock import DailyOpenCloseStock
from app.models.dto.stock_response import CompetitorData, MarketCapData, PerformanceData, StockData

AAPL_DAILY_OPEN_CLOSE_STOCK = DailyOpenCloseStock(
    status="OK",
    date="2023-10-01",
    symbol="AAPL",
    open=150.0,
    high=155.0,
    low=149.0,
    close=154.0,
    volume=1000000,
    preMarket=156.0,
    afterHours=157.0,
)
AAPL_PERFORMANCE_DATA = PerformanceData(
    five_days=1.5, one_month=3.0, three_months=5.0, year_to_date=10.0, one_year=15.0
)
AAPL_COMPANY_NAME = "Apple Inc."
AAPL_PURCHASES_AMOUNT = 100.0
AAPL_COMPETITORS: list[CompetitorData] = [
    CompetitorData(name="Competitor1", market_cap=MarketCapData(currency="$", value=123_000_000))
]
AAPL_EXPECTED_STOCK: StockData = StockData.model_validate(
    {
        "status": "OK",
        "purchased_amount": 100,
        "purchased_status": "OK",
        "request_data": date(2023, 10, 1),
        "company_code": "AAPL",
        "company_name": "Apple Inc.",
        "stock_values": {"open": 150.0, "high": 155.0, "low": 149.0, "close": 154.0},
        "performance_data": {
            "five_days": 1.5,
            "one_month": 3.0,
            "three_months": 5.0,
            "year_to_date": 10.0,
            "one_year": 15.0,
        },
        "competitors": [{"name": "Competitor1", "market_cap": {"currency": "$", "value": 123000000.0}}],
    }
)


GE_DAILY_OPEN_CLOSE_STOCK = DailyOpenCloseStock(
    status="OK",
    date="2023-10-02",
    symbol="GE",
    open=151.0,
    high=156.0,
    low=150.0,
    close=155.0,
    volume=2000000,
    preMarket=157.0,
    afterHours=158.0,
)
GE_PERFORMANCE_DATA = PerformanceData(five_days=2.5, one_month=4.0, three_months=6.0, year_to_date=11.0, one_year=16.0)
GE_COMPANY_NAME = "GE Aerospace"
GE_PURCHASES_AMOUNT = 0.0
GE_COMPETITORS: list[CompetitorData] = [
    CompetitorData(name="Competitor1", market_cap=MarketCapData(currency="$", value=124000000)),
    CompetitorData(name="Competitor2", market_cap=MarketCapData(currency="R$", value=12000000)),
]
GE_EXPECTED_STOCK: StockData = StockData.model_validate(
    {
        "status": "OK",
        "purchased_amount": 0.0,
        "purchased_status": "OK",
        "request_data": date(2023, 10, 2),
        "company_code": "GE",
        "company_name": "GE Aerospace",
        "stock_values": {"open": 151.0, "high": 156.0, "low": 150.0, "close": 155.0},
        "performance_data": {
            "five_days": 2.5,
            "one_month": 4.0,
            "three_months": 6.0,
            "year_to_date": 11.0,
            "one_year": 16.0,
        },
        "competitors": [
            {"name": "Competitor1", "market_cap": {"currency": "$", "value": 124000000.0}},
            {"name": "Competitor2", "market_cap": {"currency": "R$", "value": 12000000.0}},
        ],
    }
)

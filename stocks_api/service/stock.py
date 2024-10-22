from datetime import date

import requests

from stocks_api.models.stock.stock import Stock

OPEN_CLOSE_ENDPOINT = "open-close/{stock_symbol}/{date}"


class StockService:
    def __init__(self, polygon_base_url: str, polygon_api_key: str) -> None:
        self.polygon_base_url: str = polygon_base_url
        self.polygon_api_key: str = polygon_api_key

    def get_stock_by_symbol(self, stock_symbol: str, date: date) -> Stock:
        uri: str = f"{self.polygon_base_url}{OPEN_CLOSE_ENDPOINT.format(stock_symbol=stock_symbol, date=date)}?adjusted=true&apiKey={self.polygon_api_key}"

        response_data: requests.Response = requests.get(uri)

        response_data_json = response_data.json()

        return_data = {
            "status": response_data_json.get("status"),
            "request_data": response_data_json.get("from"),
            "company_code": response_data_json.get("symbol"),
            "stock_values": {
                "open": response_data_json.get("open"),
                "high": response_data_json.get("high"),
                "low": response_data_json.get("low"),
                "close": response_data_json.get("close"),
            },
        }

        return return_data

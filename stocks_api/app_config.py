from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    polygon_api_key: str
    polygon_base_url: str = "https://api.polygon.io"
    marketwatch_base_url: str = "https://www.marketwatch.com"
    remote_chrome_webdriver_address: str = "http://chrome:4444"
    selenium_headless_mode: bool = True
    redis_url: str = "redis://cache"
    default_caching_time: int = 60

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()

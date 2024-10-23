from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    polygon_api_key: str
    polygon_base_url: str = "https://api.polygon.io"
    marketwatch_base_url: str = "https://www.marketwatch.com"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()

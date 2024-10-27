from functools import partial
from typing import Any

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from app.app_config import Settings, get_settings

settings: Settings = get_settings()


async def init_cache() -> None:
    """
    Initialize the cache using the provided Redis URL and set the cache prefix to 'fastapi-cache'.

    This function connects to the Redis server using the URL specified in the settings and initializes the FastAPI cache with the Redis backend.
    """
    redis: aioredis.Redis[Any] = aioredis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


default_cache = partial(cache, settings.default_caching_time)

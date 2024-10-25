from functools import partial
from typing import Any

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from stocks_api.app_config import Settings, get_settings

settings: Settings = get_settings()


async def init_cache() -> None:
    redis: aioredis.Redis[Any] = aioredis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


default_cache = partial(cache, settings.default_caching_time)

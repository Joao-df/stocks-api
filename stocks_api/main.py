import logging
import time
from collections.abc import Callable
from logging.config import dictConfig
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager

from stocks_api.cache import init_cache
from stocks_api.log_config import LogConfig
from stocks_api.router.stock import router as stock_router

dictConfig(LogConfig().model_dump())
logger: logging.Logger = logging.getLogger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_cache()
    yield


app = FastAPI(title="stocks", lifespan=lifespan)


@app.middleware("http")
async def log_endpoint_start_and_end(
    request: Request, call_next: Callable[[Request], Any]
) -> Any:
    method: str = request.method
    endpoint: str = request.url.path
    logger.info("[START] %s: %s", method, endpoint)
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(f"[END] {method}: {endpoint} finished in {process_time:.2f} seconds")
    return response


app.include_router(stock_router)

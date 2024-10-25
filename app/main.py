import logging
import time
from collections.abc import Callable
from logging.config import dictConfig
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager

from app.cache import init_cache
from app.database import sessionmanager
from app.log_config import LogConfig
from app.stocks.stock_router import router as stock_router

dictConfig(LogConfig().model_dump())
logger: logging.Logger = logging.getLogger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_cache()
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(title="stocks", lifespan=lifespan)


@app.middleware("http")
async def log_endpoint_start_and_end(request: Request, call_next: Callable[[Request], Any]) -> Any:
    method: str = request.method
    endpoint: str = request.url.path
    logger.info("[START] %s: %s", method, endpoint)
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(f"[END] {method}: {endpoint} finished in {process_time:.2f} seconds")
    return response


app.include_router(stock_router)

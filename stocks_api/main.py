from fastapi import FastAPI

from stocks_api.router.stock import router as stock_router

app = FastAPI()

app.include_router(stock_router)

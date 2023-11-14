from fastapi import FastAPI
from routers import stocks

app = FastAPI()
app.include_router(stocks.router)
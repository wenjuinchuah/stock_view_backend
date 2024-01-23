from fastapi import FastAPI

import app.api.dependencies.database as db
import app.api.endpoints.price_list as PriceListEndpoint
import app.api.endpoints.stock as StockEndpoint
from app.api.dependencies.database import engine

app = FastAPI()

db.Base.metadata.create_all(bind=engine)


app.include_router(StockEndpoint.router)
app.include_router(PriceListEndpoint.router)

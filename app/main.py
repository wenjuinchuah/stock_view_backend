from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import app.api.dependencies.database as db
import app.api.endpoints.price_list as PriceListEndpoint
import app.api.endpoints.stock as StockEndpoint
import app.api.endpoints.stock_screener as StockScreenerEndpoint
from app.api.dependencies.database import engine

app = FastAPI()

db.Base.metadata.create_all(bind=engine)

# Add middleware to enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(StockEndpoint.router)
app.include_router(PriceListEndpoint.router)
app.include_router(StockScreenerEndpoint.router)

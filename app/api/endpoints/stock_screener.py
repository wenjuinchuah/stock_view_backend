from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.api.crud.stock_screener as StockScreenerCRUD
from app.api.constants import Response
from app.api.dependencies.database import SessionLocal
from app.api.models.stock_screener import StockScreener


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/api/v1/stock_screener",
    tags=["Stock Screener"],
)


@router.post("/screen", status_code=status.HTTP_200_OK)
async def screen_stock(stock_screener: StockScreener, db: db_dependency):
    try:
        stock_screener_result = await StockScreenerCRUD.screen_stock(stock_screener, db)
        return Response.success(stock_screener_result)
    except Exception as e:
        return Response.error(e)


@router.get("/available_rules/get", status_code=status.HTTP_200_OK)
def get_available_rules(db: db_dependency):
    try:
        rules = StockScreenerCRUD.get_available_rules()
        return Response.success(rules)
    except Exception as e:
        return Response.error(e)


@router.get("/indicator_selector/get", status_code=status.HTTP_200_OK)
def get_indicator_selector(db: db_dependency):
    try:
        indicator_selector = StockScreenerCRUD.get_indicator_selector()
        return Response.success(indicator_selector)
    except Exception as e:
        return Response.error(e)

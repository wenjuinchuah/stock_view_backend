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
    prefix="/stock_screener",
    tags=["Stock Screener"],
)


@router.post("/screen", status_code=status.HTTP_200_OK)
async def screen_stock(stock_screener: StockScreener, db: db_dependency):
    try:
        stock_screener_result = StockScreenerCRUD.screen_stock(stock_screener, db)
        return Response.success(stock_screener_result)
    except Exception as e:
        raise Response.error(e)

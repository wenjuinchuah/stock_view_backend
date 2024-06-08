from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

import app.api.crud.price_list as PriceListCRUD
import app.api.crud.stock as StockCRUD
from app.api.constants import Response, TimePeriod
from app.api.dependencies.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/api/v1/stock",
    tags=["Stock"],
)


@router.get("/get", status_code=status.HTTP_200_OK)
def get_stock_by_stock_code(
    db: db_dependency,
    stock_code: str | None = None,
    auto_adjust: bool = True,
    time_period: str | None = TimePeriod.one_year,
):
    try:
        if stock_code is None or stock_code == "":
            raise Exception("Stock code is required")

        price_list = PriceListCRUD.get_price_list(
            stock_code, auto_adjust, time_period, db
        )

        return Response.success(price_list)
    except Exception as e:
        return Response.error(e)


@router.get("/details/get", status_code=status.HTTP_200_OK)
def get_stock_details(db: db_dependency, stock_code: str | None = None):
    try:
        if stock_code is None or stock_code == "":
            raise Exception("Stock code is required")

        stock_details = StockCRUD.get_stock_details(db, stock_code)

        return Response.success(stock_details)
    except Exception as e:
        return Response.error(e)


@router.get("/search", status_code=status.HTTP_200_OK)
def get_matched_stock_details(db: db_dependency, query: str | None):
    try:
        if query is None or query == "":
            raise Exception("Query string is required")

        matched_stock_details = StockCRUD.get_matched_stock_details(db, query)

        return Response.success(matched_stock_details)
    except Exception as e:
        return Response.error(e)


@router.post("/update", status_code=status.HTTP_200_OK)
async def update_stock(db: db_dependency):
    try:
        counter = await StockCRUD.update_stock(db)
        return Response.success(f"{counter} stock(s) added/updated successfully")
    except Exception as e:
        return Response.error(e)

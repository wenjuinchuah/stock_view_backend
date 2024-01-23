from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

import app.api.crud.stock as crud
from app.api.constants import Response
from app.api.dependencies.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
)


# @router.get("/get", status_code=status.HTTP_200_OK)
# def get_stock_by_stock_code(
#     db: db_dependency, stock_code: str | None = None, auto_adjust: bool = True
# ):
#     try:
#         if stock_code is None or stock_code == "":
#             raise Exception("Stock code is required")
#
#         stock_ticker = crud.get_stock_ticker_data(stock_code, auto_adjust)
#         return Response.success(stock_ticker)
#     except Exception as e:
#         return Response.error(e)


@router.post("/update", status_code=status.HTTP_200_OK)
async def update_stock(db: db_dependency):
    try:
        counter = await crud.update_stock(db)
        return Response.success(f"{counter} stock(s) added/updated successfully")
    except Exception as e:
        return Response.error(e)

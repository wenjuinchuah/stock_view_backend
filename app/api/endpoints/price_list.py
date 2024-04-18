from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

import app.api.crud.price_list as crud
import app.api.crud.utils as Utils
from app.api.constants import Response
from app.api.dependencies.database import SessionLocal
from app.api.models.base import PriceListBase


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/api/v1/price_list",
    tags=["Price List"],
)


@router.post("/update", status_code=status.HTTP_200_OK)
async def update_price_list(db: db_dependency):
    try:
        counter = await crud.update(db)
        return Response.success(f"{counter} price list added/updated successfully")
    except Exception as e:
        return Response.error(e)


@router.get("/is_after_trading_hour/get", status_code=status.HTTP_200_OK)
def is_after_trading_hour(db: db_dependency):
    try:
        is_valid = Utils.is_after_trading_hour(db, PriceListBase.datetime)
        return Response.success(is_valid)
    except Exception as e:
        return Response.error(e)

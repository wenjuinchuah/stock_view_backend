from typing import Annotated
from asyncio import Lock

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

import app.api.crud.price_list as crud
import app.api.crud.utils as Utils
from app.api.constants import Response
from app.api.dependencies.database import SessionLocal
from app.api.models.base import PriceListBase


lock = Lock()


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
        if lock.locked():
            raise Exception("Price list update is in progress, please try again later!")
        else:
            async with lock:
                counter = await crud.update(db)
                return Response.success(
                    f"{counter} price list added/updated successfully"
                )
    except Exception as e:
        return Response.error(e)


@router.get("/is_after_trading_hour", status_code=status.HTTP_200_OK)
def is_after_trading_hour(db: db_dependency):
    try:
        is_valid = Utils.is_after_trading_hour(db)
        return Response.success(is_valid)
    except Exception as e:
        return Response.error(e)


@router.get("/is_data_available", status_code=status.HTTP_200_OK)
def is_data_available(db: db_dependency):
    try:
        is_available = crud.is_data_available(db)
        return Response.success(is_available)
    except Exception as e:
        return Response.error(e)


@router.get("/get_last_updated_price_list_index", status_code=status.HTTP_200_OK)
def get_last_updated_price_list_index(db: db_dependency):
    try:
        stock_index = crud.get_last_updated_price_list_data(db)
        return Response.success(stock_index)
    except Exception as e:
        return Response.error(e)

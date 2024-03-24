import asyncio

from sqlalchemy import func
from stock_indicators import Quote

import app.api.crud.stock as StockCRUD
import app.api.crud.utils as Utils
from app.api.models.base import PriceListBase
from app.api.models.price_list import PriceList


async def fetch(stock_code: str, period: str, db) -> list[PriceList]:
    print(f"Fetching price list data for {stock_code}", end="\r")

    price_list_data = []

    # Get price list data
    latest_date = (
        db.query(func.max(PriceListBase.datetime))
        .filter(PriceListBase.pricelist_id.startswith(stock_code))
        .scalar()
    )
    start_date = latest_date + 86400 if latest_date else None
    if start_date:
        price_list_data = StockCRUD.get_price_list_data(
            stock_code,
            start_date=Utils.datetime_now_from_timestamp(start_date),
            end_date=Utils.datetime_now(),
        )
    else:
        price_list_data = StockCRUD.get_price_list_data(stock_code, period=period)

    # Add new rows if they don't already exist
    for data in price_list_data:
        existing_row = db.query(PriceListBase).filter_by(pricelist_id=data.pricelist_id).first()
        if not existing_row:
            # Save to database
            db.add(data.to_base())

    db.commit()

    return price_list_data


async def update(db) -> int:
    period = "max"
    query = db.query(func.max(PriceListBase.datetime))

    # Condition check
    if Utils.db_data_days_diff(query, days=0) or (
        Utils.db_data_days_diff(query, days=1) and not Utils.is_after_trading_hour()
    ):
        return 0

    all_stock_code = StockCRUD.get_all_stock_code(db)
    tasks = [fetch(stock_code, period, db) for stock_code in all_stock_code]
    completed_tasks = await asyncio.gather(*tasks)

    return sum(len(price_list_data) for price_list_data in completed_tasks)


def get(stock_code: str, db):
    print(f"Fetching price list data for {stock_code}", end="\r")
    return (
        db.query(PriceListBase)
        .filter(PriceListBase.pricelist_id.startswith(stock_code))
        .all()
    )


def get_price_list(stock_code: str, db) -> list[PriceList]:
    data_list = get(stock_code, db)
    return [data.to_price_list() for data in data_list]


def get_quote_list_with_start_end_date(
    stock_code: str, start_date: int, end_date: int, db
) -> list[Quote]:
    data_list = get(stock_code, db)

    return [
        data.to_quote()
        for data in data_list
        if start_date - (86400 * 40) <= data.datetime <= end_date
    ]

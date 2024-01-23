import asyncio
from datetime import datetime, timedelta

import pytz
from sqlalchemy import func

import app.api.crud.stock as StockCRUD
from app.api.models.base import Stock, PriceList


async def fetch_price_list_data(stock_code: str, period: str, db) -> list[PriceList]:
    print(f"Fetching price list data for {stock_code}")
    price_list_data = StockCRUD.get_price_list_data(stock_code, period)

    existing_record_ids = (
        db.query(PriceList.pricelist_id)
        .filter(PriceList.pricelist_id.like(f"{stock_code}_%"))
        .all()
    )
    existing_record_ids = [record_id[0] for record_id in existing_record_ids]

    if price_list_data:
        price_list_data = [
            data
            for data in price_list_data
            if data.pricelist_id not in existing_record_ids
        ]

        db.bulk_save_objects(price_list_data)
        db.commit()

    return price_list_data


async def update_price_list(db) -> int:
    start_time = datetime.now()

    # End of KLSE's stock trading hours is 5pm GMT+8
    end_trading_hours = (
        datetime.now().replace(hour=17, minute=0, second=0, microsecond=0).time()
    )
    current_time = datetime.now().time()
    price_list_data = []
    period = "max"

    # Condition 1: Check if the last updated datetime is today
    existing_record_timestamp = db.query(func.max(PriceList.datetime)).scalar()
    existing_record_datetime = (
        datetime.fromtimestamp(
            existing_record_timestamp, tz=pytz.timezone("Asia/Kuala_Lumpur")
        )
        if existing_record_timestamp
        else None
    )
    if (
        existing_record_datetime
        and existing_record_datetime.date() == datetime.today().date()
    ):
        period = "5d"
        return len(price_list_data)

    # Condition 2: Check if the last updated date is not today and the current time is after 5pm
    is_update_needed = not existing_record_datetime or (
        existing_record_datetime.date() < datetime.today().date()
        and (
            current_time > end_trading_hours
            or (datetime.today().date() - existing_record_datetime.date())
            > timedelta(days=1)
        )
    )

    if not existing_record_datetime or is_update_needed:
        all_stock_code = db.query(Stock.stock_code).all()
        all_stock_code = [stock_code[0] for stock_code in all_stock_code]

        tasks = [
            fetch_price_list_data(stock_code, period, db)
            for stock_code in all_stock_code
        ]
        completed_tasks = await asyncio.gather(*tasks)

        end_time = datetime.now()
        print(f"Time taken: {end_time - start_time}")

        return sum(len(price_list_data) for price_list_data in completed_tasks)

    return len(price_list_data)

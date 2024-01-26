import asyncio
import logging

from sqlalchemy import func

import app.api.crud.common as common
import app.api.crud.stock as StockCRUD
from app.api.models.base import PriceListBase
from app.api.models.price_list import PriceList


async def fetch_price_list_data(stock_code: str, period: str, db) -> list[PriceList]:
    logging.info(f"Fetching price list data for {stock_code}")
    price_list_data = StockCRUD.get_price_list_data(stock_code, period)

    existing_record_ids = (
        db.query(PriceListBase.pricelist_id)
        .filter(PriceListBase.pricelist_id.like(f"{stock_code}_%"))
        .all()
    )
    existing_record_ids = [record_id[0] for record_id in existing_record_ids]

    if price_list_data:
        price_list_data = [
            data
            for data in price_list_data
            if data.pricelist_id not in existing_record_ids
        ]

        db.bulk_save_objects([data.to_price_list() for data in price_list_data])
        db.commit()

    return price_list_data


async def update_price_list(db) -> int:
    period = "max"
    price_list_data = []
    query = db.query(func.max(PriceListBase.datetime))

    # Condition check
    if common.db_data_days_diff(query, days=0) or (
        common.db_data_days_diff(query, days=1) and not common.is_after_trading_hour()
    ):
        period = "5d"
        return len(price_list_data)

    all_stock_code = StockCRUD.get_all_stock_code(db)

    tasks = [
        fetch_price_list_data(stock_code, period, db) for stock_code in all_stock_code
    ]
    completed_tasks = await asyncio.gather(*tasks)

    return sum(len(price_list_data) for price_list_data in completed_tasks)


def get_price_list_data(stock_code: str, db) -> list[PriceList]:
    price_list_data = (
        db.query(PriceListBase).filter(PriceListBase.stock_code == stock_code).all()
    )

    return [data.to_price_list() for data in price_list_data]

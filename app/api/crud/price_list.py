import asyncio
import time

import aiohttp
import pandas as pd
import yfinance as yf
from sqlalchemy import func
from stock_indicators import Quote
from io import StringIO

import app.api.crud.stock as StockCRUD
import app.api.crud.utils as Utils
from app.api.models.base import PriceListBase
from app.api.models.price_list import PriceList


async def fetch(stock_code: str, period: str, db) -> list[PriceList]:
    print(f"Fetching price list data for {stock_code}  ", end="\r")

    price_list_data = []

    # Get price list data
    latest_date = (
        db.query(func.max(PriceListBase.datetime))
        .filter(PriceListBase.pricelist_id.startswith(stock_code))
        .scalar()
    )
    start_date = latest_date + 86400 if latest_date else None
    if start_date:
        price_list_data = await get_price_list_data(
            stock_code,
            start_date=start_date,
            end_date=Utils.timestamp_now(),
        )
    else:
        price_list_data = await get_price_list_data(stock_code, period=period)

    # Add new rows if they don't already exist
    new_rows = [
        data.to_base()
        for data in price_list_data
        if not db.query(PriceListBase).filter_by(pricelist_id=data.pricelist_id).first()
    ]

    db.bulk_save_objects(new_rows)
    db.commit()

    return price_list_data


async def update(db) -> int:
    period = "max"

    if not is_after_trading_hour(db):
        return 0

    all_stock_code = StockCRUD.get_all_stock_code(db)
    tasks = [fetch(stock_code, period, db) for stock_code in all_stock_code]
    completed_tasks = await asyncio.gather(*tasks)

    return sum(len(price_list_data) for price_list_data in completed_tasks)


def get(stock_code: str, db):
    print(f"Fetching price list data for {stock_code}  ", end="\r")
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

    # Return data 90 days before start_date to speed up the screening process
    return [
        data.to_quote()
        for data in data_list
        if start_date - (86400 * 90) <= data.datetime <= end_date
    ]


async def get_price_list_data(
    stock_code: str,
    auto_adjust: bool | None = True,
    period: str | None = "1y",
    start_date: int | None = None,
    end_date: int | None = None,
) -> list[PriceList]:
    price_list = []

    req = yf.Ticker(f"{stock_code}.KL")
    if start_date and end_date:
        stock_df = req.history(start=start_date, end=end_date, auto_adjust=auto_adjust)
    else:
        stock_df = req.history(period=period, auto_adjust=auto_adjust)

    # fill NaN with -1
    stock_df = stock_df.fillna(-1)

    for index, row in stock_df.iterrows():
        timestamp = int(index.timestamp())
        price_list.append(
            PriceList(
                pricelist_id=f"{stock_code}_{timestamp}",
                open=round(row["Open"], 5),
                close=-1,
                adj_close=round(row["Close"], 5),
                high=round(row["High"], 5),
                low=round(row["Low"], 5),
                volume=int(row["Volume"]),
                datetime=timestamp,
                stock_code=stock_code,
            )
        )
    return price_list


def is_after_trading_hour(db) -> bool:
    query = db.query(func.max(PriceListBase.datetime))
    if Utils.db_data_days_diff(query, days=0) or (
        Utils.db_data_days_diff(query, days=1) and not Utils.is_after_trading_hour()
    ):
        return False

    return True

import asyncio
from datetime import datetime

import pandas as pd
import yfinance as yf
from stock_indicators import Quote

import app.api.crud.stock as StockCRUD
import app.api.crud.utils as Utils
from app.api.constants import TimePeriod
from app.api.models.base import PriceListBase, StockBase
from app.api.models.price_list import PriceList


# Fetch price list data for a stock code
async def fetch(stock_code: str, period: str, db) -> list[PriceListBase]:
    print(f"Fetching price list data for {stock_code}  ", end="\r")

    price_list_data = []
    new_rows = []

    # Get price list data
    latest_timestamp = PriceListBase.get_latest_timestamp_by_stock_code(db, stock_code)
    start_timestamp = latest_timestamp + 86400 if latest_timestamp else None
    if start_timestamp:
        price_list_data = await get_price_list_data(
            stock_code,
            start_date=Utils.timestamp_to_datetime(start_timestamp),
            end_date=Utils.datetime_now(),
        )
        # Add new rows if they don't already exist
        new_rows = [
            data
            for data in price_list_data
            if not PriceListBase.get(db, data.pricelist_id)
        ]
    else:
        price_list_data = await get_price_list_data(stock_code, period=period)
        new_rows = price_list_data

    # Bulk save new rows to the database
    PriceListBase.bulk_update(db, new_rows)

    return price_list_data


# Update price list data for all stock codes
async def update(db) -> int:
    period = "max"

    # Get all stock codes
    all_stock_code = StockCRUD.get_all_stock_code(db)

    # Fetch price list data for all stock codes
    tasks = [fetch(stock_code, period, db) for stock_code in all_stock_code]
    completed_tasks = await asyncio.gather(*tasks)

    return sum(len(price_list_data) for price_list_data in completed_tasks)


# Get price list data for a stock code
def get(stock_code: str, db) -> list[PriceList]:
    print(f"Getting price list data for {stock_code}  ", end="\r")
    price_list = PriceListBase.get_all_by_stock_code(db, stock_code)
    return [
        data.to_price_list()
        for data in price_list
        if data.stock_code == stock_code and data.volume > 0
    ]


# Get price list data for a stock code with time period and auto adjust
def get_price_list(
    stock_code: str, auto_adjust: bool, time_period: str, db
) -> list[PriceList]:
    price_list = get(stock_code, db)

    if price_list:
        # Sort by timestamp
        price_list = sorted(price_list, key=lambda x: x.timestamp)
        # Adjust price list if auto_adjust is True (Calculated instead of using adjusted_close in database)
        price_list = adjust_price_list(price_list) if auto_adjust else price_list

        return price_list_time_period(price_list, time_period)

    return []


# Get quote list for a stock code
def get_quote_list(stock_code: str, start_date: int, end_date: int, db) -> list[Quote]:
    price_list = get(stock_code, db)

    # Filter data before start_date to speed up the screening process
    return [
        data.to_base().to_quote()
        for data in price_list
        if start_date <= Utils.to_local_timestamp(data.timestamp) <= end_date
    ]


# Get price list data for a stock code
async def get_price_list_data(
    stock_code: str,
    period: str | None = "1y",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[PriceListBase]:
    tickers = (f"{stock_code}.KL",)

    if start_date and end_date:
        stock_df = yf.download(tickers, start=start_date, end=end_date, progress=False)
    else:
        stock_df = yf.download(tickers, period=period, progress=False)

    # fill NaN with -1 /
    if stock_df.empty:
        return []

    data = stock_df.reset_index()
    data = data.to_dict("records")

    return (
        pd.DataFrame(data)
        .apply(lambda record: create_price_list(record, stock_code), axis=1)
        .to_list()
    )


def create_price_list(record, stock_code: str) -> PriceListBase:
    timestamp = Utils.datetime_to_timestamp(record["Date"])
    return PriceListBase(
        pricelist_id=f"{stock_code}_{timestamp}",
        open=round(record["Open"], 5),
        close=round(record["Close"], 5),
        adj_close=round(record["Adj Close"], 5),
        high=round(record["High"], 5),
        low=round(record["Low"], 5),
        volume=int(record["Volume"]),
        timestamp=timestamp,
        stock_code=stock_code,
    )


# Adjust price list data
def adjust_price_list(price_list: list[PriceList]) -> list[PriceList]:
    for i in range(0, len(price_list)):
        price_list[i].open = (
            price_list[i].open * price_list[i].adj_close
        ) / price_list[i].close

        price_list[i].high = (
            price_list[i].high * price_list[i].adj_close
        ) / price_list[i].close

        price_list[i].low = (price_list[i].low * price_list[i].adj_close) / price_list[
            i
        ].close

        price_list[i].volume = (
            price_list[i].volume / price_list[i].adj_close / price_list[i].close
        ).__int__()

        price_list[i].timestamp = price_list[i].timestamp

        price_list[i].close = price_list[i].adj_close

    return price_list


# Filter price list data by time period
def price_list_time_period(
    price_list: list[PriceList], time_period: str
) -> list[PriceList]:
    shift_month, shift_year = [0, 0]

    match time_period:
        case TimePeriod.one_month:
            shift_month = 1
        case TimePeriod.three_months:
            shift_month = 3
        case TimePeriod.six_months:
            shift_month = 6
        case TimePeriod.one_year:
            shift_year = 1
        case TimePeriod.five_years:
            shift_year = 5
        case TimePeriod.all:
            return price_list
        case _:
            raise Exception("Invalid time period")

    earliest_datetime = Utils.timestamp_to_datetime(price_list[-1].timestamp)

    if shift_year > 0:
        earliest_datetime = earliest_datetime.replace(
            year=earliest_datetime.year - shift_year
        )
    elif earliest_datetime.month > shift_month:
        earliest_datetime = earliest_datetime.replace(
            month=earliest_datetime.month - shift_month
        )
    else:
        shift_month -= earliest_datetime.month
        earliest_datetime = earliest_datetime.replace(
            year=earliest_datetime.year - 1, month=12 - shift_month
        )

    return [
        data
        for data in price_list
        if data.timestamp >= Utils.datetime_to_timestamp(earliest_datetime)
    ]


def is_data_available(db) -> bool:
    return PriceListBase.exists(db)


def get_last_updated_price_list_data(db) -> int:
    pricelist = PriceListBase.get_last_updated_price_list_data(db)
    return (
        StockBase.get_index_by_stock_code(db, pricelist.stock_code) if pricelist else 0
    )

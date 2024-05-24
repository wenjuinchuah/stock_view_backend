import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import yfinance as yf
from sqlalchemy import func
from stock_indicators import Quote

import app.api.crud.stock as StockCRUD
import app.api.crud.utils as Utils
from app.api.constants import TimePeriod
from app.api.models.base import PriceListBase
from app.api.models.price_list import PriceList


# Fetch price list data for a stock code
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
            start_date=Utils.datetime_from_timestamp(start_date),
            end_date=Utils.datetime_now(),
        )
    else:
        price_list_data = await get_price_list_data(stock_code, period=period)

    # Add new rows if they don't already exist
    new_rows = [
        data.to_base()
        for data in price_list_data
        if not db.query(PriceListBase).filter_by(pricelist_id=data.pricelist_id).first()
    ]

    # Bulk save new rows to the database
    db.bulk_save_objects(new_rows)
    db.commit()

    return price_list_data


# Update price list data for all stock codes
async def update(db) -> int:
    period = "max"

    if not Utils.is_after_trading_hour(db, PriceListBase.datetime):
        return 0

    # Get all stock codes
    all_stock_code = StockCRUD.get_all_stock_code(db)

    # Fetch price list data for all stock codes
    tasks = [fetch(stock_code, period, db) for stock_code in all_stock_code]
    completed_tasks = await asyncio.gather(*tasks)

    return sum(len(price_list_data) for price_list_data in completed_tasks)


# Get price list data for a stock code
def get(stock_code: str, db) -> list[PriceList]:
    print(f"Fetching price list data for {stock_code}  ", end="\r")
    price_list = (
        db.query(PriceListBase)
        .filter(PriceListBase.pricelist_id.startswith(stock_code))
        .all()
    )
    return [
        data for data in price_list if data.stock_code == stock_code and data.volume > 0
    ]


# Get price list data for a stock code with time period and auto adjust
def get_price_list(
    stock_code: str, auto_adjust: bool, time_period: str, db
) -> list[PriceList]:
    price_list = get(stock_code, db)

    if price_list:
        # Sort by datetime
        price_list = sorted(price_list, key=lambda x: x.datetime)
        # Adjust price list if auto_adjust is True
        price_list = adjust_price_list(price_list) if auto_adjust else price_list

        return price_list_time_period(price_list, time_period)

    return []


# Get quote list for a stock code
def get_quote_list(stock_code: str, start_date: int, end_date: int, db) -> list[Quote]:
    price_list = get(stock_code, db)

    # Filter data before start_date to speed up the screening process
    filtered_data: list[PriceList] = [
        data
        for data in price_list
        if start_date <= Utils.to_local_timestamp(data.datetime) <= end_date
    ]

    # Convert to quote list
    with ThreadPoolExecutor() as executor:
        return list(executor.map(_convert_to_quote, filtered_data))


# Convert PriceList to Quote
def _convert_to_quote(data: PriceList):
    return data.to_quote()


# Get price list data for a stock code
async def get_price_list_data(
    stock_code: str,
    period: str | None = "1y",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[PriceList]:
    price_list = []

    tickers = (f"{stock_code}.KL",)

    if start_date and end_date:
        stock_df = yf.download(tickers, start=start_date, end=end_date, progress=False)
    else:
        stock_df = yf.download(tickers, period=period, progress=False)

    # fill NaN with -1 /
    if stock_df.empty:
        return price_list

    for index, row in stock_df.iterrows():
        timestamp = int(index.timestamp())
        price_list.append(
            PriceList(
                pricelist_id=f"{stock_code}_{timestamp}",
                open=round(row["Open"], 5),
                close=round(row["Close"], 5),
                adj_close=round(row["Adj Close"], 5),
                high=round(row["High"], 5),
                low=round(row["Low"], 5),
                volume=int(row["Volume"]),
                datetime=timestamp,
                stock_code=stock_code,
            )
        )
    return price_list


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
        )

        price_list[i].datetime = price_list[i].datetime

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

    earliest_datetime = Utils.datetime_from_timestamp(price_list[-1].datetime)

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
        if data.datetime >= int(earliest_datetime.timestamp())
    ]

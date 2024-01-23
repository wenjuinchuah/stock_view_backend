from datetime import datetime, timedelta

import pandas as pd
import pytz
import yfinance as yf
from sqlalchemy import func

from app.api.models.base import Stock, PriceList


def get_price_list_data(
    stock_code: str,
    auto_adjust: bool | None = True,
    period: str | None = "1y",
) -> list[PriceList]:
    priceList = []
    req = yf.Ticker(f"{stock_code}.KL")
    stock_df = req.history(period=period, auto_adjust=auto_adjust)

    # fill NaN with -1
    stock_df = stock_df.fillna(-1)

    for index, row in stock_df.iterrows():
        priceList.append(
            PriceList(
                pricelist_id=f"{stock_code}_{int(index.timestamp())}",
                open=round(row["Open"], 5),
                adj_close=round(row["Close"], 5),
                high=round(row["High"], 5),
                low=round(row["Low"], 5),
                volume=int(row["Volume"]),
                datetime=int(index.timestamp()),
                stock_code=stock_code,
            )
        )
    return priceList


async def update_stock(db) -> int:
    # End of KLSE's stock trading hours is 5pm GMT+8
    end_trading_hours = (
        datetime.now().replace(hour=17, minute=0, second=0, microsecond=0).time()
    )
    current_time = datetime.now().time()
    counter = 0

    # Condition 1: Check if the last updated date is today
    last_updated = db.query(func.min(Stock.updated_at)).scalar()
    last_updated_datetime = (
        datetime.fromtimestamp(last_updated, tz=pytz.timezone("Asia/Kuala_Lumpur"))
        if last_updated
        else None
    )
    if (
        last_updated_datetime
        and last_updated_datetime.date() == datetime.today().date()
    ):
        return counter

    # Condition 2: Check if the last updated date is not today and the current time is after 5pm
    is_update_needed = not last_updated_datetime or (
        last_updated_datetime.date() < datetime.today().date()
        and (
            current_time > end_trading_hours
            or (datetime.today().date() - last_updated_datetime.date())
            > timedelta(days=1)
        )
    )

    if not last_updated_datetime or is_update_needed:
        # read all the available stocks from the csv file
        data = pd.read_csv("app/assets/klse_stocks.csv")

        # replace NaN with None
        data.replace({pd.NA: None, pd.NaT: None}, inplace=True)

        for index, row in data.iterrows():
            existing_stock = (
                db.query(Stock).filter(Stock.stock_code == row["stock_code"]).first()
            )

            if not existing_stock:
                # insert all the stocks into the database if it does not exist
                stock = Stock(
                    stock_code=row["stock_code"],
                    stock_name=row["stock_name"],
                    category=row["category"],
                    is_shariah=row["is_shariah"],
                    updated_at=int(datetime.now().timestamp()),
                )
                db.add(stock)
            else:
                # update the stock if it exists
                existing_stock.stock_name = row["stock_name"]
                existing_stock.category = row["category"]
                existing_stock.is_shariah = row["is_shariah"]
                existing_stock.updated_at = int(datetime.now().timestamp())

            counter += 1

        # commit changes to the database
        db.commit()

    return counter

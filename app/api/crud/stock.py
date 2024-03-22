from datetime import datetime

import pandas as pd
import yfinance as yf
from sqlalchemy import func

import app.api.crud.utils as Utils
from app.api.models.base import StockBase
from app.api.models.price_list import PriceList


def get_price_list_data(
    stock_code: str,
    auto_adjust: bool | None = True,
    period: str | None = "1y",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[PriceList]:
    priceList = []
    req = yf.Ticker(f"{stock_code}.KL")
    if start_date and end_date:
        stock_df = req.history(start=start_date, end=end_date, auto_adjust=auto_adjust)
    else:
        stock_df = req.history(period=period, auto_adjust=auto_adjust)

    # fill NaN with -1
    stock_df = stock_df.fillna(-1)

    for index, row in stock_df.iterrows():
        priceList.append(
            PriceList(
                pricelist_id=f"{stock_code}_{int(index.timestamp())}",
                open=round(row["Open"], 5),
                close=-1,
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
    counter = 0
    query = db.query(func.max(StockBase.updated_at))

    # Condition check
    if Utils.db_data_days_diff(query, days=0) or (
        Utils.db_data_days_diff(query, days=1) and not Utils.is_after_trading_hour()
    ):
        return counter

    # read all the available stocks from the csv file
    data = pd.read_csv("app/assets/klse_stocks.csv")

    # replace NaN with None
    data.replace({pd.NA: None, pd.NaT: None}, inplace=True)

    for index, row in data.iterrows():
        existing_stock = (
            db.query(StockBase)
            .filter(StockBase.stock_code == row["stock_code"])
            .first()
        )

        if not existing_stock:
            # insert all the stocks into the database if it does not exist
            stock = StockBase(
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


def get_all_stock_code(db) -> list[str]:
    all_stock_code = db.query(StockBase.stock_code).all()
    return [stock_code[0] for stock_code in all_stock_code]


def get_stock_details(db, stock_code: str) -> StockBase:
    return db.query(StockBase).filter(StockBase.stock_code == stock_code).first()
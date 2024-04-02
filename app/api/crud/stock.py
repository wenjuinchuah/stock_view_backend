from datetime import datetime

import pandas as pd
from sqlalchemy import func, or_

import app.api.crud.utils as Utils
from app.api.models.base import StockBase
import app.api.crud.stock_scrapper as StockScrapper


async def update_stock(db) -> int:
    counter = 0
    query = db.query(func.max(StockBase.updated_at))

    # Condition check
    if Utils.db_data_days_diff(query, days=0) or (
        Utils.db_data_days_diff(query, days=1) and not Utils.is_after_trading_hour()
    ):
        return counter

    # Scrape stock listing from KLSE Screener (Board id: Main[1], Ace[2], Leap[6])
    for board_id in [1, 2, 6]:
        StockScrapper.scrape_stock_list(board_id)

    # read all the available stocks from the csv file
    data = pd.read_csv("app/assets/stock_list.csv")

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
                stock_full_name=row["stock_full_name"],
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


def get_matched_stock_details(db, query: str) -> list[StockBase]:
    return (
        db.query(StockBase)
        .filter(
            or_(
                StockBase.stock_name.startswith(query),
                StockBase.stock_code.startswith(query),
            )
        )
        .all()
    )

import pandas as pd
from sqlalchemy import or_

import app.api.crud.utils as Utils
from app.api.models.base import StockBase
import app.api.crud.stock_scrapper as StockScrapper


# Update stock listing
async def update_stock(db) -> int:
    counter = 0

    # Scrape stock listing from i3Investor Screener
    StockScrapper.scrape_stock_list()

    # read all the available stocks from the csv file
    data = pd.read_csv("app/assets/stock_list.csv")

    # replace NaN with None
    data.replace({pd.NA: None, pd.NaT: None}, inplace=True)

    for index, row in data.iterrows():
        existing_stock = StockBase.get(db, row["stock_code"])

        if not existing_stock:
            # insert all the stocks into the database if it does not exist
            stock = StockBase(
                stock_code=row["stock_code"],
                stock_name=row["stock_name"],
                stock_full_name=row["stock_full_name"],
                category=row["category"],
                updated_at=Utils.timestamp_now(),
            )
            StockBase.update(db, stock)
        else:
            # update the stock if it exists
            existing_stock.stock_name = row["stock_name"]
            existing_stock.stock_full_name = row["stock_full_name"]
            existing_stock.category = row["category"]
            existing_stock.updated_at = Utils.timestamp_now()

        counter += 1

    return counter


# Get all stock codes
def get_all_stock_code(db) -> list[str]:
    all_stocks = StockBase.get_all(db)
    return [stock.stock_code for stock in all_stocks]


# Get stock details
def get_stock_details(db, stock_code: str) -> StockBase:
    return StockBase.get(db, stock_code)


# Get matched stock details
def get_matched_stock_details(db, query: str) -> list[StockBase]:
    return StockBase.search_by_code_and_name(db, query)

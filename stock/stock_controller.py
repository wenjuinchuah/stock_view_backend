import yfinance as yf
import datetime as dt
import stock.indicator as indicator
import csv

from stock.stock_entity import StockTicker
from stock_indicators import indicators, Quote
from constant import Indicator, Page
from pathlib import Path


def getStockTickerData(stock_code: str, auto_adjust: str) -> StockTicker:
    auto_adjust = True if auto_adjust == "true" else False
    req = yf.Ticker(f"{stock_code}.KL")
    # print(start, end)
    stock_df = req.history(period="1y", auto_adjust=auto_adjust)

    # Convert Timestamp index to milliseconds
    timestamp_milliseconds = stock_df.index.astype(int) // 10**6

    stock_ticker = StockTicker(
        stock_code=stock_code,
        close=stock_df["Close"].tolist(),
        open=stock_df["Open"].tolist(),
        high=stock_df["High"].tolist(),
        low=stock_df["Low"].tolist(),
        volume=stock_df["Volume"].tolist(),
        timestamp=timestamp_milliseconds.tolist(),
    )

    return stock_ticker


def searchStocks(data: dict, page_number: int):
    results = {}
    matchedStocks = []
    start_row = (page_number - 1) * Page.rows_per_page

    csv_file = Path(__file__).resolve().parent.parent / "assets/klse_stocks.csv"
    with open(csv_file, mode="r") as file:
        csv_reader = csv.DictReader(file)
        row_count = 0

        for row in csv_reader:
            row_count += 1
            if row_count <= start_row:
                continue

            stock_code = row["stock_code"]
            cci_data = data.get(Indicator.CCI)
            start_date = cci_data["date_from"]
            end_date = cci_data["date_to"]

            # convert start_date and end_date from milliseconds to datetime
            start_date = dt.datetime.fromtimestamp(start_date / 1000)
            end_date = dt.datetime.fromtimestamp(end_date / 1000)
            stockTicker = getStockTickerData(stock_code, "true", start_date, end_date)

            # cci
            cci = indicator.cci(cci_data, stockTicker)
            if cci:
                matchedStocks.append(stock_code)

            if row_count - start_row >= Page.rows_per_page:
                break

        results[Indicator.CCI] = matchedStocks

    return results


def getCCI(quote_list: list[Quote]):
    cci_results = indicators.get_cci(quote_list, 20)

    cci = []
    date = []
    for result in cci_results:
        cci.append(result.cci)
        date.append(int(result.date.timestamp() * 1000))
    return {
        "cci": cci,
        "date": date,
    }


def getMACD(quote_list: list[Quote]):
    macd_results = indicators.get_macd(quote_list, 12, 26, 9)
    macd = []
    date = []
    for result in macd_results:
        macd.append(result.macd)
        date.append(int(result.date.timestamp() * 1000))
    return {
        "macd": macd,
        "date": date,
    }

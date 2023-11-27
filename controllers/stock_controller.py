import yfinance as yf
import datetime as dt
import controllers.indicator_controller as IndicatorController
import csv

from bs4 import BeautifulSoup
from stock_indicators import indicators, Quote
from models.stock_ticker_model import StockTicker
from constants import Indicator, Page
from pathlib import Path

from models.stock_search_model import StockSearchModel, CCIModel


def get_stock_ticker_data(stock_code: str, auto_adjust: bool) -> StockTicker:
    req = yf.Ticker(f"{stock_code}.KL")
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


# noinspection PyTypeChecker
def search_stocks(data: StockSearchModel, page_number: int) -> dict:
    results = {}
    matched_stocks = []
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
            cci_data: CCIModel = getattr(data, Indicator.CCI)
            start_date: int = getattr(cci_data, "date_from")
            end_date: int = getattr(cci_data, "date_to")

            # convert start_date and end_date from milliseconds to datetime
            start_date = dt.datetime.fromtimestamp(start_date / 1000)
            end_date = dt.datetime.fromtimestamp(end_date / 1000)
            stock_ticker = get_stock_ticker_data(stock_code, True)

            # cci
            cci = IndicatorController.cci(cci_data, stock_ticker)
            if cci:
                matched_stocks.append(stock_code)

            if row_count - start_row >= Page.rows_per_page:
                break

        results[Indicator.CCI] = matched_stocks

    return results


def get_cci(quote_list: list[Quote]):
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


def get_macd(quote_list: list[Quote]):
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


def scrape():
    with open("assets/klse_stocks.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    data = []

    # Find the table containing stock information
    table = soup.find(
        "table",
        class_="table table-sm table-theme table-hover tablesorter-bootstrap tablesorter",
    )

    if table:
        rows = table.find_all("tr")

        for row in rows[1:]:  # Skip the header row
            columns = row.find_all("td")
            if len(columns) >= 2:
                stock_name = columns[0].a.text
                is_shariah = "[s]" in columns[0].text
                stock_code = columns[1].text.strip()
                category_small = columns[2].find("small")
                category = category_small.text.strip() if category_small else ""

                data.append([stock_name, stock_code, is_shariah, category])

        # Save data as CSV
        with open("assets/klse_stocks.csv", "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["stock_name", "stock_code", "is_shariah", "category"])
            csv_writer.writerows(data)

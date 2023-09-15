import yfinance as yf

from stock.stock_entity import StockTicker
from stock_indicators import indicators, Quote
from constant import Indicator


def getStockTickerData(stock_code: str) -> StockTicker:
    req = yf.Ticker(stock_code + ".KL")
    stock_df = req.history(period="1y")

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


def getIndicator(stock_code: str, indicator: str):
    results = {}

    if indicator is None or indicator is "":
        return results
    else:
        stock_ticker = getStockTickerData(stock_code)
        quote_list = stock_ticker.to_quote_list()

        match indicator.upper():
            case Indicator.CCI:
                results = getCCI(quote_list)
                results["stock_code"] = stock_code
                return results
            case Indicator.MACD:
                results = getMACD(quote_list)
                results["stock_code"] = stock_code
                return results
            case _:
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

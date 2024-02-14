import time

from stock_indicators import indicators

import app.api.crud.price_list as PriceListCRUD
import app.api.crud.stock as StockCRUD
from app.api.models.stock_indicator import Indicator
from app.api.models.stock_screener import StockScreener, StockScreenerResult


def screen_stock(stock_screener: StockScreener, db) -> StockScreenerResult:
    # count time taken
    start = time.time()

    stock_screener_result = StockScreenerResult(**stock_screener.model_dump())
    all_stock_code = StockCRUD.get_all_stock_code(db)
    matched_stock = []

    if (
        stock_screener.start_date > stock_screener.end_date
        or stock_screener.start_date == 0
        or stock_screener.end_date == 0
    ):
        raise Exception("Invalid date range")

    for stock_code in all_stock_code:
        progress = (all_stock_code.index(stock_code) + 1) / len(all_stock_code) * 100
        price_list = PriceListCRUD.get(stock_code, db)
        isMatched: bool = True

        print(f"Screening progress: {progress:.2f}%", end="\r")

        if not price_list:
            continue

        for indicator in stock_screener.indicator_list:
            if not isMatched:
                continue

            temp_matched_stock = [stock_code]

            match indicator.name:
                case Indicator.CCI:
                    if stock_code in temp_matched_stock:
                        isMatched = process_cci(stock_screener, price_list, indicator)
                        if not isMatched:
                            temp_matched_stock.remove(stock_code)

                case Indicator.MACD:
                    if stock_code in temp_matched_stock:
                        isMatched = process_macd(stock_screener, price_list, indicator)
                        if not isMatched:
                            temp_matched_stock.remove(stock_code)

                case Indicator.KDJ:
                    if stock_code in temp_matched_stock:
                        isMatched = process_kdj(stock_screener, price_list, indicator)
                        if not isMatched:
                            temp_matched_stock.remove(stock_code)

                case _:
                    raise Exception("Unknown indicator")

            if temp_matched_stock:
                matched_stock.append(temp_matched_stock[0])

    stock_screener_result.add(matched_stock)

    # timer
    end = time.time()
    print(f"\nScreening time: {end - start:.2f} seconds")
    return stock_screener_result


def process_cci(stock_screener, price_list, indicator) -> bool:
    results = indicators.get_cci(
        [data.to_quote() for data in price_list],
        indicator.time_period,
    )
    for result in results:
        if not result.cci:
            continue
        if (
            indicator.overbought < result.cci or result.cci < indicator.oversold
        ) and stock_screener.start_date <= result.date.timestamp() <= stock_screener.end_date:
            return True

    return False


def process_macd(stock_screener, price_list, indicator) -> bool:
    results = indicators.get_macd(
        [data.to_quote() for data in price_list],
        indicator.fast_period,
        indicator.slow_period,
        indicator.signal_period,
    )
    for result in results:
        if not (result.macd and result.signal):
            continue
        if (
            result.macd > result.signal  # if > buy signal, else < sell signal
        ) and stock_screener.start_date <= result.date.timestamp() <= stock_screener.end_date:
            return True

    return False


def process_kdj(stock_screener, price_list, indicator) -> bool:
    results = indicators.get_stoch(
        [data.to_quote() for data in price_list],
        indicator.loopback_period,
        indicator.signal_period,
        indicator.smooth_period,
    )
    for result in results:
        if not result.k or not result.d or not result.j:
            continue

        if (
            result.k < result.d < result.j  # if < buy signal, else > sell signal
        ) and stock_screener.start_date <= result.date.timestamp() <= stock_screener.end_date:
            return True

    return False

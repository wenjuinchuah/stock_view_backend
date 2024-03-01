import asyncio
import time

from stock_indicators import indicators

import app.api.crud.price_list as PriceListCRUD
import app.api.crud.stock as StockCRUD
from app.api.models.stock_screener import StockScreener, StockScreenerResult


async def fetch_db(
    stock_code: str,
    results: StockScreenerResult,
    db,
) -> str | None:
    quote_list = PriceListCRUD.get_quote_list_with_start_end_date(
        stock_code=stock_code,
        start_date=results.start_date,
        end_date=results.end_date,
        db=db,
    )
    if not quote_list:
        return None

    temp_matched_stock = [stock_code]

    if results.stock_indicator.cci is not None:
        if stock_code in temp_matched_stock:
            isMatched = process_cci(results, quote_list, results.stock_indicator.cci)
            if not isMatched:
                temp_matched_stock = []

    if results.stock_indicator.macd is not None:
        if stock_code in temp_matched_stock:
            isMatched = process_macd(results, quote_list, results.stock_indicator.macd)
            if not isMatched:
                temp_matched_stock = []

    if results.stock_indicator.kdj is not None:
        if stock_code in temp_matched_stock:
            isMatched = process_kdj(results, quote_list, results.stock_indicator.kdj)
            if not isMatched:
                temp_matched_stock = []

    # for indicator in results.stock_indicator:
    #     if not temp_matched_stock:
    #         break
    #
    #     match indicator.name:
    #         case Indicator.CCI:
    #             if stock_code in temp_matched_stock:
    #                 isMatched = process_cci(results, quote_list, indicator)
    #                 if not isMatched:
    #                     temp_matched_stock = []
    #
    #         case Indicator.MACD:
    #             if stock_code in temp_matched_stock:
    #                 isMatched = process_macd(results, quote_list, indicator)
    #                 if not isMatched:
    #                     temp_matched_stock = []
    #
    #         case Indicator.KDJ:
    #             if stock_code in temp_matched_stock:
    #                 isMatched = process_kdj(results, quote_list, indicator)
    #                 if not isMatched:
    #                     temp_matched_stock = []
    #
    #         case _:
    #             raise Exception("Unknown indicator")

    return temp_matched_stock[0] if temp_matched_stock else None


async def screen_stock(stock_screener: StockScreener, db) -> StockScreenerResult:
    start_time = time.time()
    if (
        stock_screener.start_date > stock_screener.end_date
        or stock_screener.start_date == 0
        or stock_screener.end_date == 0
    ):
        raise Exception("Invalid date range")

    stock_screener_result = StockScreenerResult(**stock_screener.model_dump())
    all_stock_code = StockCRUD.get_all_stock_code(db)

    tasks = [
        fetch_db(stock_code, stock_screener_result, db) for stock_code in all_stock_code
    ]
    completed_tasks = await asyncio.gather(*tasks)

    matched_stock = [stock_code for stock_code in completed_tasks if stock_code]
    stock_screener_result.add(matched_stock)
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"\nTime taken: {time_taken:.2f} seconds")
    return stock_screener_result


def process_cci(stock_screener, quotes, indicator) -> bool:
    results = indicators.get_cci(
        quotes,
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


def process_macd(stock_screener, quotes, indicator) -> bool:
    results = indicators.get_macd(
        quotes,
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


def process_kdj(stock_screener, quotes, indicator) -> bool:
    results = indicators.get_stoch(
        quotes,
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

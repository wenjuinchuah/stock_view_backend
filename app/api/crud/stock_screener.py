import time

from stock_indicators import indicators

import app.api.crud.price_list as PriceListCRUD
import app.api.crud.stock as StockCRUD
from app.api.models.stock import StockDetails
from app.api.models.stock_indicator import (
    Indicator,
    CCIIndicator,
    MACDIndicator,
    KDJIndicator,
)
from app.api.models.stock_screener import StockScreener, StockScreenerResult


async def fetch_db(
    stock_code: str,
    results: StockScreenerResult,
    db,
) -> StockDetails | None:
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
            is_matched = process_cci(results, quote_list, results.stock_indicator.cci)
            if not is_matched:
                temp_matched_stock = []

    if results.stock_indicator.macd is not None:
        if stock_code in temp_matched_stock:
            is_matched = process_macd(results, quote_list, results.stock_indicator.macd)
            if not is_matched:
                temp_matched_stock = []

    if results.stock_indicator.kdj is not None:
        if stock_code in temp_matched_stock:
            is_matched = process_kdj(results, quote_list, results.stock_indicator.kdj)
            if not is_matched:
                temp_matched_stock = []

    if temp_matched_stock:
        stock = StockCRUD.get_stock_details(db, stock_code)
        # Create a new StockDetails instance
        stock_detail = StockDetails(
            stock_code=temp_matched_stock[0],
            stock_name=stock.stock_name,
            close_price=quote_list[-1].close,
            percentage_change=(quote_list[-1].close / quote_list[-2].close - 1) * 100,
        )
        return stock_detail

    return None


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

    start_index = (
        all_stock_code.index(stock_screener_result.last_stock_code) + 1
        if stock_screener_result.last_stock_code
        else 0
    )

    matched_stock: list[StockDetails] = []
    for stock_code in all_stock_code[start_index:]:
        if len(matched_stock) >= stock_screener_result.page_size:
            stock_screener_result.last_stock_code = (
                matched_stock[-1].stock_code if matched_stock else None
            )
            break
        elif stock_code == all_stock_code[-1]:
            stock_screener_result.last_stock_code = stock_code

        result = await fetch_db(stock_code, stock_screener_result, db)
        if result:
            matched_stock.append(result)

    stock_screener_result.add(matched_stock)

    end_time = time.time()
    time_taken = end_time - start_time
    print(f"\nTime taken: {time_taken:.2f} seconds")

    return stock_screener_result


def process_cci(stock_screener, quotes, indicator) -> bool:
    results = indicators.get_cci(quotes, indicator.time_period)
    filtered_results = [
        result
        for result in results
        if result.date.timestamp()
        >= stock_screener.start_date - indicator.time_period * 86400
    ]

    for result in filtered_results:
        if not result.cci:
            continue

        within_date_range = (
            stock_screener.start_date
            <= result.date.timestamp()
            <= stock_screener.end_date
        )
        if within_date_range:
            if (
                (
                    indicator.oversold is None
                    and indicator.overbought is not None
                    and indicator.overbought < result.cci
                )
                or (
                    indicator.overbought is None
                    and indicator.oversold is not None
                    and result.cci < indicator.oversold
                )
                or (
                    indicator.overbought is not None
                    and indicator.oversold is not None
                    and (
                        indicator.overbought < result.cci
                        or result.cci < indicator.oversold
                    )
                )
            ):
                return True

    return False


def process_macd(stock_screener, quotes, indicator) -> bool:
    results = indicators.get_macd(
        quotes,
        indicator.fast_period,
        indicator.slow_period,
        indicator.signal_period,
    )
    filtered_results = [
        result
        for result in results
        if result.date.timestamp()
        >= stock_screener.start_date
        - 2 * (indicator.slow_period + indicator.signal_period) * 86400
    ]

    previous_macd, previous_signal = None, None

    for result in filtered_results:
        if not (result.macd and result.signal):
            continue

        if indicator.bullish == indicator.bearish:
            raise Exception(
                "Invalid MACD indicator, please specify either bullish or bearish."
            )

        within_date_range = (
            stock_screener.start_date
            <= result.date.timestamp()
            <= stock_screener.end_date
        )

        if (
            within_date_range
            and previous_macd is not None
            and previous_signal is not None
        ):
            bearish = (
                indicator.bearish
                and previous_macd > previous_signal > result.signal > result.macd
            )
            bullish = (
                indicator.bullish
                and previous_macd < previous_signal < result.signal < result.macd
            )

            if bearish or bullish:
                return True

        previous_macd = result.macd
        previous_signal = result.signal

    return False


def process_kdj(stock_screener, quotes, indicator) -> bool:
    results = indicators.get_stoch(
        quotes,
        indicator.loopback_period,
        indicator.signal_period,
        indicator.smooth_period,
    )
    filtered_results = [
        result
        for result in results
        if result.date.timestamp()
        >= stock_screener.start_date
        - (indicator.loopback_period + indicator.smooth_period) * 86400
    ]

    previous_k, previous_d = None, None

    for result in filtered_results:
        if not result.k or not result.d or not result.j:
            continue

        if indicator.golden_cross == indicator.dead_cross:
            raise Exception(
                "Invalid KDJ indicator, please specify either golden cross or dead cross."
            )

        within_date_range = (
            stock_screener.start_date
            <= result.date.timestamp()
            <= stock_screener.end_date
        )

        if within_date_range and previous_k is not None and previous_d is not None:
            golden_cross_condition = (
                indicator.golden_cross
                and result.d < result.k
                and previous_k < previous_d < result.d < result.j
            )
            dead_cross_condition = (
                indicator.dead_cross
                and result.d > result.k
                and previous_k > previous_d > result.d > result.j
            )

            if golden_cross_condition or dead_cross_condition:
                return True

        previous_k = result.k
        previous_d = result.d

    return False


def get_available_rules():
    return {
        Indicator.CCI: CCIIndicator(),
        Indicator.MACD: MACDIndicator(),
        Indicator.KDJ: KDJIndicator(),
    }


def get_indicator_selector():
    return {
        Indicator.CCI: {
            "overbought": "is greater than",
            "oversold": "is less than",
        },
        Indicator.MACD: {
            "bullish": "MACD above Signal (Bullish)",
            "bearish": "MACD below Signal (Bearish)",
        },
        Indicator.KDJ: {
            "golden_cross": "Golden Cross (Bullish)",
            "dead_cross": "Dead Cross (Bearish)",
        },
    }

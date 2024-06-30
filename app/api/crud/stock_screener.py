import asyncio
from datetime import timedelta

from stock_indicators import indicators

import app.api.crud.price_list as PriceListCRUD
import app.api.crud.stock as StockCRUD
import app.api.crud.utils as Utils
from app.api.models.stock import StockDetails
from app.api.models.stock_indicator import (
    Indicator,
    CCIIndicator,
    MACDIndicator,
    KDJIndicator,
)
from app.api.models.stock_screener import StockScreener, StockScreenerResult


# Fetch stock details from the database
async def fetch_db(
    stock_code: str,
    results: StockScreenerResult,
    db,
) -> StockDetails | None:
    quote_list = PriceListCRUD.get_quote_list(
        stock_code=stock_code,
        start_date=results.start_date,
        end_date=results.end_date,
        db=db,
    )
    if not quote_list:
        return None

    temp_matched_stock = [stock_code]
    tasks = []

    if results.stock_indicator.cci is not None:
        tasks.append(process_cci(results, quote_list, results.stock_indicator.cci))

    if results.stock_indicator.macd is not None:
        tasks.append(process_macd(results, quote_list, results.stock_indicator.macd))

    if results.stock_indicator.kdj is not None:
        tasks.append(process_kdj(results, quote_list, results.stock_indicator.kdj))

    results_list = await asyncio.gather(*tasks)

    if any(result is None for result in results_list):
        temp_matched_stock = []

    if temp_matched_stock:
        stock = StockCRUD.get_stock_details(db, stock_code)
        # Create a new StockDetails instance
        stock_detail = StockDetails(
            stock_code=temp_matched_stock[0],
            stock_name=stock.stock_name,
            close_price=quote_list[-1].close,
            percentage_change=(
                quote_list[-1].close / quote_list[len(quote_list) - 2].close - 1
            )
            * 100,
            matched_timestamp=max(results_list) if results_list else None,
        )
        return stock_detail

    return None


# Screen stock based on the stock screener
async def screen_stock(stock_screener: StockScreener, db) -> StockScreenerResult:
    stock_screener_result = StockScreenerResult(**stock_screener.model_dump())

    if not is_valid_date_range(stock_screener.start_date, stock_screener.end_date):
        return stock_screener_result

    offset = get_indicator_required_date_offset(stock_screener_result)
    stock_screener_result.start_date -= offset

    all_stock_code = StockCRUD.get_all_stock_code(db)
    start_index = (
        all_stock_code.index(stock_screener_result.last_stock_code) + 1
        if stock_screener_result.last_stock_code
        else 0
    )

    matched_stock = []
    for stock_code in all_stock_code[start_index:]:
        result = await fetch_db(stock_code, stock_screener_result, db)
        if result is not None:
            matched_stock.append(result)
            if (
                stock_screener_result.last_stock_code is None
                or stock_screener_result.last_stock_code < result.stock_code
            ):
                stock_screener_result.last_stock_code = result.stock_code
            if len(matched_stock) >= stock_screener_result.page_size:
                break

    if not matched_stock or len(matched_stock) < stock_screener_result.page_size:
        stock_screener_result.last_stock_code = all_stock_code[-1]

    stock_screener_result.add(matched_stock)
    stock_screener_result.start_date += offset

    return stock_screener_result


# Process CCI indicator
async def process_cci(stock_screener, quotes, indicator) -> int | None:
    results = indicators.get_cci(quotes, indicator.time_period)

    filtered_results = [
        result
        for result in results
        if Utils.to_local_timestamp(result.date.timestamp())
        >= stock_screener.start_date
    ]

    for result in filtered_results:
        if not result.cci:
            continue

        within_date_range = (
            stock_screener.start_date
            + get_indicator_required_date_offset(stock_screener)
            <= Utils.to_local_timestamp(result.date.timestamp())
            <= stock_screener.end_date
        )
        if within_date_range:
            if (
                indicator.oversold is None
                and indicator.overbought is not None
                and indicator.overbought <= result.cci
            ) or (
                indicator.overbought is None
                and indicator.oversold is not None
                and result.cci <= indicator.oversold
            ):
                return int(result.date.timestamp())

    return None


# Process MACD indicator
async def process_macd(stock_screener, quotes, indicator) -> int | None:
    results = indicators.get_macd(
        quotes,
        indicator.fast_period,
        indicator.slow_period,
        indicator.signal_period,
    )

    previous_macd, previous_signal, previous_histogram = None, None, None

    for result in results:
        if not (result.macd and result.signal):
            continue

        if indicator.bullish == indicator.bearish:
            raise Exception(
                "Invalid MACD indicator, please specify either bullish or bearish."
            )

        within_date_range = (
            stock_screener.start_date
            + get_indicator_required_date_offset(stock_screener)
            <= Utils.to_local_timestamp(result.date.timestamp())
            <= stock_screener.end_date
        )

        macd = round(result.macd, 4)
        signal = round(result.signal, 4)
        histogram = round(result.histogram, 4)

        if (
            within_date_range
            and previous_macd is not None
            and previous_signal is not None
        ):
            histogram_to_positive = previous_histogram <= 0.0 < histogram
            histogram_to_negative = previous_histogram > 0.0 >= histogram

            bearish = (
                indicator.bearish
                and previous_macd >= previous_signal
                and signal >= macd
                and (histogram_to_negative or previous_histogram == histogram)
            )
            bullish = (
                indicator.bullish
                and previous_signal >= previous_macd
                and macd >= signal
                and (histogram_to_positive or previous_histogram == histogram)
            )
            if bearish or bullish:
                return int(result.date.timestamp())

        previous_macd = macd
        previous_signal = signal
        previous_histogram = histogram

    return None


# Process KDJ indicator
async def process_kdj(stock_screener, quotes, indicator) -> int | None:
    results = indicators.get_stoch(
        quotes,
        indicator.loopback_period,
        indicator.signal_period,
        indicator.smooth_period,
    )

    filtered_results = [
        result
        for result in results
        if Utils.to_local_timestamp(result.date.timestamp())
        >= stock_screener.start_date
    ]

    previous_k, previous_d = None, None

    for result in filtered_results:
        if not result.k or not result.d or not result.j:
            continue

        if indicator.golden_cross == indicator.death_cross:
            raise Exception(
                "Invalid KDJ indicator, please specify either golden cross or death cross."
            )

        within_date_range = (
            stock_screener.start_date
            + get_indicator_required_date_offset(stock_screener)
            <= Utils.to_local_timestamp(result.date.timestamp())
            <= stock_screener.end_date
        )

        if within_date_range and previous_k is not None and previous_d is not None:
            golden_cross_condition = (
                indicator.golden_cross
                and result.d < result.k
                and previous_k < previous_d < result.d < result.j
            )
            death_cross_condition = (
                indicator.death_cross
                and result.d > result.k
                and previous_k > previous_d > result.d > result.j
            )

            if golden_cross_condition or death_cross_condition:
                return int(result.date.timestamp())

        previous_k = result.k
        previous_d = result.d

    return None


# Get all available rules
def get_available_rules():
    return {
        Indicator.CCI: CCIIndicator(),
        Indicator.MACD: MACDIndicator(),
        Indicator.KDJ: KDJIndicator(),
    }


# Get all available indicators and their respective rules
def get_indicator_selector():
    return {
        Indicator.CCI: {
            "overbought": "is greater than (Overbought)",
            "oversold": "is less than (Oversold)",
        },
        Indicator.MACD: {
            "bullish": "MACD above Signal (Bullish)",
            "bearish": "MACD below Signal (Bearish)",
        },
        Indicator.KDJ: {
            "golden_cross": "Golden Cross (Bullish)",
            "death_cross": "Death Cross (Bearish)",
        },
    }


# Get the required date offset for the indicator
def get_indicator_required_date_offset(results: StockScreenerResult) -> int:
    indicator = results.stock_indicator

    if indicator.macd is not None:
        offset = indicator.macd.slow_period + indicator.macd.signal_period + 250
    elif indicator.kdj is not None:
        offset = indicator.kdj.loopback_period + indicator.kdj.smooth_period
    elif indicator.cci is not None:
        offset = indicator.cci.time_period
    else:
        offset = 0

    return offset * 86400


def is_valid_date_range(start_date: int, end_date: int) -> bool:
    if start_date > end_date or start_date == 0 or end_date == 0:
        raise Exception("Invalid date range")

    start_datetime = Utils.timestamp_to_datetime(start_date)
    end_datetime = Utils.timestamp_to_datetime(end_date)

    # Check if the date range is within 1 day and is on weekends or holidays
    if end_datetime - start_datetime <= timedelta(days=1) and (
        (end_datetime.weekday() >= 5 and start_datetime.weekday() >= 5)
        or (start_datetime.weekday() >= 5 and Utils.is_holiday(end_datetime))
        or (end_datetime.weekday() >= 5 and Utils.is_holiday(start_datetime))
        or (Utils.is_holiday(start_datetime) and Utils.is_holiday(end_datetime))
    ):
        return False

    return start_date <= end_date

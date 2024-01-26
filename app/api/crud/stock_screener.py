from stock_indicators import indicators

import app.api.crud.price_list as PriceListCRUD
import app.api.crud.stock as StockCRUD
from app.api.models.stock_indicator import Indicator
from app.api.models.stock_screener import StockScreener, StockScreenerResult


def screen_stock(stock_screener: StockScreener, db) -> StockScreenerResult:
    stock_screener_result = StockScreenerResult(**stock_screener.model_dump())
    all_stock_code = StockCRUD.get_all_stock_code(db)

    for stock_code in all_stock_code:
        price_list = PriceListCRUD.get_price_list_data(stock_code, db)

        if not price_list:
            continue

        for indicator in stock_screener.indicator_list:
            print(f"Processing {indicator.name} for {stock_code}:")

            match indicator.name:
                case Indicator.CCI:
                    if process_cci(stock_screener, price_list, indicator):
                        stock_screener_result.append(stock_code)
                case Indicator.MACD:
                    if process_macd(stock_screener, price_list, indicator):
                        stock_screener_result.append(stock_code)
                case Indicator.KDJ:
                    if process_kdj(stock_screener, price_list, indicator):
                        stock_screener_result.append(stock_code)
                case _:
                    raise Exception("Unknown indicator")

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

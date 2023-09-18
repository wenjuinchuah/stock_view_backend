from stock_indicators import indicators
from stock.stock_entity import StockTicker
from datetime import date


def cci(results: dict, stockTicker: StockTicker):
    length = results.get("length", 20)
    overbought = results.get("overbought", 100)
    oversold = results.get("oversold", -100)
    date_from = results.get("date_from", 0)
    date_to = results.get("date_to", 0)
    step = 86400000

    quoteList = stockTicker.to_quote_list()
    cci_results = indicators.get_cci(quoteList, length)

    overbought_results = [
        a
        for a, b in zip(cci_results, cci_results[1:])
        if a.cci != None
        and a.cci >= overbought
        and b.cci < overbought
        and int(a.date.timestamp() * 1000) in range(date_from, date_to + step, step)
    ]
    oversold_results = [
        a
        for a, b in zip(cci_results, cci_results[1:])
        if a.cci != None
        and a.cci <= oversold
        and b.cci > oversold
        and int(a.date.timestamp() * 1000) in range(date_from, date_to + step, step)
    ]

    return True if overbought_results or oversold_results else False

    # return {
    #     "length": length,
    #     "overbought": {
    #         "value": [result.cci for result in overbought_results],
    #         "timestamp": [int(result.date.timestamp() * 1000) for result in overbought_results]
    #     },
    #     "oversold": {
    #         "value": [result.cci for result in oversold_results],
    #         "timestamp": [int(result.date.timestamp() * 1000) for result in oversold_results]
    #     },
    # }

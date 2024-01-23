from stock_indicators import indicators

from app.api.models.stock_ticker import StockTicker


def cci(results: object, stock_ticker: StockTicker):
    length = getattr(results, "length", 20)
    overbought = getattr(results, "overbought", 100)
    oversold = getattr(results, "oversold", -100)
    date_from = getattr(results, "date_from", 0)
    date_to = getattr(results, "date_to", 0)

    # Step is used to increment datetime in milliseconds for a day
    step = 86400000

    quote_list = stock_ticker.to_quote_list()
    cci_results = indicators.get_cci(quote_list, length)

    overbought_results = [
        a
        for a, b in zip(cci_results, cci_results[1:])
        if a.cci is not None
        and a.cci >= overbought > b.cci
        and int(a.date.timestamp() * 1000) in range(date_from, date_to + step, step)
    ]
    oversold_results = [
        a
        for a, b in zip(cci_results, cci_results[1:])
        if a.cci is not None
        and a.cci <= oversold < b.cci
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

from dataclasses import dataclass
from datetime import datetime
from typing import List

from stock_indicators import Quote


@dataclass
class StockTicker:
    stock_code: str
    close: List[float]
    open: List[float]
    high: List[float]
    low: List[float]
    volume: List[int]
    timestamp: List[int]

    def to_quote_list(self):
        try:
            datetime_timestamps = [
                datetime.fromtimestamp(ts / 1000) for ts in self.timestamp
            ]
            quote_list = [
                Quote(
                    date=datetime_timestamps[i],
                    open=self.open[i],
                    high=self.high[i],
                    low=self.low[i],
                    close=self.close[i],
                    volume=self.volume[i],
                )
                for i in range(len(self.timestamp))
            ]
            return quote_list
        except Exception as e:
            raise e

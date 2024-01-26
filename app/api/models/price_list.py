from datetime import datetime

from pydantic import BaseModel
from stock_indicators import Quote


class PriceList(BaseModel):
    pricelist_id: str
    open: float
    close: float | None
    adj_close: float
    high: float
    low: float
    volume: int
    datetime: int
    stock_code: str

    def to_quote(self):
        return Quote(
            date=datetime.fromtimestamp(self.datetime),
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.adj_close,
            volume=self.volume,
        )

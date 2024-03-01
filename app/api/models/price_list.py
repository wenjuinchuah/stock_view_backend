from pydantic import BaseModel


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

    def to_base(self):
        from app.api.models.base import PriceListBase

        return PriceListBase(
            pricelist_id=self.pricelist_id,
            open=self.open,
            close=self.close,
            adj_close=self.adj_close,
            high=self.high,
            low=self.low,
            volume=self.volume,
            datetime=self.datetime,
            stock_code=self.stock_code,
        )

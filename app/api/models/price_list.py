from pydantic import BaseModel, PositiveInt


class PriceListBase(BaseModel):
    pricelist_id: int
    open: float
    close: float
    adj_close: float
    high: float
    low: float
    volume: PositiveInt
    datetime: int
    stock_code: str

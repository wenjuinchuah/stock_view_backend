from datetime import datetime

from sqlalchemy import Column, Integer, String, Double, BigInteger
from stock_indicators import Quote

from app.api.dependencies.database import Base
from app.api.models.price_list import PriceList
import app.api.crud.utils as Utils


class StockBase(Base):
    __tablename__ = "stock"

    stock_code = Column(String(50), primary_key=True)
    stock_name = Column(String(255))
    stock_full_name = Column(String(255))
    category = Column(String(255))
    updated_at = Column(Integer)


class PriceListBase(Base):
    __tablename__ = "price_list"

    pricelist_id = Column(String(50), primary_key=True)
    open = Column(Double)
    close = Column(Double)
    adj_close = Column(Double)
    high = Column(Double)
    low = Column(Double)
    volume = Column(BigInteger)
    datetime = Column(Integer)
    stock_code = Column(String(50))

    def to_price_list(self):
        return PriceList(
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

    def to_quote(self):
        return Quote(
            date=Utils.datetime_from_timestamp(self.datetime),
            open=round(self.open, 3),
            high=round(self.high, 3),
            low=round(self.low, 3),
            close=round(self.adj_close, 3),  # Use adjusted close price
            volume=float(self.volume),
        )

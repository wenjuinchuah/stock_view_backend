from sqlalchemy import Column, Integer, String, Double, Boolean, BigInteger

from app.api.dependencies.database import Base


class Stock(Base):
    __tablename__ = "stock"

    stock_code = Column(String(50), primary_key=True)
    stock_name = Column(String(255))
    category = Column(String(255))
    is_shariah = Column(Boolean)
    updated_at = Column(Integer)


class PriceList(Base):
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

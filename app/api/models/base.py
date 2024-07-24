from sqlalchemy import Column, Integer, String, Double, BigInteger, or_, func
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

    @staticmethod
    def get(db, stock_code: str) -> "StockBase":
        return db.query(StockBase).filter(StockBase.stock_code == stock_code).first()

    @staticmethod
    def get_all(db) -> list["StockBase"]:
        return db.query(StockBase).all()

    @staticmethod
    def update(db, stock: "StockBase") -> None:
        db.add(stock)
        db.commit()

    @staticmethod
    def search_by_code_and_name(db, query: str) -> list["StockBase"]:
        return (
            db.query(StockBase)
            .filter(
                or_(
                    StockBase.stock_name.startswith(query),
                    StockBase.stock_code.startswith(query),
                )
            )
            .all()
        )

    @staticmethod
    def get_index_by_stock_code(db, stock_code: str) -> int:
        all_stocks = StockBase.get_all(db)
        for index, stock in enumerate(all_stocks):
            if stock.stock_code == stock_code:
                return index + 1
        return -1


class PriceListBase(Base):
    __tablename__ = "price_list"

    pricelist_id = Column(String(50), primary_key=True)
    open = Column(Double)
    close = Column(Double)
    adj_close = Column(Double)
    high = Column(Double)
    low = Column(Double)
    volume = Column(BigInteger)
    timestamp = Column(Integer)
    stock_code = Column(String(50))

    def to_price_list(self) -> PriceList:
        return PriceList(
            pricelist_id=self.pricelist_id,
            open=self.open,
            close=self.close,
            adj_close=self.adj_close,
            high=self.high,
            low=self.low,
            volume=self.volume,
            timestamp=self.timestamp,
            stock_code=self.stock_code,
        )

    def to_quote(self) -> Quote:
        return Quote(
            date=Utils.timestamp_to_datetime(self.timestamp),
            open=round(self.open, 3),
            high=round(self.high, 3),
            low=round(self.low, 3),
            close=round(self.adj_close, 3),  # Use adjusted close price
            volume=float(self.volume),
        )

    @staticmethod
    def get_latest_timestamp(db) -> int:
        return db.query(func.max(PriceListBase.timestamp)).scalar()

    @staticmethod
    def get_latest_timestamp_by_stock_code(db, stock_code: str) -> int:
        return (
            db.query(func.max(PriceListBase.timestamp))
            .filter(PriceListBase.pricelist_id.startswith(stock_code))
            .scalar()
        )

    @staticmethod
    def get(db, pricelist_id: str) -> "PriceListBase":
        return db.query(PriceListBase).filter_by(pricelist_id=pricelist_id).first()

    @staticmethod
    def get_all_by_stock_code(db, stock_code: str) -> list["PriceListBase"]:
        return (
            db.query(PriceListBase)
            .filter(PriceListBase.pricelist_id.startswith(stock_code))
            .all()
        )

    @staticmethod
    def bulk_update(db, price_lists: list["PriceListBase"]) -> None:
        db.bulk_save_objects(price_lists)
        db.commit()

    @staticmethod
    def exists(db) -> bool:
        return db.query(db.query(PriceListBase).exists()).scalar()

    @staticmethod
    def get_last_updated_price_list_data(db) -> "PriceListBase":
        return (
            db.query(PriceListBase)
            .order_by(PriceListBase.stock_code.desc(), PriceListBase.timestamp.desc())
            .first()
        )

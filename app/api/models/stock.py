from pydantic import BaseModel


class Stock(BaseModel):
    stock_code: str
    stock_name: str
    stock_full_name: str
    category: str
    is_shariah: bool
    updated_at: int


class StockDetails(BaseModel):
    stock_code: str
    stock_name: str
    open: float
    close: float

    def __hash__(self):
        return hash((self.stock_code, self.stock_name, self.open, self.close))

    def __eq__(self, other):
        if isinstance(other, StockDetails):
            return (self.stock_code, self.stock_name, self.open, self.close) == (
                other.stock_code,
                other.stock_name,
                other.open,
                other.close,
            )
        return False

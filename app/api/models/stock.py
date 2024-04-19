from pydantic import BaseModel


class Stock(BaseModel):
    stock_code: str
    stock_name: str
    stock_full_name: str
    category: str
    updated_at: int


class StockDetails(BaseModel):
    stock_code: str
    stock_name: str
    close_price: float
    percentage_change: float

    def __hash__(self):
        return hash(
            (self.stock_code, self.stock_name, self.close_price, self.percentage_change)
        )

    def __eq__(self, other):
        if isinstance(other, StockDetails):
            return (
                self.stock_code,
                self.stock_name,
                self.close_price,
                self.percentage_change,
            ) == (
                other.stock_code,
                other.stock_name,
                other.close_price,
                other.percentage_change,
            )
        return False

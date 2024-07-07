from pydantic import BaseModel

from app.api.models.stock_indicator import Indicator


class Stock(BaseModel):
    stock_code: str
    stock_name: str
    stock_full_name: str
    category: str
    updated_at: int


class MatchedIndicator(BaseModel):
    indicator: Indicator
    matched_at: int

    def __hash__(self):
        return hash((self.indicator, self.matched_at))

    def __eq__(self, other):
        if isinstance(other, MatchedIndicator):
            return (self.indicator, self.matched_at) == (
                other.indicator,
                other.matched_at,
            )
        return False


class StockDetails(BaseModel):
    stock_code: str
    stock_name: str
    close_price: float
    percentage_change: float
    matched_indicator: list[MatchedIndicator] | None

    def __hash__(self):
        return hash(
            (
                self.stock_code,
                self.stock_name,
                self.close_price,
                self.percentage_change,
                tuple(self.matched_indicator) if self.matched_indicator else None,
            )
        )

    def __eq__(self, other):
        if isinstance(other, StockDetails):
            return (
                self.stock_code,
                self.stock_name,
                self.close_price,
                self.percentage_change,
                tuple(self.matched_indicator) if self.matched_indicator else None,
            ) == (
                other.stock_code,
                other.stock_name,
                other.close_price,
                other.percentage_change,
                tuple(other.matched_indicator) if other.matched_indicator else None,
            )
        return False

from pydantic import BaseModel

from app.api.models.stock import StockDetails
from app.api.models.stock_indicator import StockIndicator


class StockScreener(BaseModel):
    start_date: int
    end_date: int
    stock_indicator: StockIndicator | None = None
    last_stock_code: str | None = None
    page_size: int | None = 20


class StockScreenerResult(StockScreener):
    # list of stock code
    result: list[StockDetails] | None = None

    def add(self, stock_code_list: list):
        if not self.result:
            self.result = []

        self.result.extend(stock_code_list)

        # remove duplicates
        self.result = list(dict.fromkeys(self.result))

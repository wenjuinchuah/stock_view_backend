from pydantic import BaseModel

from app.api.models.stock_indicator import StockIndicator


class StockScreener(BaseModel):
    start_date: int
    end_date: int
    indicator_list: list[StockIndicator] | None = None


class StockScreenerResult(StockScreener):
    # list of stock code
    result: list[str] | None = None

    def append(self, stock_code: str):
        if not self.result:
            self.result = []

        self.result.append(stock_code)

        # remove duplicate
        self.result = list(dict.fromkeys(self.result))

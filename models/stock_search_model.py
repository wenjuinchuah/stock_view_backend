from pydantic import BaseModel


class CCIModel(BaseModel):
    length: int
    date_from: int
    date_to: int


class StockSearchModel(BaseModel):
    auto_adjust: bool
    cci: CCIModel | None = None

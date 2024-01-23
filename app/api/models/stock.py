from pydantic import BaseModel


class Stock(BaseModel):
    stock_code: str
    stock_name: str
    category: str
    is_shariah: bool
    updated_at: int

from fastapi import APIRouter

from app.api.constants import Response
from basemodel.stock_search_model import StockSearchModel
from controllers import stock_controller as StockController

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: Response.error()},
)


# @router.get("/get")
# def get_stock_by_stock_code(stock_code: str | None = None, auto_adjust: bool = True):
#     try:
#         if stock_code is None or stock_code == "":
#             raise Exception("Stock code is required")
#
#         stock_ticker = StockController.get_stock_ticker_data(stock_code, auto_adjust)
#         return Response.success(stock_ticker)
#     except Exception as e:
#         return Response.error(e)


@router.post("/search")
def search_stocks(stock_search_model: StockSearchModel, page_number: int = 1):
    try:
        if stock_search_model is None:
            raise Exception("Missing request body")
        results = StockController.search_stocks(stock_search_model, page_number)
        return Response.success(results)
    except Exception as e:
        return Response.error(e)


@router.get("/all_klse_stocks")
def get_all_klse_stocks():
    try:
        StockController.scrape()
        return Response.success()
    except Exception as e:
        return Response.error(e)

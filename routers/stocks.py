from fastapi import APIRouter
from pydantic import BaseModel
from constants import Response
from controllers import stock_controller as StockController
from models.stock_search_model import StockSearchModel


router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: Response.error},
)


@router.get("/")
def getStockByStockCode(stock_code: str, auto_adjust: bool = True):
    try:
        if stock_code is None or stock_code == "":
            raise Exception("Stock code is required")

        stock_ticker = StockController.getStockTickerData(stock_code, auto_adjust)
        Response.success["data"] = stock_ticker.__dict__
        return Response.success
    except Exception as error:
        Response.error["message"] = str(error)
        return Response.error


@router.post("/search")
def searchStocks(stockSearchModel: StockSearchModel, page_number: int = 1):
    try:
        if stockSearchModel is None:
            raise Exception("No request body")
        results = StockController.searchStocks(stockSearchModel, page_number)
        Response.success["data"] = results
        return Response.success
    except Exception as error:
        Response.error["message"] = str(error)
        return Response.error


@router.get("/all_klse_stocks")
def getAllKlseStocks():
    try:
        StockController.scrape()
        return Response.success
    except:
        return Response.error

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from constants import Response
from controllers import stock_controller as StockController
from models.stock_search_model import StockSearchModel


router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: Response.error()},
)


@router.get("/get")
def getStockByStockCode(stock_code: str | None = None, auto_adjust: bool = True):
    try:
        if stock_code is None or stock_code == "":
            raise Exception("Stock code is required")

        stock_ticker = StockController.getStockTickerData(stock_code, auto_adjust)
        return Response.success(stock_ticker)
    except Exception as e:
        return Response.error(e)


@router.post("/search")
def searchStocks(stockSearchModel: StockSearchModel, page_number: int = 1):
    try:
        if stockSearchModel is None:
            raise Exception("Missing request body")
        results = StockController.searchStocks(stockSearchModel, page_number)
        return Response.success(results)
    except Exception as e:
        return Response.error(e)


@router.get("/all_klse_stocks")
def getAllKlseStocks():
    try:
        StockController.scrape()
        return Response.success()
    except:
        return Response.error()

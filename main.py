from flask import Flask, request
from flask_cors import CORS
from stock.stock_scraper import StockScrape
import stock.stock_controller as StockController
from constant import Indicator, Response

app = Flask(__name__)
CORS(app)


@app.get("/stock")
def getStockByStockCode():
    args = request.args
    stock_code = args.get("stock_code")
    try:
        stock_ticker = StockController.getStockTickerData(stock_code)
        Response.success["data"] = stock_ticker.__dict__
        return Response.success
    except:
        return Response.error


@app.get("/stock/indicator")
def getIndicator():
    args = request.args
    stock_code = args.get("stock_code")
    indicator = args.get("indicator")

    try:
        results = StockController.getIndicator(stock_code, indicator)
        Response.success["data"] = results
        return Response.success
    except Exception as error:
        Response.error["message"] = error
        return Response.error


@app.get("/all_klse_stocks")
def getAllKlseStocks():
    try:
        results = StockScrape.get()
        Response.success["data"] = results
        return Response.success
    except:
        return Response.error


if __name__ == "__main__":
    app.run(port=8000, debug=True)

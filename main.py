from flask import Flask, request, json
from flask_cors import CORS
from stock.stock_scraper import StockScrape
import stock.stock_controller as StockController
from constant import Indicator, Response

app = Flask(__name__)
CORS(app)

# /stock
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


@app.post("/stock/search")
def searchStocks():
    try:
        args = request.args
        page_number = args.get("page_number")
        data_dict = request.get_json(silent=True)
        if data_dict is None:
            raise Exception("No request body")

        results = StockController.searchStocks(data_dict, int(page_number))
        Response.success["data"] = results
        return Response.success
    except Exception as error:
        Response.error["message"] = str(error)
        return Response.error

# /all_klse_stocks
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

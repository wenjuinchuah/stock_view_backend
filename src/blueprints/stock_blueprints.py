from flask import Blueprint, request
from src.constant import Response
import src.controllers.stock_controller as StockController

stock_blueprint = Blueprint("stock_blueprint", __name__)

@stock_blueprint.route("/", methods=["GET"])
def getStockByStockCode():
    args = request.args
    stock_code = args.get("stock_code")
    auto_adjust = args.get("auto_adjust")
    try:
        stock_ticker = StockController.getStockTickerData(stock_code, auto_adjust)
        Response.success["data"] = stock_ticker.__dict__
        return Response.success
    except:
        return Response.error

@stock_blueprint.route("/search", methods=["POST"])
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

@stock_blueprint.route("/all_klse_stocks", methods=["GET"])
def getAllKlseStocks():
    try:
        results = StockController.scrape()
        Response.success["data"] = results
        return Response.success
    except:
        return Response.error
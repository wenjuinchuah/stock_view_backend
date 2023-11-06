from flask import Flask, request
from flask_cors import CORS
from src.blueprints.stock_blueprints import stock_blueprint

app = Flask(__name__)
app.register_blueprint(stock_blueprint, url_prefix="/api/v1/stock")
CORS(app)
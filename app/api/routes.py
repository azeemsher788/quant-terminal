import re
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from app import cache
from app.services.market_data import MarketDataService
from app.utils.validators import parse_ticker_list, parse_int_param

api_bp = Blueprint('api', __name__)

@api_bp.route('/market/<symbol>', methods=['GET'])
@cache.cached(timeout=3600)
def get_market_data(symbol: str):
    """
    Fetch historical daily market data for a given symbol.
    """
    if not symbol or not symbol.isalnum():
        raise BadRequest("Invalid symbol format.")
        
    symbol = symbol.upper()
    data = MarketDataService.get_historical_data(symbol)
    
    return jsonify(data), 200


@api_bp.route('/news', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_news():
    """
    Fetch top market news headlines.
    Query parameters:
      - tickers: comma separated list of tickers (default: AAPL,MSFT,IBM)
      - limit: number of news items to fetch (default: 5, max: 15)
    """
    tickers = parse_ticker_list(request.args.get('tickers', ''), default='AAPL,MSFT,IBM')
    limit = parse_int_param(request.args.get('limit', ''), default=5, min_val=1, max_val=15)
        
    data = MarketDataService.get_news(tickers, limit)
    
    return jsonify(data), 200

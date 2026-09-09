from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from app import cache
from app.services.market_data import MarketDataService

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
    tickers_param = request.args.get('tickers', 'AAPL,MSFT,IBM')
    tickers = [t.strip().upper() for t in tickers_param.split(',') if t.strip()]
    
    if not tickers:
        raise BadRequest("Invalid tickers format.")
        
    try:
        limit = int(request.args.get('limit', 5))
        limit = min(max(1, limit), 15)
    except ValueError:
        raise BadRequest("Invalid limit parameter. Must be an integer.")
        
    data = MarketDataService.get_news(tickers, limit)
    
    return jsonify(data), 200

import os
import logging
from typing import Dict, Any, Tuple
from flask import Flask, render_template, jsonify
from flask_caching import Cache
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Caching (FileSystemCache to survive server restarts)
# This prevents exhausting the strict 25 req/day API limit during development
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": ".flask_cache",
    "CACHE_DEFAULT_TIMEOUT": 3600 # Cache for 1 hour to save API calls
}
app.config.from_mapping(cache_config)
cache = Cache(app)

API_KEY = os.getenv("API_KEY", "demo")
BASE_URL = "https://www.alphavantage.co/query"

@app.route('/')
def index() -> str:
    """Render the main dashboard interface."""
    return render_template('index.html')

@app.route('/api/market/<symbol>')
def get_market_data(symbol: str) -> Tuple[Any, int]:
    """
    Fetch historical daily market data for a given symbol.
    Cached manually to prevent caching API rate limit errors.
    """
    cache_key = f'market_data_v3_{symbol}'
    cached_response = cache.get(cache_key)
    if cached_response:
        return jsonify(cached_response), 200

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "compact"
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "Information" in data or "Note" in data:
            logger.warning(f"API Rate Limit or Info message received: {data}")
            return jsonify({"error": "API Rate Limit Exceeded. Please try again later."}), 429
            
        if "Error Message" in data:
            logger.error(f"API Error for symbol {symbol}: {data['Error Message']}")
            return jsonify({"error": "Invalid symbol or API error."}), 400
            
        time_series = data.get("Time Series (Daily)", {})
        formatted_data = []
        
        for date, metrics in time_series.items():
            formatted_data.append({
                "time": date,
                "open": float(metrics["1. open"]),
                "high": float(metrics["2. high"]),
                "low": float(metrics["3. low"]),
                "close": float(metrics["4. close"])
            })
            
        formatted_data.sort(key=lambda x: x["time"])
        
        response_data = {
            "symbol": symbol,
            "data": formatted_data
        }
        
        # Only cache successful data!
        cache.set(cache_key, response_data, timeout=3600)
        return jsonify(response_data), 200
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to market data provider timed out."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to market data provider."}), 502
    except Exception as e:
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/news')
def get_news() -> Tuple[Any, int]:
    """
    Fetch top market news headlines.
    Cached manually to prevent caching API rate limit errors.
    """
    cache_key = 'market_news_v3'
    cached_response = cache.get(cache_key)
    if cached_response:
        return jsonify(cached_response), 200

    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": "AAPL,MSFT,IBM",
        "apikey": API_KEY,
        "limit": 5
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # DEBUG LOGGING FOR THE USER
        with open("news_debug.log", "w") as f:
            f.write(str(data))
            
        if "Information" in data or "Note" in data:
            return jsonify({"error": "API Rate Limit Exceeded."}), 429
            
        if "Error Message" in data:
            return jsonify({"error": data["Error Message"]}), 400
            
        feed = data.get("feed", [])
        news_data = []
        for item in feed[:5]:
            news_data.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "time_published": item.get("time_published"),
                "source": item.get("source"),
                "summary": item.get("summary")
            })
            
        response_data = {"news": news_data}
        
        # Only cache successful data!
        cache.set(cache_key, response_data, timeout=3600)
        return jsonify(response_data), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Unable to fetch news: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Internal error fetching news: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)

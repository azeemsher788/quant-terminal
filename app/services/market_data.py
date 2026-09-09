import logging
from typing import Dict, Any, List

import requests
from flask import current_app
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.errors import ExternalAPIError, RateLimitExceeded

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service to interact with the Alpha Vantage API."""
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def _make_request(params: Dict[str, Any]) -> Dict[str, Any]:
        """Makes a GET request to the Alpha Vantage API."""
        base_url = current_app.config.get("ALPHA_VANTAGE_BASE_URL")
        api_key = current_app.config.get("API_KEY")
        
        if not api_key:
            raise ValueError("API_KEY is not configured.")
            
        params["apikey"] = api_key
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Alpha Vantage returns HTTP 200 even for rate limits, so we check payload
            if "Information" in data or "Note" in data:
                logger.warning(f"API Rate Limit or Info message received: {data}")
                raise RateLimitExceeded("API Rate Limit Exceeded. Please try again later.")
                
            if "Error Message" in data:
                error_msg = data.get("Error Message", "Unknown external API error")
                logger.error(f"Alpha Vantage API Error: {error_msg}")
                raise ExternalAPIError(f"Invalid request or API error: {error_msg}", status_code=400)
                
            return data
            
        except requests.exceptions.Timeout:
            logger.error("Request to Alpha Vantage timed out.")
            raise ExternalAPIError("Request to market data provider timed out.", status_code=504)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Alpha Vantage: {e}")
            raise ExternalAPIError("Failed to connect to market data provider.", status_code=502)

    @classmethod
    def get_historical_data(cls, symbol: str) -> Dict[str, Any]:
        """
        Fetches and formats historical daily market data.
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact"
        }
        
        data = cls._make_request(params)
        time_series = data.get("Time Series (Daily)", {})
        
        formatted_data = []
        for date, metrics in time_series.items():
            try:
                formatted_data.append({
                    "time": date,
                    "open": float(metrics["1. open"]),
                    "high": float(metrics["2. high"]),
                    "low": float(metrics["3. low"]),
                    "close": float(metrics["4. close"])
                })
            except (KeyError, ValueError) as e:
                logger.warning(f"Malformed data point for {symbol} on {date}: {e}")
                continue
                
        # Sort chronologically (oldest first)
        formatted_data.sort(key=lambda x: x["time"])
        
        if not formatted_data:
            raise ExternalAPIError(f"No valid time series data found for symbol: {symbol}", status_code=404)
            
        return {
            "symbol": symbol,
            "data": formatted_data
        }

    @classmethod
    def get_news(cls, tickers: List[str], limit: int = 5) -> Dict[str, Any]:
        """
        Fetches top market news headlines.
        """
        tickers_str = ",".join(tickers)
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": tickers_str,
            "limit": limit
        }
        
        data = cls._make_request(params)
        feed = data.get("feed", [])
        
        news_data = []
        for item in feed[:limit]:
            news_data.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "time_published": item.get("time_published"),
                "source": item.get("source"),
                "summary": item.get("summary")
            })
            
        return {"news": news_data}

import pytest
import responses
from unittest.mock import patch
from app.services.market_data import MarketDataService
from app.errors import RateLimitExceeded, ExternalAPIError


@pytest.fixture(autouse=True)
def mock_sleep():
    """Mock time.sleep globally to avoid slowing down tests due to tenacity retries."""
    with patch('time.sleep', return_value=None):
        yield


@responses.activate
def test_get_historical_data_success(app):
    with app.app_context():
        # Mock successful Alpha Vantage response
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={
                "Time Series (Daily)": {
                    "2023-10-01": {"1. open": "150.0", "2. high": "155.0", "3. low": "149.0", "4. close": "154.0"}
                }
            },
            status=200,
        )

        result = MarketDataService.get_historical_data("IBM")
        assert result["symbol"] == "IBM"
        assert len(result["data"]) == 1
        assert result["data"][0]["close"] == 154.0


@responses.activate
def test_get_historical_data_rate_limit(app):
    with app.app_context():
        # Mock rate limit response
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={
                "Information": (
                    "Thank you for using Alpha Vantage! "
                    "Our standard API call frequency is 5 calls per minute and 500 calls per day."
                )
            },
            status=200,
        )

        with pytest.raises(RateLimitExceeded):
            MarketDataService.get_historical_data("IBM")


@responses.activate
def test_get_historical_data_invalid_symbol(app):
    with app.app_context():
        # Mock error response
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={"Error Message": "Invalid API call. Please retry or visit the documentation."},
            status=200,
        )

        with pytest.raises(ExternalAPIError) as excinfo:
            MarketDataService.get_historical_data("INVALID_SYMBOL")
        assert excinfo.value.status_code == 400

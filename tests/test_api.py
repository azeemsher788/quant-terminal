from unittest.mock import patch

def test_index_route(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Financial Market Terminal" in response.data

@patch('app.services.market_data.MarketDataService.get_historical_data')
def test_get_market_data_success(mock_get_data, client):
    """Test successful market data retrieval via API endpoint."""
    mock_get_data.return_value = {
        "symbol": "IBM",
        "data": [{"time": "2023-10-01", "close": 150.0}]
    }
    
    response = client.get('/api/market/IBM')
    assert response.status_code == 200
    data = response.get_json()
    assert data["symbol"] == "IBM"
    assert len(data["data"]) == 1

def test_get_market_data_invalid_symbol_format(client):
    """Test validation of symbol format."""
    response = client.get('/api/market/IBM!@#')
    assert response.status_code == 400
    assert "error" in response.get_json()

@patch('app.services.market_data.MarketDataService.get_news')
def test_get_news_success(mock_get_news, client):
    """Test successful news retrieval via API endpoint."""
    mock_get_news.return_value = {
        "news": [{"title": "Market up today"}]
    }
    
    response = client.get('/api/news?tickers=IBM&limit=1')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["news"]) == 1

def test_404_error_handler(client):
    """Test global 404 error handler."""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404
    assert "error" in response.get_json()

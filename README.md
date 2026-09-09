# Quant Terminal

![Quant Terminal Interface](preview.png)

## Overview

Quant Terminal is a production-grade, highly polished web application demonstrating complex API consumption, server-side caching, and advanced front-end data visualization. Built for the modern web, it features a bespoke financial terminal aesthetic inspired by Bloomberg Terminal, blending dark mode, sleek typography, and high-performance interactive charting.

This project goes beyond a simple tutorial clone by addressing real-world software engineering concerns: robust error handling, API rate limiting, separation of concerns through an application factory pattern, comprehensive test coverage, and production-ready containerization.

## Problem Solved

Financial data APIs (like Alpha Vantage) impose strict rate limits and can be slow. Direct client-side consumption risks exposing API keys and easily hitting limits. Quant Terminal solves this by providing a resilient backend proxy layer that caches responses, normalizes complex nested JSON, handles timeouts gracefully, and serves a high-performance interactive UI.

## Key Features

- **Robust REST API Integration:** Securely consumes the Alpha Vantage API. API keys are completely isolated from the front-end via environment variables.
- **Server-Side Data Caching:** Implements declarative `@cache.cached()` with `Flask-Caching` to handle strict rate limits imposed by public APIs, significantly reducing latency and boilerplate code.
- **External API Resilience:** Integrates `tenacity` for exponential backoff and retry logic, enabling the service to transparently recover from transient network errors and third-party rate limits.
- **Strict Request Validation:** Employs a dedicated validation module to parse, clean, and validate all incoming query parameters and inputs, enforcing the Single Responsibility Principle.
- **Advanced Error Handling:** Gracefully handles and propagates HTTP 429 (Too Many Requests), 500 (Internal Server Error), and network timeouts, providing clear visual feedback to the user via custom error handlers.
- **High-Performance Visualization:** Integrates TradingView's Lightweight Charts via Canvas API for butter-smooth time-series financial data rendering.
- **Security Best Practices:** Employs `Flask-Limiter` for endpoint protection and `Flask-Talisman` for HTTP security headers (CSP, HSTS).
- **Modular Frontend Architecture:** Uses native ES6 modules (`api.js`, `chart.js`, `ui.js`) for a clean, maintainable, and dependency-free frontend logic layer.

## Technology Stack

- **Backend:** Python 3.11, Flask, Flask-Caching, Flask-Limiter, Flask-Talisman, requests
- **Frontend:** HTML5, Vanilla CSS3 (Custom grid/flexbox, CSS variables), Vanilla JavaScript (ES6 Modules)
- **Charting:** TradingView Lightweight Charts
- **Testing:** Pytest, responses (for API mocking)
- **Infrastructure:** Docker, Gunicorn, GitHub Actions (CI)

## Architecture

1. **Application Factory Pattern:** The Flask app is instantiated via a factory (`app/__init__.py`), allowing for isolated environments (Development, Testing, Production) and making the application highly testable.
2. **Service Layer:** Business logic (fetching and normalizing API data) is decoupled from routing. The `MarketDataService` abstracts the complexities of the external API, making the routes (`app/api/routes.py`) thin and focused on HTTP.
3. **Caching Strategy:** Time-series data and news sentiment are cached on the server for 1 hour. This drastically reduces outbound network requests and prevents hitting the 25 requests/day limit on free tier APIs.

## Getting Started

### Prerequisites
- Python 3.11+
- An Alpha Vantage API Key (Free tier is sufficient)
- Docker (Optional, for containerized running)

### Installation (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/azeemsher788/quant-terminal.git
   cd quant-terminal
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env and replace 'demo' with your Alpha Vantage API key
   ```

5. **Run the Application**
   ```bash
   python run.py
   ```
   The application will be available at `http://localhost:5000`.

### Running with Docker
```bash
docker build -t quant-terminal .
docker run -p 5000:5000 --env-file .env quant-terminal
```

## Testing

The project includes a comprehensive Pytest suite covering the service layer, error handling, and API integration.

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Interesting Engineering Challenges

- **Handling False 200s:** Alpha Vantage returns HTTP 200 even when an API key is invalid or a rate limit is hit, returning the error in the JSON payload instead. The `MarketDataService` explicitly checks the payload structure to correctly raise custom `RateLimitExceeded` or `ExternalAPIError` exceptions, converting them to proper HTTP 429 and 400/502 status codes for the frontend.
- **Frontend Modularity Without a Framework:** To keep the footprint small and performant, I eschewed React/Vue in favor of native ES6 modules. This required careful management of DOM element initialization and chart lifecycle events to prevent race conditions during rendering.

## Future Improvements
- Migrate caching backend from `FileSystemCache` to `Redis` for distributed environments.
- Implement WebSockets for real-time tick-level data updates.

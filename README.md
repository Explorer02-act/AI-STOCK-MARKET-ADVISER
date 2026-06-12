# stock_market_analyser

AI stock research app for Indian equities. It combines live Yahoo Finance data,
technical indicators, cached news sentiment, fundamentals, SQLite watchlists,
portfolio tracking, FastAPI endpoints, LangGraph research flow, Streamlit UI,
Redis caching, PostgreSQL persistence hooks, WebSocket streaming, and Prometheus
metrics.

This project is for education and research. It does not provide personalized
investment advice.

## Features

- Indian stock symbols with NSE/BSE support: `RELIANCE.NS`, `TCS.NS`,
  `INFY.NS`, `HDFCBANK.NS`, `SBIN.BO`
- Current price, previous close, market cap, sector, industry, and currency
- Technical analysis: SMA 20, SMA 50, EMA, RSI 14, MACD, Bollinger bands
- News sentiment with VADER through NewsAPI, cached to reduce rate-limit usage
- Stock comparison and sector/fundamental comparison
- SQLite watchlist and simple portfolio tracker
- Indian market-hours messaging in IST
- Streamlit dashboard with charts, sentiment table, portfolio cards, and PDF
  report export
- FastAPI endpoints for analysis, comparison, watchlists, portfolio, health,
  metrics, and WebSocket stock streams

## Local Setup

1. Copy `.env.example` to `.env`.
2. Add keys as needed:

```bash
GROQ_API_KEY=your_groq_key
NEWS_API_KEY=your_newsapi_key
```

`NEWS_API_KEY` is optional. Without it, the app still runs and reports neutral
news sentiment with a setup message.

3. Start optional infrastructure:

```bash
docker compose up -d postgres redis
```

4. Run the API:

```bash
uvicorn backend.main:app --reload
```

5. Run the Streamlit UI:

```bash
streamlit run backend/app/streamlit_app.py
```

## API Endpoints

- `GET /health`
- `GET /metrics`
- `GET /market/status`
- `GET /stocks/analyse/RELIANCE.NS`
- `GET /stocks/compare?tickers=RELIANCE.NS,TCS.NS,INFY.NS`
- `GET /stocks/sector-compare?tickers=HDFCBANK.NS,SBIN.NS`
- `GET /watchlist`
- `POST /watchlist`
- `DELETE /watchlist/{ticker}`
- `POST /portfolio/positions`
- `GET /portfolio`
- `WS /ws/stocks?tickers=RELIANCE.NS,TCS.NS`

## Demo Flow

1. Open the Streamlit dashboard.
2. Analyse `RELIANCE.NS` and show the candlestick chart with SMA and RSI.
3. Review fundamentals, news sentiment, and download the PDF report.
4. Compare `RELIANCE.NS,TCS.NS,INFY.NS`.
5. Save stocks to the watchlist.
6. Add a portfolio position and review P&L cards.
7. Ask the agent: `Compare Reliance, TCS, and Infosys using technicals and sentiment`.

## Testing

```bash
.\venv\Scripts\python.exe -m pytest tests -q
```

The local `.pytest_cache` directory may show a permission warning on Windows;
that does not affect the test results.

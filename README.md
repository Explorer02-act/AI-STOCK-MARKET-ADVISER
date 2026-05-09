# stock_market_analyser

AI stock research app for Indian equities with Streamlit, FastAPI, LangGraph,
Redis caching, PostgreSQL persistence, WebSocket streaming, and Prometheus
metrics.

## Local setup

1. Copy `.env.example` to `.env` and fill in `GROQ_API_KEY`.
2. Start infrastructure:

```bash
docker compose up -d postgres redis
```

3. Run the API:

```bash
uvicorn backend.main:app --reload
```

4. Run the Streamlit UI:

```bash
streamlit run backend/app/streamlit_app.py
```

## Runtime endpoints

- `GET /health` checks API and Redis availability.
- `GET /metrics` exposes Prometheus metrics for request volume, failures, rate
  limit gauges, and estimated API cost.
- `WS /ws/stocks?tickers=RELIANCE.NS,TCS.NS` streams live stock snapshots.

## Testing

```bash
pytest tests -q
```

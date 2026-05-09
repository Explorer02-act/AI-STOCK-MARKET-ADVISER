from __future__ import annotations

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from backend.cache import cache
from backend.streaming.market_stream import stock_price_stream
from configs.settings import APP_NAME, POPULAR_INDIAN_STOCKS
from database.connection import init_db

app = FastAPI(title=APP_NAME)


@app.on_event("startup")
def startup() -> None:
    try:
        init_db()
    except Exception:
        # The API can still serve market data if PostgreSQL is temporarily down.
        pass


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "redis": "available" if cache.available else "unavailable",
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws/stocks")
async def websocket_stocks(
    websocket: WebSocket,
    tickers: str = Query(default=",".join(POPULAR_INDIAN_STOCKS[:3])),
) -> None:
    await websocket.accept()
    ticker_list = [ticker for ticker in tickers.split(",") if ticker.strip()]
    try:
        async for payload in stock_price_stream(ticker_list):
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        return

from __future__ import annotations

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from backend.analysis.portfolio import portfolio_summary
from backend.analysis.stock_analysis import analyse_stock, compare_sector, compare_stocks
from backend.cache import cache
from backend.market.indian_market import indian_market_status, is_valid_indian_symbol, normalize_indian_symbol
from backend.streaming.market_stream import stock_price_stream
from configs.settings import APP_NAME, POPULAR_INDIAN_STOCKS
from database.connection import init_db
from database.watchlist_store import add_watchlist_item, init_watchlist_db, list_watchlist_items, remove_watchlist_item, upsert_position

app = FastAPI(title=APP_NAME)


class WatchlistItemRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=24)
    list_name: str = "default"
    notes: str = ""


class PortfolioPositionRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=24)
    quantity: float = Field(..., gt=0)
    average_price: float = Field(..., gt=0)


@app.on_event("startup")
def startup() -> None:
    try:
        init_db()
    except Exception:
        # The API can still serve market data if PostgreSQL is temporarily down.
        pass
    init_watchlist_db()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "redis": "available" if cache.available else "unavailable",
    }


@app.get("/market/status")
def market_status() -> dict:
    return indian_market_status()


@app.get("/stocks/analyse/{ticker}")
def stock_analysis(ticker: str) -> dict:
    normalized = normalize_indian_symbol(ticker)
    if not is_valid_indian_symbol(normalized):
        return {"error": "Use an Indian Yahoo Finance symbol such as RELIANCE.NS or TCS.BO."}
    return analyse_stock(normalized)


@app.get("/stocks/compare")
def stock_compare(tickers: str = Query(..., description="Comma-separated tickers")) -> dict:
    symbols = [normalize_indian_symbol(ticker) for ticker in tickers.split(",") if ticker.strip()]
    invalid = [symbol for symbol in symbols if not is_valid_indian_symbol(symbol)]
    if invalid:
        return {"error": f"Invalid Indian stock symbol(s): {', '.join(invalid)}"}
    return {"stocks": compare_stocks(symbols[:8])}


@app.get("/stocks/sector-compare")
def sector_compare(tickers: str = Query(..., description="Comma-separated tickers from a sector")) -> dict:
    symbols = [normalize_indian_symbol(ticker) for ticker in tickers.split(",") if ticker.strip()]
    return {"stocks": compare_sector(symbols[:8])}


@app.get("/watchlist")
def get_watchlist(list_name: str = "default") -> dict:
    return {"items": list_watchlist_items(list_name)}


@app.post("/watchlist")
def add_to_watchlist(item: WatchlistItemRequest) -> dict:
    ticker = add_watchlist_item(item.ticker, item.list_name, item.notes)
    return {"ticker": ticker, "status": "saved"}


@app.delete("/watchlist/{ticker}")
def delete_from_watchlist(ticker: str, list_name: str = "default") -> dict:
    remove_watchlist_item(ticker, list_name)
    return {"ticker": normalize_indian_symbol(ticker), "status": "removed"}


@app.post("/portfolio/positions")
def add_portfolio_position(position: PortfolioPositionRequest) -> dict:
    ticker = upsert_position(position.ticker, position.quantity, position.average_price)
    return {"ticker": ticker, "status": "saved"}


@app.get("/portfolio")
def get_portfolio() -> dict:
    return portfolio_summary()


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

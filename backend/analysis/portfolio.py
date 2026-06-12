from __future__ import annotations

from typing import Any

from backend.data_pipeline.stock_fetcher import get_stock_price
from database.watchlist_store import list_positions


def portfolio_summary() -> dict[str, Any]:
    positions = list_positions()
    rows = []
    invested = 0.0
    current_value = 0.0
    for position in positions:
        ticker = position["ticker"]
        quantity = float(position["quantity"] or 0)
        average_price = float(position["average_price"] or 0)
        price_data = get_stock_price(ticker)
        current_price = price_data.get("current_price")
        invested_value = quantity * average_price
        market_value = quantity * current_price if isinstance(current_price, (int, float)) else 0.0
        pnl = market_value - invested_value
        invested += invested_value
        current_value += market_value
        rows.append(
            {
                "ticker": ticker,
                "quantity": quantity,
                "average_price": round(average_price, 2),
                "current_price": current_price,
                "invested_value": round(invested_value, 2),
                "market_value": round(market_value, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round((pnl / invested_value) * 100, 2) if invested_value else 0,
            }
        )
    total_pnl = current_value - invested
    return {
        "positions": rows,
        "invested": round(invested, 2),
        "current_value": round(current_value, 2),
        "pnl": round(total_pnl, 2),
        "pnl_pct": round((total_pnl / invested) * 100, 2) if invested else 0,
    }

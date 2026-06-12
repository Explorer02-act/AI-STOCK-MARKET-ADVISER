from __future__ import annotations

from typing import Any

from backend.analysis.technical_analysis import summarize_technicals
from backend.data_pipeline.stock_fetcher import get_stock_history, get_stock_price
from backend.tools.news_sentiment import get_news_sentiment


def analyse_stock(ticker: str, period: str = "6mo") -> dict[str, Any]:
    normalized = ticker.strip().upper()
    price = get_stock_price(normalized)
    history = get_stock_history(normalized, period=period)
    technicals = summarize_technicals(history)
    sentiment = get_news_sentiment(normalized)
    return {
        "ticker": normalized,
        "price": price,
        "technicals": technicals,
        "sentiment": sentiment,
    }


def compare_stocks(tickers: list[str], period: str = "6mo") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ticker in tickers:
        analysis = analyse_stock(ticker, period=period)
        price = analysis["price"]
        technicals = analysis["technicals"]
        sentiment = analysis["sentiment"]
        current = price.get("current_price")
        previous = price.get("previous_close")
        change_pct = None
        if isinstance(current, (int, float)) and isinstance(previous, (int, float)) and previous:
            change_pct = round(((current - previous) / previous) * 100, 2)

        rows.append(
            {
                "ticker": analysis["ticker"],
                "name": price.get("name", analysis["ticker"]),
                "price": current,
                "previous_close": previous,
                "change_pct": change_pct,
                "sector": price.get("sector", "N/A"),
                "market_cap": price.get("market_cap", "N/A"),
                "rsi_14": technicals.get("rsi_14"),
                "sma_20": technicals.get("sma_20"),
                "sma_50": technicals.get("sma_50"),
                "trend": technicals.get("trend"),
                "sentiment": sentiment.get("sentiment"),
                "sentiment_score": sentiment.get("score"),
            }
        )
    return rows


def format_analysis_context(analysis: dict[str, Any]) -> str:
    price = analysis["price"]
    technicals = analysis["technicals"]
    sentiment = analysis["sentiment"]
    return (
        f"Ticker: {analysis['ticker']}\n"
        f"Company: {price.get('name')}\n"
        f"Current price: INR {price.get('current_price')}\n"
        f"Previous close: INR {price.get('previous_close')}\n"
        f"Sector: {price.get('sector')}\n"
        f"Market cap: INR {price.get('market_cap')}\n"
        f"Technical signal: {technicals.get('signal')}\n"
        f"20-day SMA: {technicals.get('sma_20')}\n"
        f"50-day SMA: {technicals.get('sma_50')}\n"
        f"RSI(14): {technicals.get('rsi_14')}\n"
        f"News sentiment: {sentiment.get('sentiment')} ({sentiment.get('score')})"
    )

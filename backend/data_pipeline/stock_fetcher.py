from __future__ import annotations

from typing import Any

import pandas as pd
import yfinance as yf
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.cache import cache
from backend.data_pipeline.errors import StockDataUnavailable
from backend.monitoring import UsageEvent, usage_monitor
from backend.market.indian_market import normalize_indian_symbol
from configs.settings import DEFAULT_PERIOD, DEFAULT_INTERVAL


def _safe_round(value: Any) -> float | str:
    if value is None:
        return "N/A"
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return "N/A"


def _fast_value(fast_info: Any, key: str, default: Any = None) -> Any:
    if isinstance(fast_info, dict):
        return fast_info.get(key, default)
    return getattr(fast_info, key, default)


def _fallback_price(ticker: str, error: Exception | None = None) -> dict:
    return {
        "ticker": ticker,
        "name": ticker,
        "current_price": "N/A",
        "previous_close": "N/A",
        "market_cap": "N/A",
        "currency": "INR",
        "sector": "N/A",
        "error": str(error) if error else None,
    }


@retry(
    retry=retry_if_exception_type((StockDataUnavailable, TimeoutError, ConnectionError)),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _fetch_stock_price(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    fast = stock.fast_info
    current_price = _fast_value(fast, "last_price")
    if current_price is None:
        raise StockDataUnavailable(f"No latest price returned for {ticker}")

    return {
        "ticker": ticker,
        "name": ticker,
        "current_price": _safe_round(current_price),
        "previous_close": _safe_round(_fast_value(fast, "previous_close")),
        "market_cap": _fast_value(fast, "market_cap", "N/A") or "N/A",
        "currency": _fast_value(fast, "currency", "INR") or "INR",
        "sector": "N/A",
    }


def get_stock_price(ticker: str) -> dict:
    ticker = normalize_indian_symbol(ticker)
    cache_key = f"stock:price:{ticker}"
    cached = cache.get_json(cache_key)
    if cached:
        usage_monitor.record(UsageEvent("redis", "stock_price_cache", "hit"))
        return cached

    try:
        usage_monitor.record(UsageEvent("yfinance", "fast_info", "request"))
        data = _fetch_stock_price(ticker)
        cache.set_json(cache_key, data)
        usage_monitor.record(UsageEvent("yfinance", "fast_info", "success"))
        return data
    except Exception as e:
        usage_monitor.record_failure("yfinance", "fast_info", e)
        return _fallback_price(ticker, e)


@retry(
    retry=retry_if_exception_type((StockDataUnavailable, TimeoutError, ConnectionError)),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _fetch_stock_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    history = stock.history(period=period, interval=interval)
    if history is None or history.empty:
        raise StockDataUnavailable(f"No history returned for {ticker}")
    return history


def get_stock_history(ticker: str, period: str = DEFAULT_PERIOD, interval: str = DEFAULT_INTERVAL) -> pd.DataFrame:
    ticker = normalize_indian_symbol(ticker)
    try:
        usage_monitor.record(UsageEvent("yfinance", "history", "request"))
        history = _fetch_stock_history(ticker, period, interval)
        usage_monitor.record(UsageEvent("yfinance", "history", "success"))
        return history
    except Exception as e:
        usage_monitor.record_failure("yfinance", "history", e)
        return pd.DataFrame()


def get_multiple_stocks(tickers: list) -> list:
    return [get_stock_price(t) for t in tickers]


def get_fundamentals(ticker: str) -> dict:
    ticker = normalize_indian_symbol(ticker)
    cache_key = f"stock:fundamentals:{ticker}"
    cached = cache.get_json(cache_key)
    if cached:
        usage_monitor.record(UsageEvent("redis", "fundamentals_cache", "hit"))
        return cached

    try:
        usage_monitor.record(UsageEvent("yfinance", "info", "request"))
        info = yf.Ticker(ticker).info or {}
        data = {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "trailing_pe": _safe_round(info.get("trailingPE")),
            "forward_pe": _safe_round(info.get("forwardPE")),
            "debt_to_equity": _safe_round(info.get("debtToEquity")),
            "revenue_growth": _safe_round(info.get("revenueGrowth")),
            "profit_margins": _safe_round(info.get("profitMargins")),
            "return_on_equity": _safe_round(info.get("returnOnEquity")),
            "market_cap": info.get("marketCap", "N/A") or "N/A",
            "currency": info.get("financialCurrency") or info.get("currency") or "INR",
        }
        cache.set_json(cache_key, data, ttl_seconds=3600)
        usage_monitor.record(UsageEvent("yfinance", "info", "success"))
        return data
    except Exception as e:
        usage_monitor.record_failure("yfinance", "info", e)
        return {
            "ticker": ticker,
            "name": ticker,
            "sector": "N/A",
            "industry": "N/A",
            "trailing_pe": "N/A",
            "forward_pe": "N/A",
            "debt_to_equity": "N/A",
            "revenue_growth": "N/A",
            "profit_margins": "N/A",
            "return_on_equity": "N/A",
            "market_cap": "N/A",
            "currency": "INR",
            "error": str(e),
        }

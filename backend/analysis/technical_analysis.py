from __future__ import annotations

import math
from typing import Any

import pandas as pd


def _last_number(series: pd.Series) -> float | None:
    if series.empty:
        return None
    value = series.dropna().iloc[-1] if not series.dropna().empty else None
    if value is None or not math.isfinite(float(value)):
        return None
    return round(float(value), 2)


def add_technical_indicators(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty or "Close" not in history.columns:
        return history.copy()

    df = history.copy()
    close = df["Close"]
    df["SMA_20"] = close.rolling(window=20, min_periods=1).mean()
    df["SMA_50"] = close.rolling(window=50, min_periods=1).mean()
    df["EMA_12"] = close.ewm(span=12, adjust=False).mean()
    df["EMA_26"] = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["RSI_14"] = calculate_rsi(close)

    middle = close.rolling(window=20, min_periods=1).mean()
    std = close.rolling(window=20, min_periods=1).std().fillna(0)
    df["BB_UPPER"] = middle + (2 * std)
    df["BB_LOWER"] = middle - (2 * std)
    return df


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def summarize_technicals(history: pd.DataFrame) -> dict[str, Any]:
    df = add_technical_indicators(history)
    if df.empty:
        return {
            "sma_20": None,
            "sma_50": None,
            "rsi_14": None,
            "macd": None,
            "trend": "unavailable",
            "signal": "No technical signal is available.",
        }

    close = _last_number(df["Close"])
    sma_20 = _last_number(df["SMA_20"])
    sma_50 = _last_number(df["SMA_50"])
    rsi = _last_number(df["RSI_14"])
    macd = _last_number(df["MACD"])
    macd_signal = _last_number(df["MACD_SIGNAL"])

    trend = "sideways"
    if close is not None and sma_20 is not None and sma_50 is not None:
        if close > sma_20 > sma_50:
            trend = "bullish"
        elif close < sma_20 < sma_50:
            trend = "bearish"

    rsi_signal = "neutral"
    if rsi is not None:
        if rsi >= 70:
            rsi_signal = "overbought"
        elif rsi <= 30:
            rsi_signal = "oversold"

    signal = f"{trend.title()} trend with {rsi_signal} RSI conditions."
    if macd is not None and macd_signal is not None:
        signal += " MACD is above signal." if macd >= macd_signal else " MACD is below signal."

    return {
        "close": close,
        "sma_20": sma_20,
        "sma_50": sma_50,
        "rsi_14": rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "trend": trend,
        "signal": signal,
    }

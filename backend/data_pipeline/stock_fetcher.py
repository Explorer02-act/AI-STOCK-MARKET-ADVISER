import yfinance as yf
import pandas as pd
import streamlit as st
from configs.settings import DEFAULT_PERIOD, DEFAULT_INTERVAL

@st.cache_data(ttl=300)
def get_stock_price(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        fast = stock.fast_info
        return {
            "ticker": ticker,
            "name": ticker,
            "current_price": round(fast.last_price, 2),
            "previous_close": round(fast.previous_close, 2),
            "market_cap": fast.market_cap,
            "currency": fast.currency,
            "sector": "N/A",
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "name": ticker,
            "current_price": "N/A",
            "previous_close": "N/A",
            "market_cap": "N/A",
            "currency": "INR",
            "sector": "N/A",
        }

@st.cache_data(ttl=300)
def get_stock_history(ticker: str, period: str = DEFAULT_PERIOD, interval: str = DEFAULT_INTERVAL) -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period, interval=interval)
    except Exception:
        return pd.DataFrame()

def get_multiple_stocks(tickers: list) -> list:
    return [get_stock_price(t) for t in tickers]
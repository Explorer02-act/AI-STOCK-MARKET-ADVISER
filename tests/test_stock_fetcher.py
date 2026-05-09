from types import SimpleNamespace

import pandas as pd

from backend.data_pipeline import stock_fetcher


class FakeCache:
    def __init__(self) -> None:
        self.values = {}

    def get_json(self, key):
        return self.values.get(key)

    def set_json(self, key, value, ttl_seconds=None):
        self.values[key] = value


def test_get_stock_price_fetches_and_caches(monkeypatch):
    fake_cache = FakeCache()
    monkeypatch.setattr(stock_fetcher, "cache", fake_cache)

    class FakeTicker:
        fast_info = SimpleNamespace(
            last_price=123.456,
            previous_close=120.1,
            market_cap=1000000,
            currency="INR",
        )

    monkeypatch.setattr(stock_fetcher.yf, "Ticker", lambda ticker: FakeTicker())

    data = stock_fetcher.get_stock_price("tcs.ns")

    assert data["ticker"] == "TCS.NS"
    assert data["current_price"] == 123.46
    assert fake_cache.values["stock:price:TCS.NS"]["previous_close"] == 120.1


def test_get_stock_price_returns_fallback_on_api_failure(monkeypatch):
    monkeypatch.setattr(stock_fetcher, "cache", FakeCache())

    def raise_error(ticker):
        raise TimeoutError("upstream timeout")

    monkeypatch.setattr(stock_fetcher.yf, "Ticker", raise_error)

    data = stock_fetcher.get_stock_price("INFY.NS")

    assert data["ticker"] == "INFY.NS"
    assert data["current_price"] == "N/A"
    assert "upstream timeout" in data["error"]


def test_get_stock_history_returns_empty_dataframe_on_api_failure(monkeypatch):
    def raise_error(ticker):
        raise ConnectionError("network down")

    monkeypatch.setattr(stock_fetcher.yf, "Ticker", raise_error)

    history = stock_fetcher.get_stock_history("RELIANCE.NS")

    assert isinstance(history, pd.DataFrame)
    assert history.empty

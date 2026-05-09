import pytest

from backend.streaming.market_stream import stock_price_stream


@pytest.mark.asyncio
async def test_stock_price_stream_emits_snapshot(monkeypatch):
    monkeypatch.setattr(
        "backend.streaming.market_stream.get_stock_price",
        lambda ticker: {"ticker": ticker, "current_price": 10.0},
    )

    stream = stock_price_stream(["tcs.ns"], interval_seconds=999)
    payload = await anext(stream)

    assert payload["type"] == "stock_snapshot"
    assert payload["data"] == [{"ticker": "TCS.NS", "current_price": 10.0}]

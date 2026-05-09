from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from backend.data_pipeline.stock_fetcher import get_stock_price
from configs.settings import STREAM_INTERVAL_SECONDS


async def stock_price_stream(
    tickers: list[str],
    interval_seconds: int = STREAM_INTERVAL_SECONDS,
) -> AsyncIterator[dict]:
    normalized = [ticker.strip().upper() for ticker in tickers if ticker.strip()]
    while True:
        yield {
            "type": "stock_snapshot",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": [get_stock_price(ticker) for ticker in normalized],
        }
        await asyncio.sleep(interval_seconds)

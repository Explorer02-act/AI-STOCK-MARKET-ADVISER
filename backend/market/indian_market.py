from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

from configs.settings import POPULAR_INDIAN_STOCKS

INDIA_TZ = ZoneInfo("Asia/Kolkata")
NSE_OPEN = time(9, 15)
NSE_CLOSE = time(15, 30)


def normalize_indian_symbol(symbol: str, default_exchange: str = "NS") -> str:
    value = symbol.strip().upper()
    if not value:
        return value
    if value.endswith((".NS", ".BO")):
        return value
    suffix = ".BO" if default_exchange.upper() == "BO" else ".NS"
    return f"{value}{suffix}"


def is_valid_indian_symbol(symbol: str) -> bool:
    value = symbol.strip().upper()
    if not value.endswith((".NS", ".BO")):
        return False
    base = value.rsplit(".", 1)[0]
    return base.isalnum() and 1 <= len(base) <= 20


def indian_market_status(now: datetime | None = None) -> dict[str, str | bool]:
    current = (now or datetime.now(tz=INDIA_TZ)).astimezone(INDIA_TZ)
    is_weekday = current.weekday() < 5
    is_open = is_weekday and NSE_OPEN <= current.time() <= NSE_CLOSE
    return {
        "is_open": is_open,
        "timezone": "Asia/Kolkata",
        "current_time": current.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "message": "Indian markets are open." if is_open else "Indian markets are closed.",
        "regular_hours": "09:15-15:30 IST, Monday-Friday",
    }


def popular_symbols() -> list[str]:
    return POPULAR_INDIAN_STOCKS.copy()

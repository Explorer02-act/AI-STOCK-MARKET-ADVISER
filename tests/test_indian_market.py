from datetime import datetime
from zoneinfo import ZoneInfo

from backend.market.indian_market import indian_market_status, is_valid_indian_symbol, normalize_indian_symbol


def test_normalize_indian_symbol_defaults_to_nse():
    assert normalize_indian_symbol("reliance") == "RELIANCE.NS"
    assert normalize_indian_symbol("TCS.BO") == "TCS.BO"


def test_valid_indian_symbol_requires_exchange_suffix():
    assert is_valid_indian_symbol("INFY.NS")
    assert is_valid_indian_symbol("SBIN.BO")
    assert not is_valid_indian_symbol("INFY")


def test_market_status_uses_indian_trading_hours():
    open_time = datetime(2026, 6, 8, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    closed_time = datetime(2026, 6, 7, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    assert indian_market_status(open_time)["is_open"] is True
    assert indian_market_status(closed_time)["is_open"] is False

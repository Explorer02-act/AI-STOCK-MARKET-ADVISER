import pandas as pd

from backend.analysis.technical_analysis import add_technical_indicators, summarize_technicals


def test_add_technical_indicators_adds_expected_columns():
    history = pd.DataFrame({"Close": list(range(100, 130))})

    result = add_technical_indicators(history)

    assert {"SMA_20", "SMA_50", "RSI_14", "MACD", "BB_UPPER", "BB_LOWER"}.issubset(result.columns)


def test_summarize_technicals_returns_signal():
    history = pd.DataFrame({"Close": list(range(100, 130))})

    summary = summarize_technicals(history)

    assert summary["sma_20"] is not None
    assert summary["trend"] in {"bullish", "bearish", "sideways"}
    assert "trend" in summary["signal"].lower()

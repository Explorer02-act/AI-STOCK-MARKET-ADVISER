from langchain_core.tools import Tool

from backend.analysis.stock_analysis import analyse_stock, compare_stocks, format_analysis_context
from backend.data_pipeline.stock_fetcher import get_stock_history, get_stock_price


def stock_price_tool_func(ticker: str) -> str:
    try:
        data = get_stock_price(ticker.strip().upper())
        if data.get("error"):
            return f"Unable to fetch fresh data for {ticker}: {data['error']}"
        return (
            f"Company: {data['name']}\n"
            f"Current Price: INR {data['current_price']}\n"
            f"Previous Close: INR {data['previous_close']}\n"
            f"Market Cap: INR {data['market_cap']}\n"
            f"Sector: {data['sector']}\n"
            f"Currency: {data['currency']}"
        )
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"


def stock_history_tool_func(ticker: str) -> str:
    try:
        df = get_stock_history(ticker.strip().upper())
        if df.empty:
            return f"No price history available for {ticker}."
        return df.tail(5).to_string()
    except Exception as e:
        return f"Error fetching history for {ticker}: {str(e)}"


def stock_analysis_tool_func(ticker: str) -> str:
    try:
        return format_analysis_context(analyse_stock(ticker.strip().upper()))
    except Exception as e:
        return f"Error analysing {ticker}: {str(e)}"


def stock_comparison_tool_func(tickers: str) -> str:
    symbols = [ticker.strip().upper() for ticker in tickers.split(",") if ticker.strip()]
    if not symbols:
        return "Please provide comma-separated stock symbols like RELIANCE.NS,TCS.NS."
    rows = compare_stocks(symbols[:6])
    lines = [
        "Ticker | Price | Change % | RSI | Trend | Sentiment",
        "--- | ---: | ---: | ---: | --- | ---",
    ]
    for row in rows:
        lines.append(
            f"{row['ticker']} | {row['price']} | {row['change_pct']} | "
            f"{row['rsi_14']} | {row['trend']} | {row['sentiment']}"
        )
    return "\n".join(lines)


stock_price_tool = Tool(
    name="StockPrice",
    func=stock_price_tool_func,
    description="Use this to get the current stock price of an Indian stock. Input should be the NSE ticker like RELIANCE.NS, TCS.NS, INFY.NS",
)

stock_history_tool = Tool(
    name="StockHistory",
    func=stock_history_tool_func,
    description="Use this to get the last 5 days price history of an Indian stock. Input should be the NSE ticker like RELIANCE.NS",
)

stock_analysis_tool = Tool(
    name="StockAnalysis",
    func=stock_analysis_tool_func,
    description="Use this for multi-dimensional Indian stock analysis with price, technical indicators, and news sentiment.",
)

stock_comparison_tool = Tool(
    name="StockComparison",
    func=stock_comparison_tool_func,
    description="Use this to compare Indian stocks. Input comma-separated symbols like RELIANCE.NS,TCS.NS,INFY.NS.",
)

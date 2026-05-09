from langchain_core.tools import Tool
from backend.data_pipeline.stock_fetcher import get_stock_price, get_stock_history

def stock_price_tool_func(ticker: str) -> str:
    try:
        data = get_stock_price(ticker.strip().upper())
        return (
            f"Company: {data['name']}\n"
            f"Current Price: ₹{data['current_price']}\n"
            f"Previous Close: ₹{data['previous_close']}\n"
            f"Market Cap: ₹{data['market_cap']}\n"
            f"Sector: {data['sector']}\n"
            f"Currency: {data['currency']}"
        )
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"

def stock_history_tool_func(ticker: str) -> str:
    try:
        df = get_stock_history(ticker.strip().upper())
        return df.tail(5).to_string()
    except Exception as e:
        return f"Error fetching history for {ticker}: {str(e)}"

# LangChain tools
stock_price_tool = Tool(
    name="StockPrice",
    func=stock_price_tool_func,
    description="Use this to get the current stock price of an Indian stock. Input should be the NSE ticker like RELIANCE.NS, TCS.NS, INFY.NS"
)

stock_history_tool = Tool(
    name="StockHistory",
    func=stock_history_tool_func,
    description="Use this to get the last 5 days price history of an Indian stock. Input should be the NSE ticker like RELIANCE.NS"
)
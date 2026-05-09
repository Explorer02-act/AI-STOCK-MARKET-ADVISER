from langchain_groq import ChatGroq
from backend.tools.stock_tools import stock_price_tool_func, stock_history_tool_func
from configs.settings import GROQ_API_KEY

llm = ChatGroq(
    temperature=0,
    model="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY
)

def ask_agent(question: str) -> str:
    try:
        # Extract ticker from question
        tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS", "SBIN.NS"]
        found_ticker = None
        for ticker in tickers:
            if ticker.lower().replace(".ns", "") in question.lower():
                found_ticker = ticker
                break

        # Fetch stock data if ticker found
        stock_context = ""
        if found_ticker:
            stock_context = stock_price_tool_func(found_ticker)

        # Send to LLM with context
        prompt = f"""You are a financial assistant for Indian stocks.
Stock data: {stock_context}
User question: {question}
Answer based on the stock data provided."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"
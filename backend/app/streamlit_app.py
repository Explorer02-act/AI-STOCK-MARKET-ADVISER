import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import plotly.graph_objects as go
import streamlit as st

from backend.agents.stock_agent import ask_agent
from backend.data_pipeline.stock_fetcher import get_stock_history, get_stock_price

st.set_page_config(page_title="AI Stock Research Agent", page_icon="IN")
st.title("AI Stock Research Agent")

st.sidebar.header("Quick Lookup")
ticker = st.sidebar.selectbox(
    "Select Stock",
    ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS", "SBIN.NS"],
)

data = get_stock_price(ticker)
st.sidebar.metric("Current Price", f"INR {data['current_price']}")
st.sidebar.metric("Previous Close", f"INR {data['previous_close']}")
st.sidebar.metric("Sector", data["sector"])

st.subheader(f"{data['name']} - Price Chart")
history = get_stock_history(ticker)
if history.empty:
    st.warning("Price history is unavailable right now. Please try again shortly.")
else:
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=history.index,
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
        )
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

st.caption("Realtime stream endpoint: ws://localhost:8000/ws/stocks?tickers=RELIANCE.NS,TCS.NS")

st.subheader("Ask AI Agent")
question = st.text_input("Ask anything about Indian stocks...")
if question:
    with st.spinner("Thinking..."):
        answer = ask_agent(question)
    st.write(answer)

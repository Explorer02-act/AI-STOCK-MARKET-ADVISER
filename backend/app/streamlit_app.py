import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import streamlit as st
import plotly.graph_objects as go
from backend.data_pipeline.stock_fetcher import get_stock_price, get_stock_history
from backend.agents.stock_agent import ask_agent

st.set_page_config(page_title="AI Stock Research Agent", page_icon="🇮🇳")
st.title("🇮🇳 AI Stock Research Agent")

# Sidebar
st.sidebar.header("Quick Lookup")
ticker = st.sidebar.selectbox("Select Stock", [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS", "SBIN.NS"
])

data = get_stock_price(ticker)
st.sidebar.metric("Current Price", f"₹{data['current_price']}")
st.sidebar.metric("Previous Close", f"₹{data['previous_close']}")
st.sidebar.metric("Sector", data['sector'])

# Chart
st.subheader(f"{data['name']} — Price Chart")
history = get_stock_history(ticker)
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=history.index,
    open=history['Open'],
    high=history['High'],
    low=history['Low'],
    close=history['Close']
))
fig.update_layout(xaxis_rangeslider_visible=False)
st.plotly_chart(fig)

# Chat
st.subheader("Ask AI Agent")
question = st.text_input("Ask anything about Indian stocks...")
if question:
    with st.spinner("Thinking..."):
        answer = ask_agent(question)
    st.write(answer)
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.agents.stock_agent import ask_agent
from backend.analysis.portfolio import portfolio_summary
from backend.analysis.stock_analysis import analyse_stock, compare_sector, compare_stocks
from backend.analysis.technical_analysis import add_technical_indicators
from backend.data_pipeline.stock_fetcher import get_stock_history
from backend.market.indian_market import indian_market_status, is_valid_indian_symbol, normalize_indian_symbol
from backend.reports.pdf_report import build_stock_report_pdf
from database.watchlist_store import add_watchlist_item, list_watchlist_items, upsert_position

DEFAULT_SYMBOLS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS", "SBIN.NS"]


def validate_symbol(symbol: str) -> str | None:
    normalized = normalize_indian_symbol(symbol)
    if not is_valid_indian_symbol(normalized):
        st.error("Use an Indian Yahoo Finance symbol like RELIANCE.NS, TCS.NS, INFY.NS, or SBIN.BO.")
        return None
    return normalized


def render_price_chart(ticker: str) -> None:
    history = get_stock_history(ticker, period="6mo")
    if history.empty:
        st.warning("Price history is unavailable right now. If the market is closed, live values may be delayed.")
        return

    history = add_technical_indicators(history)
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=history.index,
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name="Price",
        )
    )
    fig.add_trace(go.Scatter(x=history.index, y=history["SMA_20"], name="SMA 20", line={"width": 1.5}))
    fig.add_trace(go.Scatter(x=history.index, y=history["SMA_50"], name="SMA 50", line={"width": 1.5}))
    fig.update_layout(height=460, margin={"l": 10, "r": 10, "t": 20, "b": 10}, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=history.index, y=history["RSI_14"], name="RSI 14"))
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(height=220, margin={"l": 10, "r": 10, "t": 10, "b": 10})
    st.plotly_chart(rsi_fig, use_container_width=True)


def render_analysis(ticker: str) -> None:
    analysis = analyse_stock(ticker)
    price = analysis["price"]
    technicals = analysis["technicals"]
    fundamentals = analysis["fundamentals"]
    sentiment = analysis["sentiment"]

    cols = st.columns(4)
    cols[0].metric("Current Price", f"INR {price.get('current_price')}")
    cols[1].metric("Previous Close", f"INR {price.get('previous_close')}")
    cols[2].metric("RSI 14", technicals.get("rsi_14") or "N/A")
    cols[3].metric("Sentiment", sentiment.get("sentiment", "neutral").title(), sentiment.get("score"))

    st.subheader(f"{ticker} Technical Chart")
    render_price_chart(ticker)

    left, right = st.columns(2)
    with left:
        st.subheader("Fundamentals")
        st.dataframe(
            pd.DataFrame(
                [
                    {"Metric": "Sector", "Value": fundamentals.get("sector")},
                    {"Metric": "Industry", "Value": fundamentals.get("industry")},
                    {"Metric": "Trailing P/E", "Value": fundamentals.get("trailing_pe")},
                    {"Metric": "Debt to Equity", "Value": fundamentals.get("debt_to_equity")},
                    {"Metric": "Revenue Growth", "Value": fundamentals.get("revenue_growth")},
                    {"Metric": "Profit Margins", "Value": fundamentals.get("profit_margins")},
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )
    with right:
        st.subheader("News Sentiment")
        articles = sentiment.get("articles", [])
        if sentiment.get("error"):
            st.info(sentiment["error"])
        if articles:
            st.dataframe(pd.DataFrame(articles), hide_index=True, use_container_width=True)
        else:
            st.caption("No recent headlines available from the configured news provider.")

    report_lines = [
        f"Ticker: {ticker}",
        f"Current price: INR {price.get('current_price')}",
        f"Previous close: INR {price.get('previous_close')}",
        f"Sector: {fundamentals.get('sector')}",
        f"Industry: {fundamentals.get('industry')}",
        f"P/E: {fundamentals.get('trailing_pe')}",
        f"Debt to equity: {fundamentals.get('debt_to_equity')}",
        f"RSI 14: {technicals.get('rsi_14')}",
        f"Trend: {technicals.get('trend')}",
        f"Technical signal: {technicals.get('signal')}",
        f"News sentiment: {sentiment.get('sentiment')} ({sentiment.get('score')})",
        "This report is educational and is not personalized investment advice.",
    ]
    st.download_button(
        "Download PDF Report",
        data=build_stock_report_pdf(f"{ticker} Stock Analysis Report", report_lines),
        file_name=f"{ticker.replace('.', '_')}_analysis.pdf",
        mime="application/pdf",
    )


st.set_page_config(page_title="Indian Stock Analysis Assistant", page_icon="IN", layout="wide")
st.title("Indian Stock Analysis Assistant")

status = indian_market_status()
st.caption(f"{status['message']} Regular hours: {status['regular_hours']}. Current time: {status['current_time']}.")

with st.sidebar:
    st.header("Stock Controls")
    selected = st.selectbox("Popular stocks", DEFAULT_SYMBOLS)
    typed_symbol = st.text_input("Or enter symbol", value=selected)
    ticker = validate_symbol(typed_symbol) or selected
    if st.button("Save to Watchlist"):
        saved = add_watchlist_item(ticker)
        st.success(f"Saved {saved}")

tabs = st.tabs(["Analysis", "Compare", "Watchlist", "Portfolio", "Ask Agent"])

with tabs[0]:
    render_analysis(ticker)

with tabs[1]:
    comparison_input = st.text_input("Compare symbols", value="RELIANCE.NS,TCS.NS,INFY.NS")
    symbols = [validate_symbol(symbol) for symbol in comparison_input.split(",") if symbol.strip()]
    symbols = [symbol for symbol in symbols if symbol]
    if symbols:
        comparison = pd.DataFrame(compare_stocks(symbols))
        st.subheader("Stock Comparison")
        st.dataframe(comparison, hide_index=True, use_container_width=True)

        st.subheader("Sector and Fundamentals Comparison")
        st.dataframe(pd.DataFrame(compare_sector(symbols)), hide_index=True, use_container_width=True)

with tabs[2]:
    st.subheader("Saved Watchlist")
    items = list_watchlist_items()
    if items:
        st.dataframe(pd.DataFrame(items), hide_index=True, use_container_width=True)
    else:
        st.info("Your watchlist is empty. Save a stock from the sidebar to begin.")

with tabs[3]:
    st.subheader("Portfolio Tracker")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        portfolio_symbol = st.text_input("Portfolio symbol", value=ticker)
    with col_b:
        quantity = st.number_input("Quantity", min_value=0.0, value=1.0, step=1.0)
    with col_c:
        average_price = st.number_input("Average price", min_value=0.0, value=100.0, step=10.0)
    if st.button("Add Position"):
        normalized = validate_symbol(portfolio_symbol)
        if normalized:
            upsert_position(normalized, quantity, average_price)
            st.success(f"Added {normalized}")

    summary = portfolio_summary()
    cards = st.columns(4)
    cards[0].metric("Invested", f"INR {summary['invested']}")
    cards[1].metric("Current Value", f"INR {summary['current_value']}")
    cards[2].metric("P&L", f"INR {summary['pnl']}")
    cards[3].metric("P&L %", f"{summary['pnl_pct']}%")
    if summary["positions"]:
        st.dataframe(pd.DataFrame(summary["positions"]), hide_index=True, use_container_width=True)

with tabs[4]:
    st.subheader("Ask the Research Agent")
    question = st.text_input("Ask about Indian stocks, comparisons, fundamentals, sentiment, or technicals")
    if question:
        with st.spinner("Researching..."):
            st.write(ask_agent(question))

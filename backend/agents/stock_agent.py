from typing import TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

from backend.analysis.stock_analysis import analyse_stock, compare_stocks, format_analysis_context
from backend.monitoring import UsageEvent, usage_monitor
from configs.settings import (
    GROQ_API_KEY,
    GROQ_INPUT_COST_PER_1K,
    GROQ_OUTPUT_COST_PER_1K,
    POPULAR_INDIAN_STOCKS,
)


class AgentState(TypedDict):
    question: str
    ticker: str | None
    tickers: list[str]
    stock_context: str
    comparison_context: str
    answer: str


def _get_llm() -> ChatGroq:
    return ChatGroq(
        temperature=0,
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY,
    )


def _estimate_cost(prompt: str, answer: str) -> float:
    input_tokens = max(1, len(prompt.split()))
    output_tokens = max(1, len(answer.split()))
    return (input_tokens / 1000 * GROQ_INPUT_COST_PER_1K) + (
        output_tokens / 1000 * GROQ_OUTPUT_COST_PER_1K
    )


def _detect_ticker(state: AgentState) -> AgentState:
    question = state["question"].lower()
    found_ticker = None
    found_tickers = []
    for ticker in POPULAR_INDIAN_STOCKS:
        symbol = ticker.lower().replace(".ns", "")
        if ticker.lower() in question or symbol in question:
            found_tickers.append(ticker)
            found_ticker = ticker
    return {**state, "ticker": found_ticker, "tickers": found_tickers}


def _load_stock_context(state: AgentState) -> AgentState:
    ticker = state.get("ticker")
    stock_context = format_analysis_context(analyse_stock(ticker)) if ticker else ""
    return {**state, "stock_context": stock_context}


def _load_comparison_context(state: AgentState) -> AgentState:
    tickers = state.get("tickers", [])
    if len(tickers) < 2:
        return {**state, "comparison_context": ""}
    rows = compare_stocks(tickers)
    comparison = "\n".join(
        f"{row['ticker']}: price={row['price']}, change_pct={row['change_pct']}, "
        f"rsi={row['rsi_14']}, trend={row['trend']}, sentiment={row['sentiment']}"
        for row in rows
    )
    return {**state, "comparison_context": comparison}


def _answer_question(state: AgentState) -> AgentState:
    if not GROQ_API_KEY:
        return {
            **state,
            "answer": "GROQ_API_KEY is not configured, so the AI agent cannot answer yet.",
        }

    prompt = f"""You are a financial assistant for Indian stocks.
Stock data: {state['stock_context']}
Comparison data: {state['comparison_context']}
User question: {state['question']}
Answer based on the stock, technical, and sentiment data provided.
Mention uncertainty when data is unavailable. Do not provide personalized investment advice."""
    response = _get_llm().invoke(prompt)
    answer = response.content
    usage_monitor.record(
        UsageEvent(
            provider="groq",
            endpoint="chat_completion",
            status="success",
            estimated_cost_usd=_estimate_cost(prompt, answer),
        )
    )
    return {**state, "answer": answer}


agent_graph = StateGraph(AgentState)
agent_graph.add_node("detect_ticker", _detect_ticker)
agent_graph.add_node("load_stock_context", _load_stock_context)
agent_graph.add_node("load_comparison_context", _load_comparison_context)
agent_graph.add_node("answer_question", _answer_question)
agent_graph.add_edge(START, "detect_ticker")
agent_graph.add_edge("detect_ticker", "load_stock_context")
agent_graph.add_edge("load_stock_context", "load_comparison_context")
agent_graph.add_edge("load_comparison_context", "answer_question")
agent_graph.add_edge("answer_question", END)
compiled_agent_graph = agent_graph.compile()


def ask_agent(question: str) -> str:
    try:
        state = compiled_agent_graph.invoke(
            {
                "question": question,
                "ticker": None,
                "tickers": [],
                "stock_context": "",
                "comparison_context": "",
                "answer": "",
            }
        )
        return state["answer"]
    except Exception as e:
        usage_monitor.record_failure("groq", "chat_completion", e)
        return f"Error: {str(e)}"

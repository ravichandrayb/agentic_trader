from langgraph.graph import StateGraph
from agents.data_fetch_agent import fetch_data_node
from agents.strategy_generation_agent import generate_strategies_node
from agents.backtest_agent import backtest_node
from agents.evaluation_agent import evaluate_node
from agents.report_agent import report_node

builder = StateGraph()
builder.add_node("fetch_data", fetch_data_node)
builder.add_node("generate_strategies", generate_strategies_node)
builder.add_node("backtest", backtest_node)
builder.add_node("evaluate", evaluate_node)
builder.add_node("report", report_node)

builder.set_entry_point("fetch_data")
builder.add_edge("fetch_data", "generate_strategies")
builder.add_edge("generate_strategies", "backtest")
builder.add_edge("backtest", "evaluate")
builder.add_edge("evaluate", "report")

graph = builder.compile()

from agentic_trader.langgraph_flow import graph

def run(stock_symbol: str):
    result = graph.invoke({"stock": stock_symbol})
    print("Completed:", result)

if __name__ == "__main__":
    run("INFY")

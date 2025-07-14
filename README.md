# 📊 Stock Trading Strategy using AI agents with LangGraph

An AI-powered, agentic framework to generate, backtest, evaluate, and report trading strategies for Indian stock market equities using Zerodha Kite, LangGraph, and vectorbt.

---

## ✨ Features

- 🧠 **LLM-Powered Strategy Generation** via OpenAI GPT-4
- 🔄 **LangGraph Agent Flow** for modular and explainable logic
- 📉 **Backtesting with vectorbt** for lightning-fast strategy evaluation
- 📁 **Local Data Caching** using `.parquet` to avoid redundant API calls
- 📊 **Evaluation & Ranking** based on Sharpe, drawdown, returns
- 📄 **JSON Reports** for each stock and strategy combination
- 🚀 **FastAPI Interface** to trigger the full analysis via API
- 🐳 **Docker Support** for containerized deployment
- ⚙️ **GitHub Actions CI** for continuous testing

---

```markdown
## 🧱 Architecture

```mermaid
graph TD
    A[User/CLI/API] --> B[LangGraph Flow]
    B --> C[Data Fetch Agent]
    C --> D[Local Cache or Kite API]
    B --> E[LLM Strategy Generator]
    B --> F[Backtest Agent (vectorbt)]
    B --> G[Evaluation Agent]
    B --> H[Report Generator]

## 🛠️ Stack

| Layer         | Tool                           |
| ------------- | ------------------------------ |
| Orchestration | `LangGraph`, `LangChain`       |
| LLM           | `OpenAI GPT-4`                 |
| Data Fetch    | `kiteconnect`                  |
| TA Library    | `pandas_ta`                    |
| Backtesting   | `vectorbt`                     |
| Storage       | `Parquet`, `DuckDB` (optional) |
| Web API       | `FastAPI`                      |
| Infra         | `Docker`, `GitHub Actions`     |

## 🚀 Quickstart

1. Clone & Install
git clone https://github.com/yourusername/stock-strategy-langgraph.git
cd stock-strategy-langgraph

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Configure .env
KITE_API_KEY=your_key
KITE_API_SECRET=your_secret
KITE_ACCESS_TOKEN=your_token
OPEN_AI_SECRET=your_secret

3. Run CLI Pipeline
python main.py

4. Run FastAPI Server
uvicorn app.main:app --reload
Access API at http://localhost:8000/docs

5. Docker (Optional)
docker-compose up --build

## 📂 Project Structure
.
├── agents/                  # LangGraph nodes
├── strategies/              # Strategy templates & registry
├── data/                    # Cached Parquet files
├── reports/                 # Strategy evaluation reports
├── utils/                   # Data, indicator, scoring utilities
├── config/                  # Kite API secrets
├── app/                     # FastAPI web server
├── langgraph_flow.py        # LangGraph pipeline
├── main.py                  # CLI entry point
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml # GitHub Actions

📊 Sample JSON Output

{
  "stock": "INFY",
  "top_3": ["MACD + RSI Confirmation", "EMA Crossover", "ATR Breakout"],
  "scored": {
    "EMA Crossover": {
      "return": 0.26,
      "sharpe": 1.4,
      "drawdown": 0.12
    }
  }
}


📌 Future Roadmap
 Web dashboard for live report browsing

 Strategy leaderboard by performance

 Integration with Telegram/WhatsApp for alerts

 Auto-token generator for Zerodha

 Strategy editing and testing via UI

🤝 Contributing
PRs, ideas, and issue reports are very welcome!
Check strategy_registry.py to add your own favorite TA patterns.

📜 License
MIT License. Built with ❤️ for quants and traders in India 🇮🇳










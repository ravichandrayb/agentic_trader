from utils.indicators import parse_strategies
from vectorbt import Portfolio
import pandas as pd
import numpy as np
from datetime import datetime

def backtest_node(state):
    """
    Backtest trading strategies and return comprehensive performance metrics.
    
    Args:
        state: Dictionary containing data, strategies, and stock symbol
        
    Returns:
        Dictionary with backtesting results for each strategy
    """
    df = state["data"]
    strategies = parse_strategies(state["strategies"])
    results = {}
    
    # Set benchmark as buy and hold
    benchmark_pf = Portfolio.from_holding(df['close'], freq='1D')
    benchmark_metrics = calculate_metrics(benchmark_pf, "Buy & Hold")
    
    # Run backtests for each strategy
    for strat in strategies:
        try:
            # Create portfolio from entry/exit signals
            pf = Portfolio.from_signals(
                df['close'], 
                entries=strat['entries'], 
                exits=strat['exits'],
                freq='1D',
                init_cash=100000,  # Starting with $100k
                fees=0.001,        # 0.1% trading fee
                slippage=0.001     # 0.1% slippage
            )
            
            # Calculate comprehensive metrics
            strategy_metrics = calculate_metrics(pf, strat["name"])
            
            # Add comparison to benchmark
            strategy_metrics["vs_benchmark"] = {
                "excess_return": strategy_metrics["total_return"] - benchmark_metrics["total_return"],
                "alpha": strategy_metrics["cagr"] - benchmark_metrics["cagr"],
                "beta": calculate_beta(pf.returns(), benchmark_pf.returns()),
                "information_ratio": calculate_information_ratio(pf.returns(), benchmark_pf.returns())
            }
            
            results[strat["name"]] = strategy_metrics
            
        except Exception as e:
            results[strat["name"]] = {"error": str(e)}
    
    # Add benchmark results
    results["benchmark"] = benchmark_metrics
    
    return {
        "stock": state["stock"], 
        "period": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
        "results": results
    }

def calculate_metrics(portfolio, strategy_name):
    """Calculate comprehensive performance metrics for a portfolio."""
    
    # Get daily returns and drawdowns
    returns = portfolio.returns()
    drawdowns = portfolio.drawdown()
    
    # Basic performance metrics
    metrics = {
        "strategy": strategy_name,
        "total_return": portfolio.total_return(),
        "cagr": portfolio.annualized_return(),
        "sharpe_ratio": portfolio.sharpe_ratio(),
        "sortino_ratio": portfolio.sortino_ratio(),
        "calmar_ratio": portfolio.calmar_ratio(),
        "max_drawdown": portfolio.max_drawdown(),
        "avg_drawdown": drawdowns.mean(),
        "volatility": portfolio.annualized_volatility(),
        "win_rate": portfolio.win_rate(),
        "profit_factor": portfolio.profit_factor(),
        
        # Trade statistics
        "trades": {
            "total_trades": len(portfolio.trades()),
            "win_count": portfolio.trades().win_count(),
            "loss_count": portfolio.trades().loss_count(),
            "avg_win": portfolio.trades().winning.pnl.mean() if portfolio.trades().winning.shape[0] > 0 else 0,
            "avg_loss": portfolio.trades().losing.pnl.mean() if portfolio.trades().losing.shape[0] > 0 else 0,
            "avg_duration": portfolio.trades().duration.mean(),
            "max_trade_profit": portfolio.trades().pnl.max() if len(portfolio.trades()) > 0 else 0,
            "max_trade_loss": portfolio.trades().pnl.min() if len(portfolio.trades()) > 0 else 0,
        },
        
        # Drawdown statistics
        "drawdowns": {
            "max_drawdown": portfolio.max_drawdown(),
            "max_drawdown_duration": portfolio.max_dd_duration(),
            "avg_drawdown_duration": portfolio.drawdowns().duration.mean() if len(portfolio.drawdowns()) > 0 else 0,
            "recovery_factor": portfolio.recovery_factor(),
            "ulcer_index": calculate_ulcer_index(drawdowns),
        },
        
        # Return statistics
        "return_stats": {
            "best_day": returns.max(),
            "worst_day": returns.min(),
            "avg_up_day": returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0,
            "avg_down_day": returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0,
            "up_days": len(returns[returns > 0]),
            "down_days": len(returns[returns < 0]),
            "up_day_ratio": len(returns[returns > 0]) / len(returns) if len(returns) > 0 else 0,
        },
        
        # Risk metrics
        "risk_metrics": {
            "var_95": calculate_var(returns, 0.95),
            "cvar_95": calculate_cvar(returns, 0.95),
            "omega_ratio": calculate_omega_ratio(returns),
            "tail_ratio": calculate_tail_ratio(returns),
            "skew": returns.skew(),
            "kurtosis": returns.kurtosis(),
        },
        
        # Performance periods
        "period_returns": {
            "mtd": calculate_period_return(portfolio, "MTD"),
            "qtd": calculate_period_return(portfolio, "QTD"),
            "ytd": calculate_period_return(portfolio, "YTD"),
            "1m": calculate_period_return(portfolio, "1M"),
            "3m": calculate_period_return(portfolio, "3M"),
            "6m": calculate_period_return(portfolio, "6M"),
            "1y": calculate_period_return(portfolio, "1Y"),
        }
    }
    
    return metrics

def calculate_var(returns, confidence_level):
    """Calculate Value at Risk."""
    if len(returns) == 0:
        return 0
    return abs(np.percentile(returns, 100 * (1 - confidence_level)))

def calculate_cvar(returns, confidence_level):
    """Calculate Conditional Value at Risk (Expected Shortfall)."""
    if len(returns) == 0:
        return 0
    var = calculate_var(returns, confidence_level)
    return abs(returns[returns <= -var].mean()) if len(returns[returns <= -var]) > 0 else var

def calculate_ulcer_index(drawdowns):
    """Calculate Ulcer Index (root-mean-square of drawdowns)."""
    if len(drawdowns) == 0:
        return 0
    squared_dd = np.square(drawdowns)
    return np.sqrt(squared_dd.mean())

def calculate_omega_ratio(returns, threshold=0):
    """Calculate Omega ratio."""
    if len(returns) == 0:
        return 0
    returns_above = returns[returns > threshold]
    returns_below = returns[returns <= threshold]
    
    if len(returns_below) == 0 or abs(sum(returns_below)) < 1e-10:
        return float('inf') if len(returns_above) > 0 else 0
        
    return sum(returns_above) / abs(sum(returns_below))

def calculate_tail_ratio(returns):
    """Calculate tail ratio (ratio of 95th to 5th percentile)."""
    if len(returns) == 0:
        return 0
    return abs(np.percentile(returns, 95) / np.percentile(returns, 5)) if np.percentile(returns, 5) != 0 else 0

def calculate_beta(strategy_returns, benchmark_returns):
    """Calculate beta (systematic risk)."""
    if len(strategy_returns) != len(benchmark_returns):
        return 0
    if benchmark_returns.std() == 0:
        return 0
    return np.cov(strategy_returns, benchmark_returns)[0, 1] / benchmark_returns.var()

def calculate_information_ratio(strategy_returns, benchmark_returns):
    """Calculate information ratio."""
    if len(strategy_returns) != len(benchmark_returns):
        return 0
    excess_returns = strategy_returns - benchmark_returns
    if excess_returns.std() == 0:
        return 0
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)  # Annualized

def calculate_period_return(portfolio, period):
    """Calculate return for specific periods."""
    today = datetime.now()
    
    if period == "MTD":
        start_date = datetime(today.year, today.month, 1)
    elif period == "QTD":
        quarter = (today.month - 1) // 3
        start_date = datetime(today.year, 3*quarter + 1, 1)
    elif period == "YTD":
        start_date = datetime(today.year, 1, 1)
    elif period == "1M":
        start_date = datetime(today.year, today.month - 1, today.day) if today.month > 1 else datetime(today.year - 1, 12, today.day)
    elif period == "3M":
        start_date = datetime(today.year, today.month - 3, today.day) if today.month > 3 else datetime(today.year - 1, 12 + (today.month - 3), today.day)
    elif period == "6M":
        start_date = datetime(today.year, today.month - 6, today.day) if today.month > 6 else datetime(today.year - 1, 12 + (today.month - 6), today.day)
    elif period == "1Y":
        start_date = datetime(today.year - 1, today.month, today.day)
    else:
        return 0
    
    # Get portfolio value at the start date or closest available date
    try:
        return portfolio.slice(start_date=start_date).total_return()
    except:
        return 0  # Return 0 if data not available for the period

if __name__ == "__main__":
    # Example usage for testing
    import pandas as pd
    import numpy as np
    
    # Create sample data with OHLCV format
    dates = pd.date_range('2025-01-01', '2025-06-30')
    data = {
        'open': np.random.normal(100, 5, len(dates)),
        'high': np.random.normal(105, 5, len(dates)),
        'low': np.random.normal(95, 5, len(dates)),
        'close': np.random.normal(100, 5, len(dates)),
        'volume': np.random.normal(1000000, 200000, len(dates))
    }
    df = pd.DataFrame(data, index=dates)
    
    # Create simple moving average crossover strategy
    df['sma20'] = df['close'].rolling(20).mean()
    df['sma50'] = df['close'].rolling(50).mean()
    
    # Create entry/exit signals
    entries = (df['sma20'] > df['sma50']) & (df['sma20'].shift(1) <= df['sma50'].shift(1))
    exits = (df['sma20'] < df['sma50']) & (df['sma20'].shift(1) >= df['sma50'].shift(1))
    
    # Run backtest
    state = {
        "data": df,
        "stock": "EXAMPLE",
        "strategies": [{"name": "SMA Crossover", "entries": entries, "exits": exits}]
    }
    
    results = backtest_node(state)
    print(f"Backtesting results for {results['stock']}:")
    for strategy, metrics in results["results"].items():
        print(f"\n{strategy}:")
        print(f"Total Return: {metrics.get('total_return', 0):.2%}")
        print(f"CAGR: {metrics.get('cagr', 0):.2%}")
        print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2%}")
        print(f"Win Rate: {metrics.get('win_rate', 0):.2%}")

strategy_examples = [
    {
        "name": "EMA Crossover",
        "description": "Buy when 10 EMA crosses above 30 EMA, sell when it crosses below.",
        "entry_rule": "ema_fast > ema_slow and ema_fast_prev <= ema_slow_prev",
        "exit_rule": "ema_fast < ema_slow and ema_fast_prev >= ema_slow_prev",
        "indicators": ["ema"],
        "category": "trend-following"
    },
    {
        "name": "MACD + RSI Confirmation",
        "description": "Buy when MACD crosses above signal and RSI < 30. Exit when MACD crosses below signal or RSI > 70.",
        "entry_rule": "macd_cross_up and rsi < 30",
        "exit_rule": "macd_cross_down or rsi > 70",
        "indicators": ["macd", "rsi"],
        "category": "trend-following"
    },
    {
        "name": "Bollinger Band Reversal",
        "description": "Buy when price closes below lower Bollinger Band and RSI < 30. Sell when price closes above upper band or RSI > 70.",
        "entry_rule": "close < bb_lower and rsi < 30",
        "exit_rule": "close > bb_upper or rsi > 70",
        "indicators": ["bollinger", "rsi"],
        "category": "mean-reversion"
    },
    {
        "name": "ATR Breakout",
        "description": "Enter long when price breaks above high + 1.5 * ATR. Exit when price drops below low - ATR.",
        "entry_rule": "close > high.shift(1) + 1.5 * atr",
        "exit_rule": "close < low.shift(1) - atr",
        "indicators": ["atr"],
        "category": "high-volatility"
    }
]

def get_example_strategies():
    return strategy_examples

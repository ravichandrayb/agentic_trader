import json
import os
import pandas as pd
from datetime import datetime
from utils.scoring import StockScoring
import matplotlib.pyplot as plt
import seaborn as sns

def report_node(state):
    """
    Generate comprehensive reports for stock analysis.
    
    Args:
        state: Dictionary containing stock data, analysis results, and backtest results
        
    Returns:
        Original state with added report_path
    """
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{state['stock']}_{timestamp}"
    
    # Extract relevant data
    stock_symbol = state.get('stock', 'UNKNOWN')
    df = state.get('data', pd.DataFrame())
    backtest_results = state.get('backtest_results', {})
    
    # Generate comprehensive report if we have price data
    if not df.empty:
        # Generate detailed stock analysis report using scoring.py
        analysis_report = StockScoring.generate_report(df, stock_symbol)
        
        # Add the analysis report to the state
        state['analysis_report'] = analysis_report
        
        # Generate visualizations
        chart_paths = generate_charts(df, stock_symbol, reports_dir, report_filename)
        state['chart_paths'] = chart_paths
    
    # Save complete state as JSON
    json_path = os.path.join(reports_dir, f"{report_filename}.json")
    with open(json_path, "w") as f:
        # Convert any non-serializable objects
        serializable_state = make_json_serializable(state)
        json.dump(serializable_state, f, indent=2)
    
    # Generate HTML report
    html_path = generate_html_report(state, reports_dir, report_filename)
    
    # Add report paths to state
    state['report_paths'] = {
        'json': json_path,
        'html': html_path,
        'charts': chart_paths if 'chart_paths' in state else []
    }
    
    print(f"Report generated for {stock_symbol}: {json_path}")
    return state

def make_json_serializable(obj):
    """Convert non-serializable objects to serializable types."""
    if isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, (float, int)) and (pd.isna(obj) or pd.isinf(obj)):
        return None
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def generate_charts(df, symbol, reports_dir, report_filename):
    """Generate and save visualizations for the report."""
    # Create charts directory
    charts_dir = os.path.join(reports_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    chart_paths = {}
    
    # Set style
    plt.style.use('ggplot')
    
    # 1. Price chart with key indicators
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        # Plot price
        ax.plot(df.index, df['close'], label='Close Price', linewidth=2)
        
        # Plot moving averages if available
        if 'sma20' in df.columns:
            ax.plot(df.index, df['sma20'], label='SMA 20', linestyle='--')
        if 'sma50' in df.columns:
            ax.plot(df.index, df['sma50'], label='SMA 50', linestyle='--')
        if 'sma200' in df.columns:
            ax.plot(df.index, df['sma200'], label='SMA 200', linestyle='--')
        
        ax.set_title(f"{symbol} - Price Chart with Indicators")
        ax.set_ylabel('Price')
        ax.legend()
        plt.tight_layout()
        
        # Save the chart
        price_chart_path = os.path.join(charts_dir, f"{report_filename}_price.png")
        plt.savefig(price_chart_path)
        plt.close()
        chart_paths['price'] = price_chart_path
    except Exception as e:
        print(f"Error generating price chart: {e}")
    
    # 2. Technical indicators chart
    try:
        fig, axs = plt.subplots(3, 1, figsize=(12, 12), gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # Price and Bollinger Bands
        axs[0].plot(df.index, df['close'], label='Close Price')
        if all(col in df.columns for col in ['BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']):
            axs[0].plot(df.index, df['BBL_20_2.0'], label='Lower BB', linestyle='--')
            axs[0].plot(df.index, df['BBM_20_2.0'], label='Middle BB', linestyle='--')
            axs[0].plot(df.index, df['BBU_20_2.0'], label='Upper BB', linestyle='--')
        axs[0].set_title(f"{symbol} - Price and Bollinger Bands")
        axs[0].set_ylabel('Price')
        axs[0].legend()
        
        # RSI
        if 'rsi14' in df.columns:
            axs[1].plot(df.index, df['rsi14'], label='RSI (14)', color='purple')
            axs[1].axhline(y=70, color='r', linestyle='-', alpha=0.3)
            axs[1].axhline(y=30, color='g', linestyle='-', alpha=0.3)
            axs[1].set_ylabel('RSI')
            axs[1].set_ylim([0, 100])
            axs[1].legend()
        
        # Volume
        axs[2].bar(df.index, df['volume'], label='Volume')
        if 'volume_sma20' in df.columns:
            axs[2].plot(df.index, df['volume_sma20'], color='r', label='Volume SMA (20)')
        axs[2].set_ylabel('Volume')
        axs[2].legend()
        
        plt.tight_layout()
        
        # Save the chart
        indicators_chart_path = os.path.join(charts_dir, f"{report_filename}_indicators.png")
        plt.savefig(indicators_chart_path)
        plt.close()
        chart_paths['indicators'] = indicators_chart_path
    except Exception as e:
        print(f"Error generating indicators chart: {e}")
    
    # 3. Performance chart if backtest data is available
    # (This would be implemented if backtest results include performance data)
    
    return chart_paths

def generate_html_report(state, reports_dir, report_filename):
    """Generate an HTML report with all analysis and charts."""
    stock_symbol = state.get('stock', 'UNKNOWN')
    analysis_report = state.get('analysis_report', {})
    backtest_results = state.get('backtest_results', {})
    chart_paths = state.get('chart_paths', {})
    
    # Start building the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stock Analysis Report - {stock_symbol}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .section {{ margin-bottom: 30px; padding: 20px; background-color: #f9f9f9; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #fff; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .metric-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
            .metric-label {{ font-size: 14px; color: #7f8c8d; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #2c3e50; color: white; }}
            tr:hover {{background-color: #f5f5f5;}}
            .chart-container {{ margin: 20px 0; }}
            .score-high {{ color: green; }}
            .score-medium {{ color: orange; }}
            .score-low {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Stock Analysis Report - {stock_symbol}</h1>
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    # Add stock summary section
    if analysis_report:
        score = analysis_report.get('score', 0)
        score_class = 'score-high' if score >= 70 else ('score-medium' if score >= 40 else 'score-low')
        signal = analysis_report.get('signal', 'neutral')
        
        html_content += f"""
            <div class="section">
                <h2>Stock Summary</h2>
                <div class="metric">
                    <div class="metric-label">Overall Score</div>
                    <div class="metric-value {score_class}">{score:.1f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Signal</div>
                    <div class="metric-value">{signal.upper()}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">₹{analysis_report.get('price', {}).get('close', 0):.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Daily Change</div>
                    <div class="metric-value">{analysis_report.get('price', {}).get('daily_change', 0):.2f}%</div>
                </div>
            </div>
        """
    
    # Add chart images
    if chart_paths:
        html_content += """
            <div class="section">
                <h2>Charts</h2>
                <div class="chart-container">
        """
        
        for chart_type, chart_path in chart_paths.items():
            relative_path = os.path.relpath(chart_path, reports_dir)
            chart_filename = os.path.basename(chart_path)
            # In a real web environment, you'd need to adjust these paths
            html_content += f"""
                    <h3>{chart_type.capitalize()} Chart</h3>
                    <img src="charts/{chart_filename}" alt="{chart_type} chart" style="width:100%; max-width:1000px;">
            """
        
        html_content += """
                </div>
            </div>
        """
    
    # Add detailed analysis
    if analysis_report:
        html_content += """
            <div class="section">
                <h2>Technical Analysis</h2>
        """
        
        # Key indicators
        if 'indicators' in analysis_report:
            indicators = analysis_report['indicators']
            html_content += """
                <h3>Key Indicators</h3>
                <table>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                    </tr>
            """
            
            for indicator, value in indicators.items():
                if value is not None:
                    html_content += f"""
                    <tr>
                        <td>{indicator.upper()}</td>
                        <td>{value:.2f}</td>
                    </tr>
                    """
            
            html_content += """
                </table>
            """
        
        # Component scores
        if 'component_scores' in analysis_report:
            html_content += """
                <h3>Component Scores</h3>
                <table>
                    <tr>
                        <th>Component</th>
                        <th>Score</th>
                    </tr>
            """
            
            for component, score in analysis_report['component_scores'].items():
                html_content += f"""
                <tr>
                    <td>{component.capitalize()}</td>
                    <td>{score:.2f}</td>
                </tr>
                """
            
            html_content += """
                </table>
            """
        
        # Support and resistance levels
        if 'key_levels' in analysis_report:
            html_content += """
                <h3>Key Price Levels</h3>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Levels</th>
                    </tr>
            """
            
            for level_type, levels in analysis_report['key_levels'].items():
                html_content += f"""
                <tr>
                    <td>{level_type.capitalize()}</td>
                    <td>{', '.join([str(round(level, 2)) for level in levels])}</td>
                </tr>
                """
            
            html_content += """
                </table>
            """
        
        html_content += """
            </div>
        """
    
    # Add backtest results
    if backtest_results:
        html_content += """
            <div class="section">
                <h2>Backtesting Results</h2>
                <table>
                    <tr>
                        <th>Strategy</th>
                        <th>Total Return</th>
                        <th>CAGR</th>
                        <th>Sharpe Ratio</th>
                        <th>Max Drawdown</th>
                        <th>Win Rate</th>
                    </tr>
        """
        
        results = backtest_results.get('results', {})
        for strategy_name, metrics in results.items():
            if isinstance(metrics, dict) and 'error' not in metrics:
                html_content += f"""
                <tr>
                    <td>{strategy_name}</td>
                    <td>{metrics.get('total_return', 0):.2%}</td>
                    <td>{metrics.get('cagr', 0):.2%}</td>
                    <td>{metrics.get('sharpe_ratio', 0):.2f}</td>
                    <td>{metrics.get('max_drawdown', 0):.2%}</td>
                    <td>{metrics.get('win_rate', 0):.2%}</td>
                </tr>
                """
        
        html_content += """
                </table>
            </div>
        """
    
    # Close the HTML
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Write the HTML to a file
    html_path = os.path.join(reports_dir, f"{report_filename}.html")
    with open(html_path, "w") as f:
        f.write(html_content)
    
    return html_path

if __name__ == "__main__":
    # Example usage for testing
    import pandas as pd
    import numpy as np
    from utils.indicators import TechnicalIndicators
    
    # Create sample data
    dates = pd.date_range('2025-01-01', '2025-06-30')
    data = {
        'open': np.random.normal(100, 5, len(dates)),
        'high': np.random.normal(105, 5, len(dates)),
        'low': np.random.normal(95, 5, len(dates)),
        'close': np.random.normal(100, 5, len(dates)),
        'volume': np.random.normal(1000000, 200000, len(dates))
    }
    df = pd.DataFrame(data, index=dates)
    
    # Add technical indicators
    df = TechnicalIndicators.calculate_all_indicators(df)
    
    # Create test state
    state = {
        "stock": "TESTSTOCK",
        "data": df,
        "backtest_results": {
            "results": {
                "Strategy 1": {
                    "total_return": 0.35,
                    "cagr": 0.15,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": -0.12,
                    "win_rate": 0.65
                },
                "Buy & Hold": {
                    "total_return": 0.25,
                    "cagr": 0.12,
                    "sharpe_ratio": 0.9,
                    "max_drawdown": -0.18,
                    "win_rate": 0.58
                }
            }
        }
    }
    
    # Generate report
    result = report_node(state)
    print(f"Report generated: {result['report_paths']['html']}")

# Stock scoring and signal generation utilities

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.indicators import TechnicalIndicators

class StockScoring:
    def __init__(self):
        pass
    
    @staticmethod
    def momentum_score(df, periods=(5, 10, 20, 60)):
        """
        Calculate momentum score based on price changes over multiple periods.
        
        Args:
            df: DataFrame with price data
            periods: Periods to calculate momentum for (in days)
            
        Returns:
            Dictionary with momentum scores
        """
        momentum_scores = {}
        for period in periods:
            if len(df) > period:
                # Calculate percentage change over the period
                pct_change = (df['close'].iloc[-1] / df['close'].iloc[-period-1] - 1) * 100
                momentum_scores[f'momentum_{period}d'] = pct_change
        
        # Calculate overall momentum score (average of all periods)
        if momentum_scores:
            momentum_scores['momentum_overall'] = sum(momentum_scores.values()) / len(momentum_scores)
            
        return momentum_scores
    
    @staticmethod
    def trend_score(df):
        """
        Calculate trend score based on moving averages and ADX.
        
        Args:
            df: DataFrame with indicator data
            
        Returns:
            Dictionary with trend scores
        """
        if len(df) < 50:
            return {'trend_score': 0}
        
        latest = df.iloc[-1]
        
        # Score based on SMA alignments (50, 100, 200)
        sma_alignment = 0
        
        if 'sma20' in df.columns and 'sma50' in df.columns:
            if latest['sma20'] > latest['sma50']:
                sma_alignment += 1
            else:
                sma_alignment -= 1
                
        if 'sma50' in df.columns and 'sma200' in df.columns:
            if latest['sma50'] > latest['sma200']:
                sma_alignment += 1
            else:
                sma_alignment -= 1
        
        # Score based on price vs moving averages
        price_vs_ma = 0
        if 'sma20' in df.columns:
            if latest['close'] > latest['sma20']:
                price_vs_ma += 1
            else:
                price_vs_ma -= 1
                
        if 'sma200' in df.columns:
            if latest['close'] > latest['sma200']:
                price_vs_ma += 1
            else:
                price_vs_ma -= 1
        
        # ADX trend strength
        adx_score = 0
        if 'ADX_14' in df.columns:
            adx = latest['ADX_14']
            if adx > 30:  # Strong trend
                adx_score = 2
            elif adx > 20:  # Moderate trend
                adx_score = 1
            else:  # Weak trend
                adx_score = 0
        
        # Calculate overall trend score
        trend_score = (sma_alignment / 2) * 30 + (price_vs_ma / 2) * 30 + adx_score * 40
        
        return {'trend_score': trend_score / 100}  # Normalize to 0-1
    
    @staticmethod
    def volatility_score(df, window=20):
        """
        Calculate volatility score based on ATR relative to price.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            window: Window for volatility calculation
            
        Returns:
            Dictionary with volatility score
        """
        if len(df) < window or 'atr' not in df.columns:
            return {'volatility_score': 0}
        
        # ATR relative to price
        latest = df.iloc[-1]
        atr_pct = latest['atr'] / latest['close'] * 100
        
        # Normalize to 0-1 scale (5% ATR would be extremely volatile, scoring 1)
        volatility_score = min(atr_pct / 5, 1)
        
        return {'volatility_score': volatility_score}
    
    @staticmethod
    def volume_score(df, window=20):
        """
        Calculate volume score based on recent volume vs average.
        
        Args:
            df: DataFrame with OHLCV data
            window: Window for volume calculation
            
        Returns:
            Dictionary with volume score
        """
        if len(df) < window:
            return {'volume_score': 0}
        
        # Calculate recent average volume compared to longer window
        recent_vol_avg = df['volume'].iloc[-5:].mean()
        window_vol_avg = df['volume'].iloc[-window:].mean()
        
        # Volume ratio (above 1 means increased volume)
        vol_ratio = recent_vol_avg / window_vol_avg
        
        # Normalize to 0-1 scale
        volume_score = min(vol_ratio / 2, 1)  # 2x volume would be max score
        
        return {'volume_score': volume_score}
    
    @staticmethod
    def oscillator_score(df):
        """
        Calculate oscillator score based on RSI, Stochastic, etc.
        
        Args:
            df: DataFrame with indicator data
            
        Returns:
            Dictionary with oscillator scores and signals
        """
        if len(df) < 14 or 'rsi14' not in df.columns:
            return {'oscillator_score': 0.5, 'signals': {}}
        
        latest = df.iloc[-1]
        signals = {}
        
        # RSI signals
        rsi = latest['rsi14']
        if rsi < 30:
            signals['rsi'] = 'oversold'
            rsi_score = 0.8  # Bullish
        elif rsi > 70:
            signals['rsi'] = 'overbought'
            rsi_score = 0.2  # Bearish
        else:
            signals['rsi'] = 'neutral'
            rsi_score = 0.5
        
        # Stochastic signals if available
        stoch_score = 0.5
        if 'STOCHk_14_3_3' in df.columns and 'STOCHd_14_3_3' in df.columns:
            stoch_k = latest['STOCHk_14_3_3']
            stoch_d = latest['STOCHd_14_3_3']
            
            if stoch_k < 20 and stoch_d < 20:
                signals['stoch'] = 'oversold'
                stoch_score = 0.8  # Bullish
            elif stoch_k > 80 and stoch_d > 80:
                signals['stoch'] = 'overbought'
                stoch_score = 0.2  # Bearish
            else:
                signals['stoch'] = 'neutral'
        
        # Combine scores
        oscillator_score = (rsi_score + stoch_score) / 2
        
        return {'oscillator_score': oscillator_score, 'signals': signals}
    
    @staticmethod
    def pattern_score(df):
        """
        Calculate score based on candlestick patterns.
        
        Args:
            df: DataFrame with pattern recognition data
            
        Returns:
            Dictionary with pattern scores
        """
        if len(df) < 5:
            return {'pattern_score': 0.5, 'patterns': []}
        
        # Check for patterns in the last 3 days
        patterns = []
        pattern_value = 0
        count = 0
        
        for i in range(1, min(4, len(df))):
            row = df.iloc[-i]
            
            pattern_fields = ['doji', 'engulfing', 'hammer', 'shooting_star']
            for field in pattern_fields:
                if field in row and row[field] != 0:
                    patterns.append(f"{field}:{row[field]}")
                    # Add to the score (positive or negative)
                    pattern_value += row[field]
                    count += 1
        
        # Normalize to 0-1 scale
        if count > 0:
            normalized_score = 0.5 + (pattern_value / (count * 2))  # Convert to 0-1 scale
            pattern_score = max(0, min(1, normalized_score))  # Clamp to 0-1
        else:
            pattern_score = 0.5  # Neutral if no patterns found
        
        return {'pattern_score': pattern_score, 'patterns': patterns}
    
    @staticmethod
    def calculate_overall_score(df):
        """
        Calculate an overall stock score combining all metrics.
        
        Args:
            df: DataFrame with price, volume, and indicator data
            
        Returns:
            Dictionary with overall score and component scores
        """
        # Ensure we have all necessary indicators
        if not isinstance(df, pd.DataFrame) or df.empty:
            return {'overall_score': 0, 'error': 'Invalid or empty dataframe'}
            
        if len(df) < 60:
            return {'overall_score': 0, 'error': 'Insufficient data points'}
        
        # Calculate component scores
        momentum = StockScoring.momentum_score(df)
        trend = StockScoring.trend_score(df)
        volatility = StockScoring.volatility_score(df)
        volume = StockScoring.volume_score(df)
        oscillator = StockScoring.oscillator_score(df)
        pattern = StockScoring.pattern_score(df)
        
        # Weighted overall score (0-100)
        weights = {
            'momentum': 0.25,
            'trend': 0.30,
            'volatility': 0.10,
            'volume': 0.10,
            'oscillator': 0.15,
            'pattern': 0.10
        }
        
        # Normalize momentum to 0-1 scale (assuming ±10% is the range)
        momentum_norm = 0.5
        if 'momentum_overall' in momentum:
            momentum_norm = max(0, min(1, (momentum['momentum_overall'] + 10) / 20))
        
        # Calculate weighted score
        score_components = {
            'momentum': momentum_norm,
            'trend': trend.get('trend_score', 0.5),
            'volatility': 1 - volatility.get('volatility_score', 0.5),  # Lower volatility is better
            'volume': volume.get('volume_score', 0.5),
            'oscillator': oscillator.get('oscillator_score', 0.5),
            'pattern': pattern.get('pattern_score', 0.5)
        }
        
        weighted_score = sum(score_components[k] * weights[k] for k in weights)
        
        # Scale to 0-100
        overall_score = weighted_score * 100
        
        # Determine signal
        signal = 'neutral'
        if overall_score > 70:
            signal = 'buy'
        elif overall_score < 30:
            signal = 'sell'
        
        # Create result dictionary
        result = {
            'overall_score': overall_score,
            'signal': signal,
            'components': {
                'momentum': momentum,
                'trend': trend,
                'volatility': volatility,
                'volume': volume,
                'oscillator': oscillator,
                'pattern': pattern
            },
            'component_scores': score_components
        }
        
        return result
    
    @staticmethod
    def generate_report(df, symbol):
        """
        Generate a comprehensive report for a stock.
        
        Args:
            df: DataFrame with price, volume, and indicator data
            symbol: Stock symbol
            
        Returns:
            Dictionary with report data
        """
        # Ensure we have the indicators
        if 'sma20' not in df.columns:
            df = TechnicalIndicators.calculate_all_indicators(df)
        
        # Get the scoring
        score_data = StockScoring.calculate_overall_score(df)
        
        # Get the latest price data
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # Calculate daily change
        daily_change = (latest['close'] - prev['close']) / prev['close'] * 100
        
        # Key price levels
        support_levels = []
        resistance_levels = []
        
        # Simple support/resistance based on recent lows/highs
        recent = df.iloc[-20:] if len(df) >= 20 else df
        support_levels.append(round(recent['low'].min(), 2))
        resistance_levels.append(round(recent['high'].max(), 2))
        
        # Add moving averages as support/resistance
        if 'sma50' in df.columns:
            support_levels.append(round(latest['sma50'], 2))
        if 'sma200' in df.columns:
            support_levels.append(round(latest['sma200'], 2))
        
        # Create the report
        report = {
            'symbol': symbol,
            'date': str(latest.name) if hasattr(latest.name, 'strftime') else str(latest.name),
            'price': {
                'open': latest['open'],
                'high': latest['high'],
                'low': latest['low'],
                'close': latest['close'],
                'volume': latest['volume'],
                'daily_change': daily_change
            },
            'score': score_data['overall_score'],
            'signal': score_data['signal'],
            'key_levels': {
                'support': sorted(support_levels),
                'resistance': sorted(resistance_levels)
            },
            'indicators': {
                'sma20': latest.get('sma20', None),
                'sma50': latest.get('sma50', None),
                'sma200': latest.get('sma200', None),
                'rsi': latest.get('rsi14', None),
                'macd': latest.get('MACD_12_26_9', None),
                'macd_signal': latest.get('MACDs_12_26_9', None)
            },
            'component_scores': score_data['component_scores'],
            'signals': {}
        }
        
        # Add oscillator signals
        if 'signals' in score_data['components']['oscillator']:
            report['signals'].update(score_data['components']['oscillator']['signals'])
        
        # Add pattern signals
        if 'patterns' in score_data['components']['pattern']:
            report['signals']['patterns'] = score_data['components']['pattern']['patterns']
        
        return report
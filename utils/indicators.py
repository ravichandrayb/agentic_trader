# Technical indicators for stock analysis

import pandas as pd
import pandas_ta as ta
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def add_basic_indicators(df):
        """
        Add basic technical indicators to a DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        # Make a copy to avoid modifying the original
        result = df.copy()
        
        # Ensure we have the required columns
        required = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in result.columns]
        if missing:
            raise ValueError(f"DataFrame missing required columns: {missing}")
        
        # Simple Moving Averages
        result['sma20'] = ta.sma(result['close'], length=20)
        result['sma50'] = ta.sma(result['close'], length=50)
        result['sma200'] = ta.sma(result['close'], length=200)
        
        # Exponential Moving Averages
        result['ema9'] = ta.ema(result['close'], length=9)
        result['ema21'] = ta.ema(result['close'], length=21)
        
        # Relative Strength Index
        result['rsi14'] = ta.rsi(result['close'], length=14)
        
        # MACD
        macd = ta.macd(result['close'])
        result = pd.concat([result, macd], axis=1)
        
        # Bollinger Bands
        bbands = ta.bbands(result['close'], length=20)
        result = pd.concat([result, bbands], axis=1)
        
        # Average True Range
        result['atr'] = ta.atr(result['high'], result['low'], result['close'], length=14)
        
        # Volume indicators
        result['volume_sma20'] = ta.sma(result['volume'], length=20)
        result['volume_ratio'] = result['volume'] / result['volume_sma20']
        
        return result
    
    @staticmethod
    def add_advanced_indicators(df):
        """
        Add more advanced technical indicators to a DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        # Make a copy to avoid modifying the original
        result = df.copy()
        
        # Ichimoku Cloud
        ichimoku = ta.ichimoku(result['high'], result['low'], result['close'])
        result = pd.concat([result, ichimoku], axis=1)
        
        # Parabolic SAR
        result['psar'] = ta.psar(result['high'], result['low'])
        
        # Stochastic Oscillator
        stoch = ta.stoch(result['high'], result['low'], result['close'])
        result = pd.concat([result, stoch], axis=1)
        
        # Commodity Channel Index
        result['cci'] = ta.cci(result['high'], result['low'], result['close'])
        
        # On-Balance Volume
        result['obv'] = ta.obv(result['close'], result['volume'])
        
        # Awesome Oscillator
        result['ao'] = ta.ao(result['high'], result['low'])
        
        return result
    
    @staticmethod
    def add_trend_indicators(df):
        """
        Add trend identification indicators to a DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added trend indicators
        """
        result = df.copy()
        
        # ADX (Average Directional Index)
        adx = ta.adx(result['high'], result['low'], result['close'])
        result = pd.concat([result, adx], axis=1)
        
        # Trend identification based on moving averages
        result['trend_sma'] = np.where(result['sma20'] > result['sma50'], 1, 
                               np.where(result['sma20'] < result['sma50'], -1, 0))
        
        # Price above/below moving averages
        result['price_vs_sma200'] = np.where(result['close'] > result['sma200'], 1, -1)
        
        # Golden/Death Cross (SMA 50 and 200)
        result['golden_cross'] = np.where((result['sma50'] > result['sma200']) & 
                                 (result['sma50'].shift(1) <= result['sma200'].shift(1)), 1, 0)
        result['death_cross'] = np.where((result['sma50'] < result['sma200']) & 
                                (result['sma50'].shift(1) >= result['sma200'].shift(1)), 1, 0)
        
        return result
    
    @staticmethod
    def add_pattern_recognition(df):
        """
        Add candlestick pattern recognition to a DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added pattern indicators
        """
        result = df.copy()
        
        # Candlestick patterns
        result['doji'] = ta.cdl_pattern(result['open'], result['high'], result['low'], result['close'], 'doji')
        result['engulfing'] = ta.cdl_pattern(result['open'], result['high'], result['low'], result['close'], 'engulfing')
        result['hammer'] = ta.cdl_pattern(result['open'], result['high'], result['low'], result['close'], 'hammer')
        result['shooting_star'] = ta.cdl_pattern(result['open'], result['high'], result['low'], result['close'], 'shootingstar')
        
        return result
    
    @staticmethod
    def calculate_all_indicators(df):
        """
        Calculate all available indicators.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all indicators
        """
        result = TechnicalIndicators.add_basic_indicators(df)
        result = TechnicalIndicators.add_advanced_indicators(result)
        result = TechnicalIndicators.add_trend_indicators(result)
        result = TechnicalIndicators.add_pattern_recognition(result)
        
        # Replace infinite values with NaN and then fill NaN with 0
        result = result.replace([np.inf, -np.inf], np.nan)
        result = result.fillna(0)
        
        return result
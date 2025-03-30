import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime

class TradingStrategy:
    """
    Implementation of various trading strategies for cryptocurrency.
    """
    def __init__(self, risk_percentage=1.0, max_open_trades=3):
        """
        Initialize the trading strategy with risk parameters.
        
        Args:
            risk_percentage (float): Percentage of account to risk per trade
            max_open_trades (int): Maximum number of concurrent open trades
        """
        self.risk_percentage = risk_percentage
        self.max_open_trades = max_open_trades
        
    def calculate_indicators(self, df):
        """
        Calculate technical indicators for analysis.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: DataFrame with added indicators
        """
        if df.empty:
            return df
        
        # Copy DataFrame to avoid modifying the original
        result = df.copy()
        
        # Calculate EMAs
        result['ema20'] = ta.ema(result['close'], length=20)
        result['ema50'] = ta.ema(result['close'], length=50)
        result['ema100'] = ta.ema(result['close'], length=100)
        
        # Calculate RSI
        result['rsi'] = ta.rsi(result['close'], length=14)
        
        # Calculate Bollinger Bands
        bbands = ta.bbands(result['close'], length=20)
        result = pd.concat([result, bbands], axis=1)
        
        # Calculate MACD
        macd = ta.macd(result['close'])
        result = pd.concat([result, macd], axis=1)
        
        # Calculate Average True Range for volatility
        result['atr'] = ta.atr(result['high'], result['low'], result['close'], length=14)
        
        # Calculate Volume Moving Average
        result['volume_sma'] = ta.sma(result['volume'], length=20)
        
        # Calculate support and resistance
        self._add_support_resistance(result)
        
        return result
    
    def _add_support_resistance(self, df, window=10):
        """
        Add support and resistance levels to the DataFrame.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            window (int): Window size for support/resistance calculation
        """
        # Initialize columns
        df['support'] = np.nan
        df['resistance'] = np.nan
        
        # Loop through data to find local minima/maxima
        for i in range(window, len(df) - window):
            # Check for local low (support)
            if all(df['low'].iloc[i] <= df['low'].iloc[i-window:i]) and \
               all(df['low'].iloc[i] <= df['low'].iloc[i+1:i+window+1]):
                df.loc[df.index[i], 'support'] = df['low'].iloc[i]
            
            # Check for local high (resistance)
            if all(df['high'].iloc[i] >= df['high'].iloc[i-window:i]) and \
               all(df['high'].iloc[i] >= df['high'].iloc[i+1:i+window+1]):
                df.loc[df.index[i], 'resistance'] = df['high'].iloc[i]
    
    def identify_break_retest(self, df):
        """
        Identify break and retest patterns in the price data.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV and indicator data
            
        Returns:
            list: Identified break and retest patterns
        """
        if df.empty or 'support' not in df.columns or 'resistance' not in df.columns:
            return []
        
        patterns = []
        
        # Loop through the data to find break and retest patterns
        for i in range(5, len(df)):
            # Resistance break and retest
            if not pd.isna(df['resistance'].iloc[i-5]):
                resistance_level = df['resistance'].iloc[i-5]
                
                # Check for breakout above resistance
                if any(df['close'].iloc[i-4:i-1] > resistance_level):
                    # Check for retest of the broken resistance
                    if df['low'].iloc[i] <= resistance_level <= df['high'].iloc[i]:
                        pattern = {
                            'type': 'resistance_break_retest',
                            'level': resistance_level,
                            'date': df.index[i] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[i],
                            'signal': 'buy',
                            'price': df['close'].iloc[i],
                            'stop_loss': df['low'].iloc[i-1] - df['atr'].iloc[i]
                        }
                        patterns.append(pattern)
            
            # Support break and retest
            if not pd.isna(df['support'].iloc[i-5]):
                support_level = df['support'].iloc[i-5]
                
                # Check for breakout below support
                if any(df['close'].iloc[i-4:i-1] < support_level):
                    # Check for retest of the broken support
                    if df['low'].iloc[i] <= support_level <= df['high'].iloc[i]:
                        pattern = {
                            'type': 'support_break_retest',
                            'level': support_level,
                            'date': df.index[i] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[i],
                            'signal': 'sell',
                            'price': df['close'].iloc[i],
                            'stop_loss': df['high'].iloc[i-1] + df['atr'].iloc[i]
                        }
                        patterns.append(pattern)
        
        return patterns
    
    def identify_liquidity_sweep(self, df, liquidity_levels):
        """
        Identify liquidity sweep patterns.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV and indicator data
            liquidity_levels (list): List of identified liquidity levels
            
        Returns:
            list: Identified liquidity sweep patterns
        """
        if df.empty or not liquidity_levels:
            return []
        
        patterns = []
        
        # Loop through the data to find liquidity sweep patterns
        for i in range(5, len(df)):
            for level in liquidity_levels:
                level_price = level['price']
                
                # Look for price quickly sweeping through liquidity level and reversing
                if df['low'].iloc[i] < level_price < df['low'].iloc[i-1] and df['close'].iloc[i] > level_price:
                    # Bullish sweep (sweep lows and reverse up)
                    pattern = {
                        'type': 'liquidity_sweep_bullish',
                        'level': level_price,
                        'date': df.index[i] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[i],
                        'signal': 'buy',
                        'price': df['close'].iloc[i],
                        'stop_loss': df['low'].iloc[i] - df['atr'].iloc[i],
                        'strength': level['strength']
                    }
                    patterns.append(pattern)
                
                elif df['high'].iloc[i] > level_price > df['high'].iloc[i-1] and df['close'].iloc[i] < level_price:
                    # Bearish sweep (sweep highs and reverse down)
                    pattern = {
                        'type': 'liquidity_sweep_bearish',
                        'level': level_price,
                        'date': df.index[i] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[i],
                        'signal': 'sell',
                        'price': df['close'].iloc[i],
                        'stop_loss': df['high'].iloc[i] + df['atr'].iloc[i],
                        'strength': level['strength']
                    }
                    patterns.append(pattern)
        
        return patterns
    
    def calculate_position_size(self, account_balance, entry_price, stop_loss, symbol):
        """
        Calculate appropriate position size based on risk management rules.
        
        Args:
            account_balance (float): Total account balance
            entry_price (float): Entry price for the trade
            stop_loss (float): Stop loss price
            symbol (str): Trading pair symbol
            
        Returns:
            float: Position size in base currency
        """
        # Calculate risk amount based on account balance and risk percentage
        risk_amount = account_balance * (self.risk_percentage / 100)
        
        # Calculate position size
        if entry_price > stop_loss:  # Long position
            risk_per_unit = entry_price - stop_loss
        else:  # Short position
            risk_per_unit = stop_loss - entry_price
        
        if risk_per_unit <= 0:
            return 0
        
        position_size = risk_amount / risk_per_unit
        
        return position_size
    
    def generate_trade_signal(self, df, liquidity_levels, current_balance=10000):
        """
        Generate trading signals based on identified patterns.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV and indicator data
            liquidity_levels (list): List of identified liquidity levels
            current_balance (float): Current account balance
            
        Returns:
            dict: Trade signal information if a signal is generated, None otherwise
        """
        if df.empty:
            return None
        
        # Calculate indicators
        analysis_df = self.calculate_indicators(df)
        
        # Identify patterns
        break_retest_patterns = self.identify_break_retest(analysis_df)
        liquidity_sweep_patterns = self.identify_liquidity_sweep(analysis_df, liquidity_levels)
        
        # Combine patterns and sort by most recent
        all_patterns = break_retest_patterns + liquidity_sweep_patterns
        if not all_patterns:
            return None
        
        # Sort by date, most recent first
        all_patterns.sort(key=lambda x: x['date'], reverse=True)
        
        # Get the most recent pattern
        latest_pattern = all_patterns[0]
        
        # Check if the pattern is recent enough (last 3 candles)
        latest_timestamp = df['timestamp'].iloc[-1] if 'timestamp' in df.columns else df.index[-1]
        pattern_timestamp = latest_pattern['date']
        
        # Convert to datetime objects if they aren't already
        if not isinstance(latest_timestamp, datetime):
            latest_timestamp = pd.to_datetime(latest_timestamp)
        if not isinstance(pattern_timestamp, datetime):
            pattern_timestamp = pd.to_datetime(pattern_timestamp)
        
        time_diff = latest_timestamp - pattern_timestamp
        if time_diff.total_seconds() > 10800:  # More than 3 hours old
            return None
        
        # Calculate position size
        position_size = self.calculate_position_size(
            current_balance, 
            latest_pattern['price'], 
            latest_pattern['stop_loss'], 
            'BTC/USDT'  # Example symbol, should be replaced with actual symbol
        )
        
        # Create trade signal
        signal = {
            'type': latest_pattern['type'],
            'signal': latest_pattern['signal'],
            'price': latest_pattern['price'],
            'stop_loss': latest_pattern['stop_loss'],
            'date': latest_pattern['date'],
            'position_size': position_size,
            'take_profit': self.calculate_take_profit(latest_pattern),
            'risk_reward': self.calculate_risk_reward(latest_pattern)
        }
        
        return signal
    
    def calculate_take_profit(self, pattern):
        """
        Calculate take profit level based on pattern and risk-reward ratio.
        
        Args:
            pattern (dict): Pattern information
            
        Returns:
            float: Take profit price
        """
        risk = abs(pattern['price'] - pattern['stop_loss'])
        if pattern['signal'] == 'buy':
            return pattern['price'] + (risk * 2)  # 1:2 risk-reward ratio
        else:
            return pattern['price'] - (risk * 2)  # 1:2 risk-reward ratio
    
    def calculate_risk_reward(self, pattern):
        """
        Calculate risk-reward ratio for a pattern.
        
        Args:
            pattern (dict): Pattern information
            
        Returns:
            float: Risk-reward ratio
        """
        risk = abs(pattern['price'] - pattern['stop_loss'])
        take_profit = self.calculate_take_profit(pattern)
        reward = abs(pattern['price'] - take_profit)
        
        if risk == 0:
            return 0
        
        return reward / risk

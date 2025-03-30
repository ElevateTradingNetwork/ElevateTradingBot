import pandas as pd
import numpy as np
import pandas_ta as ta

class PatternRecognition:
    """
    Implements pattern recognition algorithms for technical analysis.
    """
    
    @staticmethod
    def identify_candlestick_patterns(df):
        """
        Identify candlestick patterns in OHLCV data.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            list: Identified candlestick patterns
        """
        if df.empty:
            return []
        
        patterns = []
        
        # Make a copy of the dataframe to avoid modifying the original
        ohlc = df.copy()
        
        # Calculate average body size
        ohlc['body_size'] = abs(ohlc['close'] - ohlc['open'])
        avg_body = ohlc['body_size'].mean()
        avg_range = (ohlc['high'] - ohlc['low']).mean()
        
        # Loop through the data to find patterns (starting from the 3rd candle)
        for i in range(3, len(ohlc)):
            idx = ohlc.index[i]
            
            # Get current and previous candles
            curr = ohlc.iloc[i]
            prev1 = ohlc.iloc[i-1]
            prev2 = ohlc.iloc[i-2]
            prev3 = ohlc.iloc[i-3]
            
            timestamp = curr['timestamp'] if 'timestamp' in curr.index else idx
            
            # Doji Pattern (small body)
            if curr['body_size'] < 0.1 * avg_range:
                patterns.append({
                    'type': 'doji',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 1
                })
            
            # Hammer Pattern (bullish)
            if (curr['close'] > curr['open'] and  # Bullish candle
                curr['body_size'] > 0.1 * avg_range and  # Significant body
                (curr['low'] < curr['open'] - 2 * curr['body_size']) and  # Long lower wick
                (curr['high'] - max(curr['close'], curr['open']) < 0.3 * curr['body_size']):  # Short/no upper wick
                patterns.append({
                    'type': 'hammer_bullish',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 2
                })
            
            # Inverted Hammer Pattern (bullish)
            if (curr['close'] > curr['open'] and  # Bullish candle
                curr['body_size'] > 0.1 * avg_range and  # Significant body
                (curr['high'] > curr['close'] + 2 * curr['body_size']) and  # Long upper wick
                (min(curr['close'], curr['open']) - curr['low'] < 0.3 * curr['body_size']):  # Short/no lower wick
                patterns.append({
                    'type': 'inverted_hammer_bullish',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 2
                })
            
            # Shooting Star Pattern (bearish)
            if (curr['close'] < curr['open'] and  # Bearish candle
                curr['body_size'] > 0.1 * avg_range and  # Significant body
                (curr['high'] > curr['open'] + 2 * curr['body_size']) and  # Long upper wick
                (min(curr['close'], curr['open']) - curr['low'] < 0.3 * curr['body_size']):  # Short/no lower wick
                patterns.append({
                    'type': 'shooting_star',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 3
                })
            
            # Hanging Man Pattern (bearish)
            if (curr['close'] < curr['open'] and  # Bearish candle
                curr['body_size'] > 0.1 * avg_range and  # Significant body
                (curr['low'] < curr['close'] - 2 * curr['body_size']) and  # Long lower wick
                (curr['high'] - max(curr['close'], curr['open']) < 0.3 * curr['body_size']):  # Short/no upper wick
                patterns.append({
                    'type': 'hanging_man',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 3
                })
            
            # Engulfing Bullish
            if (prev1['close'] < prev1['open'] and  # Previous is bearish
                curr['close'] > curr['open'] and  # Current is bullish
                curr['open'] < prev1['close'] and  # Open below previous close
                curr['close'] > prev1['open']):  # Close above previous open
                patterns.append({
                    'type': 'engulfing_bullish',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 4
                })
            
            # Engulfing Bearish
            if (prev1['close'] > prev1['open'] and  # Previous is bullish
                curr['close'] < curr['open'] and  # Current is bearish
                curr['open'] > prev1['close'] and  # Open above previous close
                curr['close'] < prev1['open']):  # Close below previous open
                patterns.append({
                    'type': 'engulfing_bearish',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 4
                })
            
            # Morning Star (bullish)
            if (prev2['close'] < prev2['open'] and  # First candle is bearish
                abs(prev1['close'] - prev1['open']) < 0.3 * avg_body and  # Second candle is small (doji-like)
                curr['close'] > curr['open'] and  # Third candle is bullish
                curr['close'] > (prev2['open'] + prev2['close']) / 2):  # Close above midpoint of first candle
                patterns.append({
                    'type': 'morning_star',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 5
                })
            
            # Evening Star (bearish)
            if (prev2['close'] > prev2['open'] and  # First candle is bullish
                abs(prev1['close'] - prev1['open']) < 0.3 * avg_body and  # Second candle is small (doji-like)
                curr['close'] < curr['open'] and  # Third candle is bearish
                curr['close'] < (prev2['open'] + prev2['close']) / 2):  # Close below midpoint of first candle
                patterns.append({
                    'type': 'evening_star',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 5
                })
            
            # Three White Soldiers (bullish)
            if (prev2['close'] > prev2['open'] and  # First candle is bullish
                prev1['close'] > prev1['open'] and  # Second candle is bullish
                curr['close'] > curr['open'] and  # Third candle is bullish
                prev1['close'] > prev2['close'] and  # Each close is higher than previous
                curr['close'] > prev1['close'] and
                prev1['open'] > prev2['open'] and  # Each open is higher than previous
                curr['open'] > prev1['open']):
                patterns.append({
                    'type': 'three_white_soldiers',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 5
                })
            
            # Three Black Crows (bearish)
            if (prev2['close'] < prev2['open'] and  # First candle is bearish
                prev1['close'] < prev1['open'] and  # Second candle is bearish
                curr['close'] < curr['open'] and  # Third candle is bearish
                prev1['close'] < prev2['close'] and  # Each close is lower than previous
                curr['close'] < prev1['close'] and
                prev1['open'] < prev2['open'] and  # Each open is lower than previous
                curr['open'] < prev1['open']):
                patterns.append({
                    'type': 'three_black_crows',
                    'candle_idx': i,
                    'timestamp': timestamp,
                    'price': curr['close'],
                    'strength': 5
                })
        
        return patterns
    
    @staticmethod
    def identify_break_retest_patterns(df):
        """
        Identify break and retest patterns in price data.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV and potentially indicator data
            
        Returns:
            list: Identified break and retest patterns
        """
        if df.empty:
            return []
        
        # Make a copy and ensure we have all required columns
        ohlc = df.copy()
        
        if 'support' not in ohlc.columns or 'resistance' not in ohlc.columns:
            # Calculate pivot points for support/resistance
            ohlc['pivot_high'] = np.nan
            ohlc['pivot_low'] = np.nan
            
            # Simple pivot point calculation (for demonstration - a more sophisticated algorithm would be better)
            window = 5
            for i in range(window, len(ohlc) - window):
                # Check if current candle's high is highest in the window
                if ohlc['high'].iloc[i] == ohlc['high'].iloc[i-window:i+window+1].max():
                    ohlc.loc[ohlc.index[i], 'pivot_high'] = ohlc['high'].iloc[i]
                
                # Check if current candle's low is lowest in the window
                if ohlc['low'].iloc[i] == ohlc['low'].iloc[i-window:i+window+1].min():
                    ohlc.loc[ohlc.index[i], 'pivot_low'] = ohlc['low'].iloc[i]
        
        # Initialize lists for supports, resistances and patterns
        supports = []
        resistances = []
        patterns = []
        
        # If we have support/resistance columns, use them
        if 'support' in ohlc.columns:
            supports = ohlc[~ohlc['support'].isna()][['timestamp' if 'timestamp' in ohlc.columns else ohlc.index.name, 'support']].values.tolist()
        elif 'pivot_low' in ohlc.columns:
            supports = ohlc[~ohlc['pivot_low'].isna()][['timestamp' if 'timestamp' in ohlc.columns else ohlc.index.name, 'pivot_low']].values.tolist()
        
        if 'resistance' in ohlc.columns:
            resistances = ohlc[~ohlc['resistance'].isna()][['timestamp' if 'timestamp' in ohlc.columns else ohlc.index.name, 'resistance']].values.tolist()
        elif 'pivot_high' in ohlc.columns:
            resistances = ohlc[~ohlc['pivot_high'].isna()][['timestamp' if 'timestamp' in ohlc.columns else ohlc.index.name, 'pivot_high']].values.tolist()
        
        # Build dictionary of index positions for timestamps
        timestamp_to_idx = {}
        for i, idx in enumerate(ohlc.index):
            if 'timestamp' in ohlc.columns:
                timestamp_to_idx[ohlc['timestamp'].iloc[i]] = i
            else:
                timestamp_to_idx[idx] = i
        
        # Find break and retest of resistance
        for resistance in resistances:
            timestamp, level = resistance
            
            # Skip if timestamp is not in our dictionary (shouldn't happen but just to be safe)
            if timestamp not in timestamp_to_idx:
                continue
                
            level_idx = timestamp_to_idx[timestamp]
            
            # Look for a break of the resistance (at least 3 candles after pivot)
            for i in range(level_idx + 3, min(level_idx + 20, len(ohlc))):
                if ohlc['close'].iloc[i] > level * 1.005:  # 0.5% breakout
                    breakout_idx = i
                    
                    # Look for retest of the broken resistance
                    for j in range(breakout_idx + 1, min(breakout_idx + 15, len(ohlc))):
                        if ohlc['low'].iloc[j] <= level <= ohlc['high'].iloc[j]:
                            if ohlc['close'].iloc[j] > level:  # Bullish retest
                                retest_timestamp = ohlc.index[j] if not isinstance(ohlc.index, pd.RangeIndex) else ohlc['timestamp'].iloc[j]
                                patterns.append({
                                    'type': 'resistance_break_retest',
                                    'subtype': 'bullish',
                                    'level': level,
                                    'breakout_idx': breakout_idx,
                                    'retest_idx': j,
                                    'timestamp': retest_timestamp,
                                    'price': ohlc['close'].iloc[j],
                                    'strength': 4
                                })
                                break
                    break
        
        # Find break and retest of support
        for support in supports:
            timestamp, level = support
            
            # Skip if timestamp is not in our dictionary
            if timestamp not in timestamp_to_idx:
                continue
                
            level_idx = timestamp_to_idx[timestamp]
            
            # Look for a break of the support (at least 3 candles after pivot)
            for i in range(level_idx + 3, min(level_idx + 20, len(ohlc))):
                if ohlc['close'].iloc[i] < level * 0.995:  # 0.5% breakdown
                    breakdown_idx = i
                    
                    # Look for retest of the broken support
                    for j in range(breakdown_idx + 1, min(breakdown_idx + 15, len(ohlc))):
                        if ohlc['low'].iloc[j] <= level <= ohlc['high'].iloc[j]:
                            if ohlc['close'].iloc[j] < level:  # Bearish retest
                                retest_timestamp = ohlc.index[j] if not isinstance(ohlc.index, pd.RangeIndex) else ohlc['timestamp'].iloc[j]
                                patterns.append({
                                    'type': 'support_break_retest',
                                    'subtype': 'bearish',
                                    'level': level,
                                    'breakdown_idx': breakdown_idx,
                                    'retest_idx': j,
                                    'timestamp': retest_timestamp,
                                    'price': ohlc['close'].iloc[j],
                                    'strength': 4
                                })
                                break
                    break
        
        return patterns
    
    @staticmethod
    def identify_liquidity_sweeps(df, high_volume_levels):
        """
        Identify liquidity sweep patterns in price data.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            high_volume_levels (list): List of price levels with high liquidity
            
        Returns:
            list: Identified liquidity sweep patterns
        """
        if df.empty or not high_volume_levels:
            return []
        
        ohlc = df.copy()
        patterns = []
        
        # Loop through the candles
        for i in range(3, len(ohlc)):
            candle = ohlc.iloc[i]
            prev_candle = ohlc.iloc[i-1]
            
            timestamp = candle['timestamp'] if 'timestamp' in candle.index else ohlc.index[i]
            
            # Check each liquidity level
            for level in high_volume_levels:
                level_price = level['price']
                
                # Bullish sweep: price dips below support (liquidity grab) and closes back above
                if (prev_candle['low'] > level_price and  # Previous candle was above the level
                    candle['low'] < level_price and  # Current candle wicked below the level
                    candle['close'] > level_price):  # But closed back above
                    patterns.append({
                        'type': 'liquidity_sweep',
                        'subtype': 'bullish',
                        'level': level_price,
                        'candle_idx': i,
                        'timestamp': timestamp,
                        'price': candle['close'],
                        'strength': 3 + level.get('strength', 0) / 2  # Base strength + bonus from level strength
                    })
                
                # Bearish sweep: price spikes above resistance (liquidity grab) and closes back below
                elif (prev_candle['high'] < level_price and  # Previous candle was below the level
                      candle['high'] > level_price and  # Current candle wicked above the level
                      candle['close'] < level_price):  # But closed back below
                    patterns.append({
                        'type': 'liquidity_sweep',
                        'subtype': 'bearish',
                        'level': level_price,
                        'candle_idx': i,
                        'timestamp': timestamp,
                        'price': candle['close'],
                        'strength': 3 + level.get('strength', 0) / 2  # Base strength + bonus from level strength
                    })
        
        return patterns
    
    @staticmethod
    def calculate_pattern_probability(patterns, historical_patterns=None):
        """
        Calculate probability of pattern success based on historical data.
        
        Args:
            patterns (list): Current identified patterns
            historical_patterns (list): Historical patterns with outcome data
            
        Returns:
            list: Patterns with added probability metrics
        """
        if not patterns:
            return []
        
        # If we don't have historical data, just return base probabilities
        if not historical_patterns:
            for pattern in patterns:
                # Assign default probability based on pattern strength
                pattern['probability'] = min(0.3 + (pattern['strength'] / 10), 0.7)
            return patterns
        
        # If we have historical data, calculate probabilities based on past performance
        pattern_types = set(p['type'] for p in patterns)
        
        # Calculate success rates for each pattern type
        success_rates = {}
        for p_type in pattern_types:
            relevant_history = [p for p in historical_patterns if p['type'] == p_type and 'outcome' in p]
            if relevant_history:
                successes = sum(1 for p in relevant_history if p['outcome'] == 'success')
                success_rates[p_type] = successes / len(relevant_history)
            else:
                # Default if no history for this pattern type
                success_rates[p_type] = 0.5
        
        # Apply probabilities to current patterns
        for pattern in patterns:
            if pattern['type'] in success_rates:
                pattern['probability'] = success_rates[pattern['type']]
            else:
                # Fallback to strength-based probability
                pattern['probability'] = min(0.3 + (pattern['strength'] / 10), 0.7)
        
        return patterns

import os
import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta
import numpy as np

class BitgetClient:
    """
    Client for interacting with the Bitget exchange API.
    """
    def __init__(self):
        """
        Initialize the Bitget client with API credentials from environment variables.
        """
        self.api_key = os.getenv('BITGET_API_KEY', '')
        self.api_secret = os.getenv('BITGET_API_SECRET', '')
        self.api_password = os.getenv('BITGET_API_PASSWORD', '')
        
        # Initialize connection
        self.exchange = None
        self.connect()
        
    def connect(self):
        """
        Establish connection with Bitget API.
        """
        try:
            self.exchange = ccxt.bitget({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.api_password,
                'enableRateLimit': True
            })
            self.check_connection()
            return True
        except Exception as e:
            print(f"Error connecting to Bitget: {str(e)}")
            return False
    
    def check_connection(self):
        """
        Check if the connection to the exchange is working.
        """
        try:
            self.exchange.fetch_time()
            return True
        except Exception as e:
            print(f"Connection check failed: {str(e)}")
            return False
    
    def get_markets(self):
        """
        Get available trading markets/pairs.
        
        Returns:
            list: List of available trading pairs
        """
        try:
            self.exchange.load_markets()
            return list(self.exchange.markets.keys())
        except Exception as e:
            print(f"Error fetching markets: {str(e)}")
            return []
    
    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetch candlestick data for a specific trading pair.
        
        Args:
            symbol (str): Trading pair symbol
            timeframe (str): Timeframe for candlesticks (e.g., '1m', '5m', '1h', '1d')
            limit (int): Number of candles to fetch
            
        Returns:
            pandas.DataFrame: DataFrame containing OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching OHLCV data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_balance(self):
        """
        Get account balance.
        
        Returns:
            dict: Account balance information
        """
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            return {}
    
    def get_ticker(self, symbol):
        """
        Get current ticker information for a symbol.
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Ticker information
        """
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {str(e)}")
            return {}
    
    def create_order(self, symbol, order_type, side, amount, price=None, params={}):
        """
        Create a trading order.
        
        Args:
            symbol (str): Trading pair symbol
            order_type (str): Type of order ('limit' or 'market')
            side (str): Order side ('buy' or 'sell')
            amount (float): Order amount
            price (float, optional): Order price (required for limit orders)
            params (dict, optional): Additional parameters
            
        Returns:
            dict: Order information
        """
        try:
            return self.exchange.create_order(symbol, order_type, side, amount, price, params)
        except Exception as e:
            print(f"Error creating order: {str(e)}")
            return {}
    
    def cancel_order(self, order_id, symbol):
        """
        Cancel an existing order.
        
        Args:
            order_id (str): Order ID
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Cancellation result
        """
        try:
            return self.exchange.cancel_order(order_id, symbol)
        except Exception as e:
            print(f"Error cancelling order: {str(e)}")
            return {}
    
    def get_open_orders(self, symbol=None):
        """
        Get open orders.
        
        Args:
            symbol (str, optional): Trading pair symbol
            
        Returns:
            list: List of open orders
        """
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            print(f"Error fetching open orders: {str(e)}")
            return []
    
    def calculate_high_liquidity_levels(self, symbol, timeframe='1h', look_back=100):
        """
        Identify high liquidity levels based on volume and price.
        
        Args:
            symbol (str): Trading pair symbol
            timeframe (str): Timeframe for analysis
            look_back (int): Number of candles to analyze
            
        Returns:
            list: List of identified liquidity levels
        """
        try:
            df = self.fetch_ohlcv(symbol, timeframe, limit=look_back)
            if df.empty:
                return []
            
            # Identify areas with high volume
            df['volume_sma'] = df['volume'].rolling(window=10).mean()
            high_vol_areas = df[df['volume'] > df['volume_sma'] * 1.5]
            
            # Create liquidity levels at price points with high volume
            liquidity_levels = []
            for _, row in high_vol_areas.iterrows():
                level = {
                    'price': row['close'],
                    'volume': row['volume'],
                    'timestamp': row['timestamp'],
                    'strength': (row['volume'] / df['volume'].mean())
                }
                liquidity_levels.append(level)
            
            # Sort by strength
            liquidity_levels = sorted(liquidity_levels, key=lambda x: x['strength'], reverse=True)
            
            return liquidity_levels[:10]  # Return top 10 levels
        except Exception as e:
            print(f"Error calculating liquidity levels: {str(e)}")
            return []

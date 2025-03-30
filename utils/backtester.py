import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from utils.strategy import TradingStrategy
import joblib

class Backtester:
    """
    Backtester for evaluating trading strategies on historical data.
    """
    def __init__(self, starting_balance=10000, commission_rate=0.001):
        """
        Initialize backtester with account parameters.
        
        Args:
            starting_balance (float): Initial account balance
            commission_rate (float): Trading commission rate
        """
        self.starting_balance = starting_balance
        self.commission_rate = commission_rate
        self.strategy = TradingStrategy()
        
    def run_backtest(self, df, liquidity_levels=None):
        """
        Run a backtest on the provided historical data.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            liquidity_levels (list, optional): List of liquidity levels
            
        Returns:
            dict: Backtest results and performance metrics
        """
        if df.empty:
            return {'error': 'No data provided for backtesting'}
        
        # Ensure we have liquidity levels
        if liquidity_levels is None:
            liquidity_levels = []
        
        # Make a copy of the data to avoid modifying the original
        backtest_df = df.copy()
        
        # Calculate indicators
        analysis_df = self.strategy.calculate_indicators(backtest_df)
        
        # Initialize backtest variables
        balance = self.starting_balance
        initial_balance = balance
        in_position = False
        position = {}
        trades = []
        equity_curve = []
        
        # Run through the historical data
        for i in range(50, len(analysis_df)):  # Start after indicators have enough data
            # Current data point
            current_data = analysis_df.iloc[:i+1]
            current_price = current_data['close'].iloc[-1]
            current_date = current_data.index[-1] if isinstance(current_data.index, pd.DatetimeIndex) else current_data['timestamp'].iloc[-1]
            
            # Track equity for each period
            if in_position:
                if position['type'] == 'long':
                    current_value = balance + position['size'] * (current_price - position['entry_price'])
                else:  # short
                    current_value = balance + position['size'] * (position['entry_price'] - current_price)
            else:
                current_value = balance
            
            equity_curve.append({
                'date': current_date,
                'equity': current_value
            })
            
            # Check if we need to close existing position
            if in_position:
                # Check for stop loss hit
                if position['type'] == 'long' and current_price <= position['stop_loss']:
                    # Close long position at stop loss
                    profit = position['size'] * (position['stop_loss'] - position['entry_price'])
                    commission = position['size'] * position['stop_loss'] * self.commission_rate
                    balance += profit - commission
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': position['stop_loss'],
                        'type': position['type'],
                        'size': position['size'],
                        'profit': profit,
                        'commission': commission,
                        'result': 'stop_loss'
                    })
                    
                    in_position = False
                    
                elif position['type'] == 'short' and current_price >= position['stop_loss']:
                    # Close short position at stop loss
                    profit = position['size'] * (position['entry_price'] - position['stop_loss'])
                    commission = position['size'] * position['stop_loss'] * self.commission_rate
                    balance += profit - commission
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': position['stop_loss'],
                        'type': position['type'],
                        'size': position['size'],
                        'profit': profit,
                        'commission': commission,
                        'result': 'stop_loss'
                    })
                    
                    in_position = False
                    
                # Check for take profit hit
                elif position['type'] == 'long' and current_price >= position['take_profit']:
                    # Close long position at take profit
                    profit = position['size'] * (position['take_profit'] - position['entry_price'])
                    commission = position['size'] * position['take_profit'] * self.commission_rate
                    balance += profit - commission
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': position['take_profit'],
                        'type': position['type'],
                        'size': position['size'],
                        'profit': profit,
                        'commission': commission,
                        'result': 'take_profit'
                    })
                    
                    in_position = False
                    
                elif position['type'] == 'short' and current_price <= position['take_profit']:
                    # Close short position at take profit
                    profit = position['size'] * (position['entry_price'] - position['take_profit'])
                    commission = position['size'] * position['take_profit'] * self.commission_rate
                    balance += profit - commission
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': position['take_profit'],
                        'type': position['type'],
                        'size': position['size'],
                        'profit': profit,
                        'commission': commission,
                        'result': 'take_profit'
                    })
                    
                    in_position = False
            
            # Look for new entry signals if not in a position
            if not in_position:
                # Get current subset of data
                subset_df = current_data.iloc[-30:]  # Last 30 candles
                
                # Get current liquidity levels (in real system, this would be updated)
                current_liquidity = [level for level in liquidity_levels 
                                     if level['timestamp'] < current_date]
                
                # Generate signal
                signal = self.strategy.generate_trade_signal(subset_df, current_liquidity, balance)
                
                if signal:
                    # Calculate position size (risk management)
                    position_size = balance * 0.02 / abs(current_price - signal['stop_loss'])
                    
                    # Check if we have enough balance
                    if position_size * current_price * (1 + self.commission_rate) <= balance:
                        # Enter position
                        if signal['signal'] == 'buy':
                            # Enter long position
                            cost = position_size * current_price
                            commission = cost * self.commission_rate
                            balance -= (cost + commission)
                            
                            position = {
                                'type': 'long',
                                'entry_price': current_price,
                                'stop_loss': signal['stop_loss'],
                                'take_profit': signal['take_profit'],
                                'size': position_size,
                                'entry_date': current_date
                            }
                            
                            in_position = True
                            
                        elif signal['signal'] == 'sell':
                            # Enter short position
                            cost = position_size * current_price
                            commission = cost * self.commission_rate
                            balance -= commission
                            
                            position = {
                                'type': 'short',
                                'entry_price': current_price,
                                'stop_loss': signal['stop_loss'],
                                'take_profit': signal['take_profit'],
                                'size': position_size,
                                'entry_date': current_date
                            }
                            
                            in_position = True
        
        # Close any open position at the end
        if in_position:
            final_price = analysis_df['close'].iloc[-1]
            
            if position['type'] == 'long':
                profit = position['size'] * (final_price - position['entry_price'])
            else:  # short
                profit = position['size'] * (position['entry_price'] - final_price)
                
            commission = position['size'] * final_price * self.commission_rate
            balance += profit - commission
            
            trades.append({
                'entry_date': position['entry_date'],
                'exit_date': analysis_df.index[-1] if isinstance(analysis_df.index, pd.DatetimeIndex) else analysis_df['timestamp'].iloc[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'type': position['type'],
                'size': position['size'],
                'profit': profit,
                'commission': commission,
                'result': 'end_of_period'
            })
        
        # Calculate performance metrics
        metrics = self.calculate_performance_metrics(trades, initial_balance, balance, equity_curve)
        
        # Return results
        return {
            'initial_balance': initial_balance,
            'final_balance': balance,
            'profit_loss': balance - initial_balance,
            'profit_loss_percent': ((balance - initial_balance) / initial_balance) * 100,
            'trades': trades,
            'metrics': metrics,
            'equity_curve': equity_curve
        }
    
    def calculate_performance_metrics(self, trades, initial_balance, final_balance, equity_curve):
        """
        Calculate performance metrics from backtest results.
        
        Args:
            trades (list): List of trade records
            initial_balance (float): Initial account balance
            final_balance (float): Final account balance
            equity_curve (list): List of equity values over time
            
        Returns:
            dict: Performance metrics
        """
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'average_profit': 0,
                'average_loss': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        # Calculate basic metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['profit'] > 0]
        losing_trades = [t for t in trades if t['profit'] <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = win_count / total_trades if total_trades > 0 else 0
        
        # Calculate profit metrics
        total_profit = sum(t['profit'] for t in winning_trades) if winning_trades else 0
        total_loss = sum(t['profit'] for t in losing_trades) if losing_trades else 0
        
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
        
        average_profit = total_profit / win_count if win_count > 0 else 0
        average_loss = total_loss / loss_count if loss_count > 0 else 0
        
        # Calculate drawdown
        if equity_curve:
            equity_values = [e['equity'] for e in equity_curve]
            peak = equity_values[0]
            max_drawdown = 0
            
            for equity in equity_values:
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak
                max_drawdown = max(max_drawdown, drawdown)
        else:
            max_drawdown = 0
        
        # Calculate Sharpe ratio (assuming risk-free rate = 0)
        if len(equity_curve) > 1:
            # Convert equity curve to returns
            equity_values = [e['equity'] for e in equity_curve]
            returns = [(equity_values[i] - equity_values[i-1]) / equity_values[i-1] for i in range(1, len(equity_values))]
            
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'average_profit': average_profit,
            'average_loss': average_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'return_percentage': ((final_balance - initial_balance) / initial_balance) * 100
        }
    
    def save_backtest_results(self, results, filename):
        """
        Save backtest results to a file.
        
        Args:
            results (dict): Backtest results
            filename (str): Filename to save results to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            joblib.dump(results, filename)
            return True
        except Exception as e:
            print(f"Error saving backtest results: {str(e)}")
            return False
    
    def load_backtest_results(self, filename):
        """
        Load backtest results from a file.
        
        Args:
            filename (str): Filename to load results from
            
        Returns:
            dict: Backtest results if successful, None otherwise
        """
        try:
            return joblib.load(filename)
        except Exception as e:
            print(f"Error loading backtest results: {str(e)}")
            return None

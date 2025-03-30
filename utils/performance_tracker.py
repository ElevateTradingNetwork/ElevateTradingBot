import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import os
import json

class PerformanceTracker:
    """
    Tracks and analyzes trading bot performance over time.
    """
    
    def __init__(self, data_file='performance_data.joblib'):
        """
        Initialize the performance tracker.
        
        Args:
            data_file (str): File to store performance data
        """
        self.data_file = data_file
        self.trades = []
        self.equity_curve = []
        self.initial_balance = 0
        self.current_balance = 0
        self.metrics = {}
        
        # Load existing data if available
        self.load_data()
    
    def load_data(self):
        """
        Load performance data from file.
        
        Returns:
            bool: True if data was loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.data_file):
                data = joblib.load(self.data_file)
                self.trades = data.get('trades', [])
                self.equity_curve = data.get('equity_curve', [])
                self.initial_balance = data.get('initial_balance', 0)
                self.current_balance = data.get('current_balance', 0)
                self.metrics = data.get('metrics', {})
                return True
            return False
        except Exception as e:
            print(f"Error loading performance data: {str(e)}")
            return False
    
    def save_data(self):
        """
        Save performance data to file.
        
        Returns:
            bool: True if data was saved successfully, False otherwise
        """
        try:
            data = {
                'trades': self.trades,
                'equity_curve': self.equity_curve,
                'initial_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'metrics': self.metrics
            }
            joblib.dump(data, self.data_file)
            return True
        except Exception as e:
            print(f"Error saving performance data: {str(e)}")
            return False
    
    def initialize_tracker(self, initial_balance):
        """
        Initialize tracker with starting balance.
        
        Args:
            initial_balance (float): Initial account balance
        """
        if not self.trades and not self.equity_curve:
            self.initial_balance = initial_balance
            self.current_balance = initial_balance
            self.equity_curve.append({
                'date': datetime.now(),
                'equity': initial_balance
            })
            self.save_data()
    
    def record_trade(self, trade_data):
        """
        Record a completed trade.
        
        Args:
            trade_data (dict): Trade information
        """
        # Ensure required fields are present
        required_fields = ['entry_date', 'exit_date', 'entry_price', 'exit_price', 
                          'type', 'size', 'profit', 'commission']
        
        if not all(field in trade_data for field in required_fields):
            print("Error: Missing required trade information")
            return False
        
        # Add trade to the list
        self.trades.append(trade_data)
        
        # Update current balance
        self.current_balance += trade_data['profit'] - trade_data['commission']
        
        # Update equity curve
        self.equity_curve.append({
            'date': datetime.now() if not isinstance(trade_data['exit_date'], datetime) else trade_data['exit_date'],
            'equity': self.current_balance
        })
        
        # Update metrics
        self.update_metrics()
        
        # Save data
        self.save_data()
        
        return True
    
    def update_metrics(self):
        """
        Update performance metrics based on recorded trades.
        """
        if not self.trades:
            self.metrics = {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'average_profit': 0,
                'average_loss': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'avg_holding_time': 0
            }
            return
        
        # Calculate basic metrics
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['profit'] > 0]
        losing_trades = [t for t in self.trades if t['profit'] <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = win_count / total_trades if total_trades > 0 else 0
        
        # Calculate profit metrics
        total_profit = sum(t['profit'] for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t['profit'] for t in losing_trades)) if losing_trades else 0
        
        profit_factor = total_profit / total_loss if total_loss != 0 else float('inf')
        
        average_profit = total_profit / win_count if win_count > 0 else 0
        average_loss = total_loss / loss_count if loss_count > 0 else 0
        
        # Calculate average holding time
        holding_times = []
        for trade in self.trades:
            entry_date = trade['entry_date']
            exit_date = trade['exit_date']
            
            # Convert to datetime if they're not already
            if not isinstance(entry_date, datetime):
                entry_date = pd.to_datetime(entry_date)
            if not isinstance(exit_date, datetime):
                exit_date = pd.to_datetime(exit_date)
            
            holding_time = (exit_date - entry_date).total_seconds() / 3600  # hours
            holding_times.append(holding_time)
        
        avg_holding_time = sum(holding_times) / len(holding_times) if holding_times else 0
        
        # Calculate drawdown
        if self.equity_curve:
            equity_values = [e['equity'] for e in self.equity_curve]
            peak = equity_values[0]
            max_drawdown = 0
            
            for equity in equity_values:
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak if peak > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
        else:
            max_drawdown = 0
        
        # Calculate Sharpe ratio (assuming risk-free rate = 0)
        if len(self.equity_curve) > 1:
            equity_values = [e['equity'] for e in self.equity_curve]
            returns = [(equity_values[i] - equity_values[i-1]) / equity_values[i-1] for i in range(1, len(equity_values))]
            
            mean_return = np.mean(returns) if returns else 0
            std_return = np.std(returns) if returns else 0
            
            sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Update metrics dictionary
        self.metrics = {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'average_profit': average_profit,
            'average_loss': average_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_profit': total_profit - total_loss,
            'total_profit_percent': ((self.current_balance - self.initial_balance) / self.initial_balance) * 100 if self.initial_balance > 0 else 0,
            'avg_holding_time': avg_holding_time
        }
    
    def get_recent_trades(self, n=10):
        """
        Get the most recent trades.
        
        Args:
            n (int): Number of trades to return
            
        Returns:
            list: Recent trades
        """
        if not self.trades:
            return []
        
        # Sort trades by exit date (most recent first)
        sorted_trades = sorted(self.trades, key=lambda x: x['exit_date'] if isinstance(x['exit_date'], datetime) else pd.to_datetime(x['exit_date']), reverse=True)
        
        return sorted_trades[:n]
    
    def get_metrics(self):
        """
        Get current performance metrics.
        
        Returns:
            dict: Performance metrics
        """
        return self.metrics
    
    def get_equity_curve(self):
        """
        Get equity curve data.
        
        Returns:
            list: Equity curve data
        """
        return self.equity_curve
    
    def get_trade_statistics_by_period(self, period='day'):
        """
        Get trade statistics aggregated by time period.
        
        Args:
            period (str): Time period ('day', 'week', 'month')
            
        Returns:
            pandas.DataFrame: Aggregated statistics
        """
        if not self.trades:
            return pd.DataFrame()
        
        # Convert trades to DataFrame
        df_trades = pd.DataFrame(self.trades)
        
        # Ensure exit_date is datetime
        df_trades['exit_date'] = pd.to_datetime(df_trades['exit_date'])
        
        # Set the period for grouping
        if period == 'day':
            df_trades['period'] = df_trades['exit_date'].dt.date
        elif period == 'week':
            df_trades['period'] = df_trades['exit_date'].dt.to_period('W').dt.start_time
        elif period == 'month':
            df_trades['period'] = df_trades['exit_date'].dt.to_period('M').dt.start_time
        else:
            df_trades['period'] = df_trades['exit_date'].dt.date
        
        # Group by period and calculate statistics
        stats = df_trades.groupby('period').agg({
            'profit': ['sum', 'mean', 'count'],
            'type': lambda x: x.value_counts().get('long', 0),  # Count of long trades
        })
        
        # Flatten column names
        stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
        
        # Rename columns
        stats = stats.rename(columns={
            'profit_sum': 'total_profit',
            'profit_mean': 'average_profit',
            'profit_count': 'trade_count',
            'type_<lambda>': 'long_count'
        })
        
        # Calculate short count
        stats['short_count'] = stats['trade_count'] - stats['long_count']
        
        # Calculate win rate per period
        def win_rate(group):
            wins = sum(1 for p in group if p > 0)
            return wins / len(group) if len(group) > 0 else 0
        
        win_rates = df_trades.groupby('period')['profit'].apply(win_rate)
        stats['win_rate'] = win_rates
        
        return stats
    
    def export_to_csv(self, filename='performance_export.csv'):
        """
        Export performance data to CSV.
        
        Args:
            filename (str): Output filename
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Export trades
            df_trades = pd.DataFrame(self.trades)
            df_trades.to_csv(filename, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
    
    def export_to_json(self, filename='performance_export.json'):
        """
        Export performance data to JSON.
        
        Args:
            filename (str): Output filename
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Prepare data for JSON export
            data = {
                'initial_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'metrics': self.metrics,
                'trades': self.trades,
                'equity_curve': self.equity_curve
            }
            
            # Convert datetime objects to strings
            data_str = json.dumps(data, default=str)
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(data_str)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False

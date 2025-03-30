import os
import sys
import time
from datetime import datetime, timedelta

# Try to import required packages, handle missing dependencies gracefully
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("Warning: plotly.graph_objects not found. Charts will not be available.")

    # Import custom modules
    # Use conditional imports to handle potential errors
    try:
        from utils.ai_assistant import TradingAssistant
        ai_assistant_available = True
    except ImportError:
        print("Warning: AI Assistant module not available.")
        ai_assistant_available = False
    
    # Store availability flags for other modules
    modules_available = {
        'api_client': False,
        'strategy': False,
        'backtester': False,
        'chart_utils': False,
        'pattern_recognition': False,
        'performance_tracker': False
    }
    
    try:
        from utils.api_client import BitgetClient
        modules_available['api_client'] = True
    except ImportError:
        print("Warning: BitgetClient module not available.")
    
    try:
        from utils.strategy import TradingStrategy
        modules_available['strategy'] = True
    except ImportError:
        print("Warning: TradingStrategy module not available.")
    
    try:
        from utils.backtester import Backtester
        modules_available['backtester'] = True
    except ImportError:
        print("Warning: Backtester module not available.")
    
    try:
        from utils.chart_utils import ChartUtils
        modules_available['chart_utils'] = True
    except ImportError:
        print("Warning: ChartUtils module not available.")
    
    try:
        from utils.pattern_recognition import PatternRecognition
        modules_available['pattern_recognition'] = True
    except ImportError:
        print("Warning: PatternRecognition module not available.")
    
    try:
        from utils.performance_tracker import PerformanceTracker
        modules_available['performance_tracker'] = True
    except ImportError:
        print("Warning: PerformanceTracker module not available.")
        
except ImportError as e:
    print(f"Critical import error: {str(e)}")
    print("Please install the required packages: streamlit, pandas, numpy")
    sys.exit(1)

# Page configuration
st.set_page_config(
    page_title="Crypto Trading Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'client' not in st.session_state:
    st.session_state.client = BitgetClient()
if 'strategy' not in st.session_state:
    st.session_state.strategy = TradingStrategy()
if 'backtester' not in st.session_state:
    st.session_state.backtester = Backtester()
if 'performance_tracker' not in st.session_state:
    st.session_state.performance_tracker = PerformanceTracker()
if 'ai_assistant' not in st.session_state:
    st.session_state.ai_assistant = TradingAssistant()
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = "BTC/USDT"
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = "1h"
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'liquidity_levels' not in st.session_state:
    st.session_state.liquidity_levels = []
if 'patterns' not in st.session_state:
    st.session_state.patterns = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now()
if 'trade_signals' not in st.session_state:
    st.session_state.trade_signals = []
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False

# Application title
st.title("Cryptocurrency Trading Bot")
st.markdown("**Break, Retest, and Liquidity Sweep Strategies with Bitget Integration**")

# Create sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Connection section
    st.subheader("API Connection")
    api_key = st.text_input("API Key", value=os.getenv('BITGET_API_KEY', ''), type="password")
    api_secret = st.text_input("API Secret", value=os.getenv('BITGET_API_SECRET', ''), type="password")
    api_password = st.text_input("API Password", value=os.getenv('BITGET_API_PASSWORD', ''), type="password")
    
    # Set environment variables with API details
    os.environ['BITGET_API_KEY'] = api_key
    os.environ['BITGET_API_SECRET'] = api_secret
    os.environ['BITGET_API_PASSWORD'] = api_password
    
    if st.button("Connect to Bitget"):
        with st.spinner("Connecting to Bitget..."):
            client = BitgetClient()
            connection_success = client.connect()
            
            if connection_success:
                st.session_state.client = client
                st.session_state.api_connected = True
                st.success("Connected to Bitget successfully!")
            else:
                st.error("Failed to connect to Bitget. Please check your API credentials.")
    
    # Display connection status
    if st.session_state.api_connected:
        st.success("Connected to Bitget")
    else:
        st.warning("Not connected to Bitget")
    
    # Trading parameters section
    st.subheader("Trading Parameters")
    
    # Symbol selection
    if st.session_state.api_connected:
        available_markets = st.session_state.client.get_markets()
        default_idx = available_markets.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in available_markets else 0
        selected_symbol = st.selectbox("Trading Pair", available_markets, index=default_idx)
    else:
        selected_symbol = st.selectbox("Trading Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"])
    
    # Timeframe selection
    timeframe = st.selectbox(
        "Timeframe",
        ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        index=["1m", "5m", "15m", "30m", "1h", "4h", "1d"].index(st.session_state.timeframe)
    )
    
    # Update session state if selections changed
    if selected_symbol != st.session_state.selected_symbol or timeframe != st.session_state.timeframe:
        st.session_state.selected_symbol = selected_symbol
        st.session_state.timeframe = timeframe
        st.session_state.data = pd.DataFrame()  # Clear data to force refresh
    
    # Strategy parameters
    st.subheader("Strategy Parameters")
    risk_percentage = st.slider("Risk Percentage per Trade (%)", 0.1, 5.0, 1.0, 0.1)
    max_open_trades = st.slider("Maximum Open Trades", 1, 10, 3, 1)
    
    # Update strategy with new parameters
    if risk_percentage != st.session_state.strategy.risk_percentage or max_open_trades != st.session_state.strategy.max_open_trades:
        st.session_state.strategy = TradingStrategy(risk_percentage, max_open_trades)
    
    # Auto-refresh option
    st.subheader("Auto Refresh")
    auto_refresh = st.checkbox("Enable Auto Refresh", value=st.session_state.auto_refresh)
    
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
    
    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (seconds)", 30, 300, 60, 10)

# Function to fetch and analyze data
def fetch_and_analyze_data():
    if not st.session_state.api_connected:
        st.warning("Please connect to Bitget API first")
        return
    
    # Fetch OHLCV data
    with st.spinner(f"Fetching {st.session_state.selected_symbol} data for {st.session_state.timeframe} timeframe..."):
        df = st.session_state.client.fetch_ohlcv(
            st.session_state.selected_symbol, 
            st.session_state.timeframe,
            limit=500
        )
        
        if df.empty:
            st.error(f"Failed to fetch data for {st.session_state.selected_symbol}")
            return
        
        st.session_state.data = df
        
        # Calculate liquidity levels
        st.session_state.liquidity_levels = st.session_state.client.calculate_high_liquidity_levels(
            st.session_state.selected_symbol,
            st.session_state.timeframe
        )
        
        # Calculate indicators
        with st.spinner("Calculating technical indicators..."):
            analysis_df = st.session_state.strategy.calculate_indicators(df)
            
            # Identify patterns
            candlestick_patterns = PatternRecognition.identify_candlestick_patterns(analysis_df)
            breakout_patterns = PatternRecognition.identify_break_retest_patterns(analysis_df)
            liquidity_sweep_patterns = PatternRecognition.identify_liquidity_sweeps(
                analysis_df, 
                st.session_state.liquidity_levels
            )
            
            # Combine all patterns
            all_patterns = candlestick_patterns + breakout_patterns + liquidity_sweep_patterns
            
            # Calculate pattern probabilities
            patterns_with_probability = PatternRecognition.calculate_pattern_probability(all_patterns)
            
            # Sort by recency (most recent first)
            patterns_with_probability.sort(key=lambda x: x['timestamp'] if 'timestamp' in x else x.get('date', 0), reverse=True)
            
            st.session_state.patterns = patterns_with_probability
            
            # Generate trade signals
            signal = st.session_state.strategy.generate_trade_signal(
                analysis_df, 
                st.session_state.liquidity_levels
            )
            
            if signal:
                st.session_state.trade_signals.append(signal)
                # Keep only the 10 most recent signals
                if len(st.session_state.trade_signals) > 10:
                    st.session_state.trade_signals = st.session_state.trade_signals[-10:]
        
        st.session_state.analysis_results = {
            'analysis_df': analysis_df,
            'last_refresh': datetime.now()
        }
        
        st.session_state.last_refresh_time = datetime.now()

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Market Analysis", 
    "Trading Signals", 
    "Backtesting", 
    "Performance", 
    "AI Assistant"
])

# Tab 1: Market Analysis
with tab1:
    st.header("Market Analysis")
    
    # Buttons for data refresh and analysis
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Refresh Data"):
            fetch_and_analyze_data()
    
    with col2:
        if st.button("Clear Cache"):
            st.session_state.data = pd.DataFrame()
            st.session_state.analysis_results = {}
            st.session_state.patterns = []
            st.session_state.liquidity_levels = []
            st.rerun()
    
    with col3:
        # Show last refresh time
        if 'last_refresh_time' in st.session_state:
            st.info(f"Last refreshed: {st.session_state.last_refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if auto-refresh is enabled
    if st.session_state.auto_refresh:
        # Calculate time since last refresh
        time_since_refresh = (datetime.now() - st.session_state.last_refresh_time).total_seconds()
        
        # If it's time to refresh based on the interval
        if time_since_refresh > refresh_interval:
            fetch_and_analyze_data()
    
    # Display chart if data is available
    if not st.session_state.data.empty and 'analysis_results' in st.session_state and st.session_state.analysis_results:
        analysis_df = st.session_state.analysis_results['analysis_df']
        
        # Create price chart
        fig = ChartUtils.create_candlestick_chart(
            analysis_df,
            title=f"{st.session_state.selected_symbol} - {st.session_state.timeframe}",
            patterns=st.session_state.patterns,
            liquidity_levels=st.session_state.liquidity_levels
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display identified patterns
        if st.session_state.patterns:
            st.subheader("Identified Patterns")
            
            # Create a dataframe for better display
            patterns_df = pd.DataFrame([
                {
                    'Type': p['type'],
                    'Subtype': p.get('subtype', ''),
                    'Price': p['price'],
                    'Timestamp': p['timestamp'] if 'timestamp' in p else p.get('date', ''),
                    'Strength': p.get('strength', 0),
                    'Probability': f"{p.get('probability', 0)*100:.1f}%"
                } for p in st.session_state.patterns[:10]  # Show top 10 most recent
            ])
            
            st.dataframe(patterns_df, use_container_width=True)
        else:
            st.info("No patterns identified in the current timeframe.")
        
        # Display liquidity levels
        if st.session_state.liquidity_levels:
            st.subheader("Liquidity Levels")
            
            # Create a dataframe for better display
            liquidity_df = pd.DataFrame([
                {
                    'Price': level['price'],
                    'Volume': level['volume'],
                    'Timestamp': level['timestamp'],
                    'Strength': level['strength']
                } for level in st.session_state.liquidity_levels[:5]  # Show top 5
            ])
            
            st.dataframe(liquidity_df, use_container_width=True)
        else:
            st.info("No significant liquidity levels identified.")
    else:
        st.info("Click 'Refresh Data' to fetch and analyze market data.")

# Tab 2: Trading Signals
with tab2:
    st.header("Trading Signals")
    
    # Display current active signals
    if st.session_state.trade_signals:
        # Get the most recent signal
        latest_signal = st.session_state.trade_signals[-1]
        
        # Create a metrics display for the latest signal
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Signal", 
                f"{latest_signal['signal'].upper()} {latest_signal['type']}",
                delta=f"R:R {latest_signal['risk_reward']:.2f}"
            )
        
        with col2:
            st.metric(
                "Entry Price", 
                f"{latest_signal['price']:.2f}",
                delta=f"Position Size: {latest_signal['position_size']:.4f}"
            )
        
        with col3:
            st.metric(
                "Stop Loss", 
                f"{latest_signal['stop_loss']:.2f}",
                delta=f"Take Profit: {latest_signal['take_profit']:.2f}"
            )
        
        # Display a table of recent signals
        st.subheader("Recent Signals")
        
        signals_df = pd.DataFrame([
            {
                'Date': s['date'],
                'Type': s['type'],
                'Signal': s['signal'].upper(),
                'Price': f"{s['price']:.2f}",
                'Stop Loss': f"{s['stop_loss']:.2f}",
                'Take Profit': f"{s['take_profit']:.2f}",
                'Risk-Reward': f"{s['risk_reward']:.2f}"
            } for s in st.session_state.trade_signals
        ])
        
        st.dataframe(signals_df, use_container_width=True)
        
        # Manual trade execution section
        st.subheader("Manual Trade Execution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Execute Latest Signal"):
                if st.session_state.api_connected:
                    with st.spinner("Executing trade..."):
                        # This would be connected to actual trading execution
                        # For safety, we'll just show a success message here
                        st.success("Trade executed successfully! (Simulated)")
                else:
                    st.error("Cannot execute trade: Not connected to Bitget API")
        
        with col2:
            if st.button("Cancel All Orders"):
                if st.session_state.api_connected:
                    with st.spinner("Cancelling orders..."):
                        # This would cancel all open orders
                        st.success("All orders cancelled successfully! (Simulated)")
                else:
                    st.error("Cannot cancel orders: Not connected to Bitget API")
    else:
        st.info("No trading signals generated yet. Refresh market data in the Analysis tab to generate signals.")
    
    # Current positions and orders
    st.subheader("Current Positions")
    
    if st.session_state.api_connected:
        with st.spinner("Fetching current positions..."):
            # This would fetch actual positions
            # For demonstration, show sample positions
            st.info("No open positions (simulated)")
    else:
        st.warning("Connect to Bitget API to view your current positions")
    
    st.subheader("Open Orders")
    
    if st.session_state.api_connected:
        with st.spinner("Fetching open orders..."):
            # This would fetch actual open orders
            # For demonstration, show sample orders
            st.info("No open orders (simulated)")
    else:
        st.warning("Connect to Bitget API to view your open orders")

# Tab 3: Backtesting
with tab3:
    st.header("Strategy Backtesting")
    
    # Backtesting parameters
    st.subheader("Backtesting Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backtest_symbol = st.selectbox(
            "Symbol for Backtesting",
            ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"],
            index=0
        )
    
    with col2:
        backtest_timeframe = st.selectbox(
            "Timeframe for Backtesting",
            ["15m", "30m", "1h", "4h", "1d"],
            index=2
        )
    
    with col3:
        backtest_period = st.selectbox(
            "Backtesting Period",
            ["7 days", "14 days", "30 days", "60 days", "90 days"],
            index=2
        )
    
    # Initial balance for backtesting
    initial_balance = st.number_input("Initial Balance (USDT)", min_value=100.0, value=10000.0, step=1000.0)
    
    # Start backtest button
    if st.button("Run Backtest"):
        if st.session_state.api_connected:
            with st.spinner("Running backtest, please wait..."):
                # Calculate date range for backtest
                days_map = {
                    "7 days": 7,
                    "14 days": 14,
                    "30 days": 30,
                    "60 days": 60,
                    "90 days": 90
                }
                days = days_map[backtest_period]
                
                # Fetch historical data for backtest
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Get data for backtesting
                backtest_data = st.session_state.client.fetch_ohlcv(
                    backtest_symbol,
                    backtest_timeframe,
                    limit=500  # Adjust based on timeframe to cover the period
                )
                
                if backtest_data.empty:
                    st.error(f"Failed to fetch backtest data for {backtest_symbol}")
                else:
                    # Calculate liquidity levels for backtest
                    liquidity_levels = st.session_state.client.calculate_high_liquidity_levels(
                        backtest_symbol,
                        backtest_timeframe
                    )
                    
                    # Run backtest
                    backtest_results = st.session_state.backtester.run_backtest(
                        backtest_data, 
                        liquidity_levels
                    )
                    
                    # Store results
                    st.session_state.backtest_results = backtest_results
                    
                    # Display success message
                    st.success("Backtest completed successfully!")
        else:
            st.error("Please connect to Bitget API first to run a backtest")
    
    # Display backtest results if available
    if st.session_state.backtest_results:
        results = st.session_state.backtest_results
        
        # Results summary
        st.subheader("Backtest Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            profit_loss = results['profit_loss']
            profit_loss_percent = results['profit_loss_percent']
            delta_color = "normal" if profit_loss >= 0 else "inverse"
            st.metric(
                "Profit/Loss", 
                f"${profit_loss:.2f}", 
                delta=f"{profit_loss_percent:.2f}%",
                delta_color=delta_color
            )
        
        with col2:
            win_rate = results['metrics']['win_rate'] * 100
            st.metric("Win Rate", f"{win_rate:.2f}%")
        
        with col3:
            profit_factor = results['metrics']['profit_factor']
            st.metric("Profit Factor", f"{profit_factor:.2f}")
        
        with col4:
            max_drawdown = results['metrics']['max_drawdown'] * 100
            st.metric("Max Drawdown", f"{max_drawdown:.2f}%", delta_color="inverse")
        
        # Performance chart
        st.subheader("Equity Curve")
        
        equity_chart = ChartUtils.create_performance_chart(
            results['equity_curve'],
            results['trades'],
            title=f"Backtest Performance: {backtest_symbol} {backtest_timeframe}"
        )
        
        st.plotly_chart(equity_chart, use_container_width=True)
        
        # Trade details
        st.subheader("Trade Details")
        
        if results['trades']:
            trades_df = pd.DataFrame([
                {
                    'Entry Date': t['entry_date'],
                    'Exit Date': t['exit_date'],
                    'Type': t['type'].capitalize(),
                    'Entry Price': f"{t['entry_price']:.2f}",
                    'Exit Price': f"{t['exit_price']:.2f}",
                    'Profit/Loss': f"{t['profit']:.2f}",
                    'Result': t['result'].replace('_', ' ').title()
                } for t in results['trades']
            ])
            
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("No trades were executed during the backtest period.")
        
        # Save backtest results
        if st.button("Save Backtest Results"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_{backtest_symbol.replace('/', '')}_{backtest_timeframe}_{timestamp}.joblib"
            
            if st.session_state.backtester.save_backtest_results(results, filename):
                st.success(f"Backtest results saved to {filename}")
            else:
                st.error("Failed to save backtest results")
    else:
        st.info("Run a backtest to see results here.")

# Tab 4: Performance
with tab4:
    st.header("Trading Performance")
    
    # Initialize performance tracker if needed
    if st.button("Initialize Performance Tracker"):
        starting_balance = st.session_state.performance_tracker.initial_balance
        if starting_balance == 0:
            st.session_state.performance_tracker.initialize_tracker(10000)  # Default starting balance
            st.success("Performance tracker initialized with 10,000 USDT balance")
        else:
            st.info(f"Performance tracker already initialized with {starting_balance} USDT balance")
    
    # Get current performance metrics
    metrics = st.session_state.performance_tracker.get_metrics()
    
    if metrics:
        # Display key performance metrics
        st.subheader("Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_profit_percent = metrics.get('total_profit_percent', 0)
            delta_color = "normal" if total_profit_percent >= 0 else "inverse"
            st.metric(
                "Total Return", 
                f"{total_profit_percent:.2f}%", 
                delta=f"${metrics.get('total_profit', 0):.2f}",
                delta_color=delta_color
            )
        
        with col2:
            win_rate = metrics.get('win_rate', 0) * 100
            st.metric("Win Rate", f"{win_rate:.2f}%")
        
        with col3:
            profit_factor = metrics.get('profit_factor', 0)
            st.metric("Profit Factor", f"{profit_factor:.2f}")
        
        with col4:
            max_drawdown = metrics.get('max_drawdown', 0) * 100
            st.metric("Max Drawdown", f"{max_drawdown:.2f}%", delta_color="inverse")
        
        # Get equity curve and trades
        equity_curve = st.session_state.performance_tracker.get_equity_curve()
        recent_trades = st.session_state.performance_tracker.get_recent_trades()
        
        # Display equity curve chart
        if equity_curve:
            st.subheader("Equity Curve")
            
            equity_chart = ChartUtils.create_performance_chart(
                equity_curve,
                recent_trades,
                title="Trading Performance"
            )
            
            st.plotly_chart(equity_chart, use_container_width=True)
        
        # Display recent trades
        if recent_trades:
            st.subheader("Recent Trades")
            
            trades_df = pd.DataFrame([
                {
                    'Entry Date': t['entry_date'],
                    'Exit Date': t['exit_date'],
                    'Type': t['type'].capitalize(),
                    'Entry Price': f"{t['entry_price']:.2f}",
                    'Exit Price': f"{t['exit_price']:.2f}",
                    'Profit/Loss': f"{t['profit']:.2f}",
                    'Result': t.get('result', '').replace('_', ' ').title()
                } for t in recent_trades
            ])
            
            st.dataframe(trades_df, use_container_width=True)
        
        # Trade statistics by period
        st.subheader("Performance by Period")
        
        period_type = st.selectbox("Aggregation Period", ["day", "week", "month"], index=1)
        
        period_stats = st.session_state.performance_tracker.get_trade_statistics_by_period(period_type)
        
        if not period_stats.empty:
            st.dataframe(period_stats, use_container_width=True)
        else:
            st.info("No trade statistics available for the selected period.")
        
        # Export options
        st.subheader("Export Performance Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to CSV"):
                if st.session_state.performance_tracker.export_to_csv():
                    st.success("Performance data exported to CSV successfully")
                else:
                    st.error("Failed to export performance data")
        
        with col2:
            if st.button("Export to JSON"):
                if st.session_state.performance_tracker.export_to_json():
                    st.success("Performance data exported to JSON successfully")
                else:
                    st.error("Failed to export performance data")
    else:
        st.info("No performance data available. Initialize the performance tracker to start recording trades.")
        
        # For demonstration purposes, add sample trade button
        if st.button("Add Sample Trade (Demo)"):
            sample_trade = {
                'entry_date': datetime.now() - timedelta(days=1),
                'exit_date': datetime.now(),
                'entry_price': 50000,
                'exit_price': 51000,
                'type': 'long',
                'size': 0.1,
                'profit': 100,
                'commission': 5,
                'result': 'take_profit'
            }
            
            if st.session_state.performance_tracker.record_trade(sample_trade):
                st.success("Sample trade recorded successfully")
                st.rerun()
            else:
                st.error("Failed to record sample trade")

# Tab 5: AI Assistant
with tab5:
    st.header("Trading Assistant")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
        openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
        
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            st.session_state.ai_assistant = TradingAssistant()
            st.success("OpenAI API key set successfully!")
    
    # Main AI assistant section
    st.subheader("Ask a Question")
    
    user_question = st.text_area("Enter your trading question:", height=100)
    
    if st.button("Ask Assistant"):
        if user_question:
            with st.spinner("Thinking..."):
                # Get trading history and patterns for context
                trading_history = {
                    'metrics': st.session_state.performance_tracker.get_metrics(),
                    'trades': st.session_state.performance_tracker.get_recent_trades()
                }
                
                # Get AI response
                response = st.session_state.ai_assistant.ask_question(
                    user_question,
                    trading_history,
                    st.session_state.patterns
                )
                
                # Display response in a nice box
                st.markdown("### Response:")
                st.markdown(f"<div style='background-color:#f0f2f6;padding:20px;border-radius:5px'>{response}</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter a question first.")
    
    # Pattern analysis section
    st.subheader("Pattern Analysis")
    
    # Only show if patterns are available
    if st.session_state.patterns:
        selected_pattern_index = st.selectbox(
            "Select Pattern to Analyze:",
            range(len(st.session_state.patterns)),
            format_func=lambda i: f"{st.session_state.patterns[i]['type']} at {st.session_state.patterns[i]['price']:.2f}"
        )
        
        if st.button("Analyze Pattern"):
            with st.spinner("Analyzing pattern..."):
                selected_pattern = st.session_state.patterns[selected_pattern_index]
                
                # Get AI analysis of the pattern
                analysis = st.session_state.ai_assistant.analyze_pattern(selected_pattern)
                
                # Display analysis
                st.markdown("### Pattern Analysis:")
                st.markdown(f"<div style='background-color:#f0f2f6;padding:20px;border-radius:5px'>{analysis}</div>", unsafe_allow_html=True)
    else:
        st.info("No patterns available for analysis. Refresh market data in the Analysis tab to identify patterns.")
    
    # Trading plan evaluation
    st.subheader("Evaluate Trading Plan")
    
    if st.button("Evaluate Current Strategy"):
        with st.spinner("Evaluating strategy..."):
            # Get current strategy settings
            strategy_settings = {
                'risk_percentage': st.session_state.strategy.risk_percentage,
                'max_open_trades': st.session_state.strategy.max_open_trades
            }
            
            # Get current performance metrics
            performance_metrics = st.session_state.performance_tracker.get_metrics()
            
            # If no actual metrics, use backtest results if available
            if not performance_metrics and st.session_state.backtest_results:
                performance_metrics = st.session_state.backtest_results['metrics']
            
            # Get AI evaluation
            if performance_metrics:
                evaluation = st.session_state.ai_assistant.evaluate_trading_plan(
                    strategy_settings,
                    performance_metrics
                )
                
                # Display evaluation
                st.markdown("### Strategy Evaluation:")
                st.markdown(f"<div style='background-color:#f0f2f6;padding:20px;border-radius:5px'>{evaluation}</div>", unsafe_allow_html=True)
            else:
                st.warning("No performance data available for evaluation. Run a backtest or record some trades first.")

# Footer
st.markdown("---")
st.markdown("### Risk Disclaimer")
st.markdown("""
This trading bot is for educational and informational purposes only. Cryptocurrency trading involves significant risk and can result in the loss of your invested capital. 
Always conduct your own research before making any trading decisions. Past performance is not indicative of future results.
""")

# Check for auto-refresh
if st.session_state.auto_refresh:
    time.sleep(1)
    st.rerun()

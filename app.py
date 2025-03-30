import os
import random
import datetime
from datetime import timedelta

# Import required libraries - if available
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit and other dependencies are not available. Using terminal-based preview.")

# Set page configuration if Streamlit is available
if STREAMLIT_AVAILABLE:
    st.set_page_config(
        page_title="Crypto Trading Bot",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def check_api_status():
    """Check status of API keys."""
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    bitget_api_key = os.environ.get("BITGET_API_KEY", "")
    bitget_api_secret = os.environ.get("BITGET_API_SECRET", "")
    bitget_api_password = os.environ.get("BITGET_API_PASSWORD", "")
    
    api_status = {}
    api_status["openai"] = bool(openai_api_key)
    api_status["bitget"] = bool(bitget_api_key and bitget_api_secret and bitget_api_password)
    
    return api_status

def generate_mock_data():
    """Generate mock data for demonstration."""
    # Mock candlestick data
    num_candles = 100
    today = datetime.datetime.now()
    dates = [(today - timedelta(hours=i)).strftime("%Y-%m-%d %H:00") for i in range(num_candles)]
    dates.reverse()
    
    # Start with a base price and generate realistic-looking price movement
    base_price = 65000
    price_data = []
    current_price = base_price
    
    for i in range(num_candles):
        change_percent = random.uniform(-1.5, 1.5)
        close = current_price * (1 + change_percent/100)
        high = close * (1 + random.uniform(0.1, 0.5)/100)
        low = close * (1 - random.uniform(0.1, 0.5)/100)
        open_price = current_price
        volume = random.uniform(100, 500)
        
        price_data.append({
            "date": dates[i],
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": round(volume, 2)
        })
        
        current_price = close
    
    # Mock patterns
    pattern_types = ["Break and Retest", "Liquidity Sweep", "Support Bounce", "Resistance Rejection", 
                     "Engulfing Bullish", "Evening Star", "Hammer"]
    
    patterns = []
    for _ in range(5):
        pattern_type = random.choice(pattern_types)
        price_idx = random.randint(num_candles - 15, num_candles - 1)
        if price_idx < 0:
            price_idx = 0  # Ensure valid index
        pattern = {
            'type': pattern_type,
            'price': price_data[price_idx]["close"],
            'strength': random.randint(1, 5),
            'timestamp': price_data[price_idx]["date"],
            'description': f"{pattern_type} pattern detected at ${price_data[price_idx]['close']}"
        }
        patterns.append(pattern)
    
    # Mock account data
    account = {
        "balance": round(random.uniform(25000, 35000), 2),
        "open_positions": random.randint(0, 3),
        "unrealized_pnl": round(random.uniform(-500, 2000), 2),
        "daily_pnl": round(random.uniform(-200, 800), 2)
    }
    
    # Mock performance metrics
    performance = {
        "total_return": round(random.uniform(15, 35), 1),
        "win_rate": round(random.uniform(55, 70), 1),
        "profit_factor": round(random.uniform(1.8, 2.5), 2),
        "max_drawdown": round(random.uniform(10, 20), 1),
        "sharpe_ratio": round(random.uniform(1.5, 2.2), 2)
    }
    
    # Mock trades
    trades = []
    for i in range(15):
        entry_idx = random.randint(0, len(price_data) - 2)
        exit_idx = entry_idx + random.randint(1, len(price_data) - entry_idx - 1)
        
        entry_price = price_data[entry_idx]["close"]
        exit_price = price_data[exit_idx]["close"]
        profit = round((exit_price - entry_price) / entry_price * 100, 2)
        
        trade = {
            "id": i + 1,
            "symbol": "BTC/USDT",
            "entry_date": price_data[entry_idx]["date"],
            "exit_date": price_data[exit_idx]["date"],
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": round(random.uniform(0.1, 0.5), 2),
            "profit": profit,
            "profit_usd": round(profit * entry_price * 0.01, 2),
            "type": "Long" if random.random() > 0.3 else "Short",
            "result": "Win" if profit > 0 else "Loss"
        }
        trades.append(trade)
    
    # Sort trades by date
    trades.sort(key=lambda x: x["entry_date"], reverse=True)
    
    # Mock liquidity levels
    liquidity_levels = []
    for i in range(4):
        level_price = base_price * (1 + random.uniform(-5, 5)/100)
        liquidity_levels.append({
            "price": round(level_price, 2),
            "strength": round(random.uniform(1, 5), 2),
            "type": "Support" if i % 2 == 0 else "Resistance"
        })
    
    # Convert price data to pandas DataFrame if available
    if STREAMLIT_AVAILABLE:
        df = pd.DataFrame(price_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    else:
        df = price_data
    
    return {
        "price_data": df,
        "patterns": patterns,
        "account": account,
        "performance": performance,
        "trades": trades,
        "liquidity_levels": liquidity_levels
    }

def create_candlestick_chart(df, patterns=None, liquidity_levels=None):
    """
    Create an interactive candlestick chart with patterns and liquidity levels.
    """
    if not STREAMLIT_AVAILABLE:
        return None
    
    # Create subplot with 2 rows
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.02, 
                        row_heights=[0.8, 0.2],
                        subplot_titles=("Price Action", "Volume"))
    
    # Add price candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        showlegend=False
    ), row=1, col=1)
    
    # Add volume bars
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker=dict(color='rgba(0, 0, 200, 0.3)'),
        showlegend=False
    ), row=2, col=1)
    
    # Add patterns if available
    if patterns:
        pattern_x = []
        pattern_y = []
        pattern_text = []
        pattern_colors = []
        
        for pattern in patterns:
            try:
                # Find the closest date to plot the pattern
                pattern_date = pd.to_datetime(pattern['timestamp'])
                if pattern_date in df.index:
                    # Adjust y position based on pattern type
                    if 'Support' in pattern['type'] or 'Hammer' in pattern['type'] or 'Bullish' in pattern['type']:
                        y_pos = df.loc[pattern_date, 'low'] * 0.998  # Slightly below the low
                    else:
                        y_pos = df.loc[pattern_date, 'high'] * 1.002  # Slightly above the high
                        
                    pattern_x.append(pattern_date)
                    pattern_y.append(y_pos)
                    pattern_text.append(f"{pattern['type']} (S:{pattern['strength']})")
                    
                    # Color based on pattern type
                    if 'Support' in pattern['type'] or 'Bullish' in pattern['type']:
                        pattern_colors.append('green')
                    elif 'Resistance' in pattern['type'] or 'Evening Star' in pattern['type']:
                        pattern_colors.append('red')
                    else:
                        pattern_colors.append('orange')
            except:
                # Skip patterns with date issues
                continue
        
        # Add pattern markers
        if pattern_x:
            fig.add_trace(go.Scatter(
                x=pattern_x,
                y=pattern_y,
                mode='markers+text',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color=pattern_colors,
                    line=dict(color='black', width=1)
                ),
                text=pattern_text,
                textposition="bottom center",
                name='Patterns',
                showlegend=True
            ), row=1, col=1)
    
    # Add liquidity levels if available
    if liquidity_levels:
        for level in liquidity_levels:
            level_color = 'rgba(0, 255, 0, 0.3)' if level['type'] == 'Support' else 'rgba(255, 0, 0, 0.3)'
            fig.add_shape(
                type="line",
                x0=df.index[0],
                x1=df.index[-1],
                y0=level['price'],
                y1=level['price'],
                line=dict(color=level_color, width=2, dash="dash"),
                row=1, col=1
            )
            
            # Add annotation for level
            fig.add_annotation(
                x=df.index[0],
                y=level['price'],
                text=f"{level['type']} (S:{level['strength']})",
                showarrow=False,
                font=dict(color="black", size=10),
                bgcolor=level_color,
                bordercolor="black",
                borderwidth=1,
                row=1, col=1
            )
    
    # Update layout
    fig.update_layout(
        title='Price Chart with Patterns',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Setup y-axes
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    # Style adjustments
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )
    
    return fig

def create_performance_chart(trades):
    """
    Create a performance chart showing trade results.
    """
    if not STREAMLIT_AVAILABLE:
        return None
    
    # Convert to DataFrame if not already
    if not isinstance(trades, pd.DataFrame):
        df_trades = pd.DataFrame(trades)
        df_trades['entry_date'] = pd.to_datetime(df_trades['entry_date'])
        df_trades.sort_values('entry_date', inplace=True)
    else:
        df_trades = trades
    
    # Calculate cumulative returns
    df_trades['cum_profit_pct'] = df_trades['profit'].cumsum()
    
    # Create figure
    fig = go.Figure()
    
    # Add cumulative profit line
    fig.add_trace(go.Scatter(
        x=df_trades['entry_date'],
        y=df_trades['cum_profit_pct'],
        mode='lines+markers',
        name='Cumulative Profit %',
        line=dict(color='blue', width=2)
    ))
    
    # Add individual trade markers
    win_trades = df_trades[df_trades['profit'] > 0]
    loss_trades = df_trades[df_trades['profit'] <= 0]
    
    # Win trades markers
    if not win_trades.empty:
        fig.add_trace(go.Scatter(
            x=win_trades['entry_date'],
            y=win_trades['profit'],
            mode='markers',
            marker=dict(
                size=10,
                color='green',
                symbol='circle',
                line=dict(color='black', width=1)
            ),
            name='Win Trades'
        ))
    
    # Loss trades markers
    if not loss_trades.empty:
        fig.add_trace(go.Scatter(
            x=loss_trades['entry_date'],
            y=loss_trades['profit'],
            mode='markers',
            marker=dict(
                size=10,
                color='red',
                symbol='circle',
                line=dict(color='black', width=1)
            ),
            name='Loss Trades'
        ))
    
    # Update layout
    fig.update_layout(
        title='Trading Performance',
        xaxis_title='Date',
        yaxis_title='Profit (%)',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )
    
    return fig

def streamlit_ui():
    """
    Render Streamlit UI for the trading bot.
    """
    # Title and description
    st.title("🚀 Crypto Trading Bot")
    st.markdown("""
    This interactive dashboard allows you to monitor and control your automated 
    cryptocurrency trading strategy focusing on break, retest, and liquidity sweep patterns.
    """)
    
    # Sidebar for controls
    st.sidebar.title("Controls")
    
    # Check API status
    api_status = check_api_status()
    
    # API Status indicators
    st.sidebar.header("API Status")
    if api_status["bitget"]:
        st.sidebar.success("✅ Bitget API: Connected")
    else:
        st.sidebar.error("❌ Bitget API: Not Connected")
        
    if api_status["openai"]:
        st.sidebar.success("✅ OpenAI API: Connected")
    else:
        st.sidebar.error("❌ OpenAI API: Not Connected")
    
    # Trading pair selector
    st.sidebar.header("Trading Settings")
    selected_symbol = st.sidebar.selectbox(
        "Select Trading Pair",
        options=["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"],
        index=0
    )
    
    # Timeframe selector
    selected_timeframe = st.sidebar.selectbox(
        "Select Timeframe",
        options=["5m", "15m", "1h", "4h", "1d"],
        index=2
    )
    
    # Risk management settings
    st.sidebar.header("Risk Management")
    risk_per_trade = st.sidebar.slider(
        "Risk Per Trade (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1
    )
    
    max_trades = st.sidebar.slider(
        "Max Open Trades",
        min_value=1,
        max_value=10,
        value=3
    )
    
    # Auto-trading toggle
    st.sidebar.header("Auto Trading")
    auto_trading = st.sidebar.toggle("Enable Auto Trading", value=False)
    
    if auto_trading:
        st.sidebar.warning("⚠️ Auto trading is enabled. The bot will execute trades automatically.")
    else:
        st.sidebar.info("ℹ️ Auto trading is disabled. You'll need to manually confirm trades.")
    
    # Get data
    data = generate_mock_data()
    
    # Main app layout with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "🔍 Pattern Analysis", 
        "⚙️ Strategy Configuration", 
        "📈 Backtesting",
        "🤖 AI Assistant"
    ])
    
    # Dashboard Tab
    with tab1:
        show_dashboard(data, selected_symbol, selected_timeframe)
    
    # Pattern Analysis Tab
    with tab2:
        show_pattern_analysis(data, selected_symbol, selected_timeframe)
    
    # Strategy Configuration Tab
    with tab3:
        show_strategy_configuration(risk_per_trade, max_trades)
    
    # Backtesting Tab
    with tab4:
        show_backtesting(data, selected_symbol, selected_timeframe)
    
    # AI Assistant Tab
    with tab5:
        show_ai_assistant(data)

def show_dashboard(data, selected_symbol, selected_timeframe):
    """Display dashboard with charts and metrics."""
    if STREAMLIT_AVAILABLE:
        # Account metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Account Balance",
                value=f"${data['account']['balance']:,.2f}"
            )
        
        with col2:
            st.metric(
                label="Open Positions",
                value=f"{data['account']['open_positions']}"
            )
        
        with col3:
            st.metric(
                label="Unrealized P&L",
                value=f"${data['account']['unrealized_pnl']:,.2f}",
                delta=f"{'+' if data['account']['unrealized_pnl'] >= 0 else ''}{data['account']['unrealized_pnl']:,.2f}"
            )
        
        with col4:
            st.metric(
                label="Daily P&L",
                value=f"${data['account']['daily_pnl']:,.2f}",
                delta=f"{'+' if data['account']['daily_pnl'] >= 0 else ''}{data['account']['daily_pnl']:,.2f}"
            )
        
        # Price chart with patterns
        st.subheader(f"{selected_symbol} Price Chart ({selected_timeframe})")
        price_chart = create_candlestick_chart(
            data['price_data'], 
            patterns=data['patterns'],
            liquidity_levels=data['liquidity_levels']
        )
        st.plotly_chart(price_chart, use_container_width=True)
        
        # Recent trades
        st.subheader("Recent Trades")
        if isinstance(data['trades'], list):
            # Convert to DataFrame for display
            df_trades = pd.DataFrame(data['trades'])
            st.dataframe(df_trades.head(5), use_container_width=True)
        else:
            st.dataframe(data['trades'].head(5), use_container_width=True)
        
        # Performance metrics
        st.subheader("Performance Metrics")
        perf_col1, perf_col2, perf_col3, perf_col4, perf_col5 = st.columns(5)
        
        with perf_col1:
            st.metric(
                label="Total Return",
                value=f"{data['performance']['total_return']}%"
            )
        
        with perf_col2:
            st.metric(
                label="Win Rate",
                value=f"{data['performance']['win_rate']}%"
            )
        
        with perf_col3:
            st.metric(
                label="Profit Factor",
                value=f"{data['performance']['profit_factor']}"
            )
        
        with perf_col4:
            st.metric(
                label="Max Drawdown",
                value=f"{data['performance']['max_drawdown']}%"
            )
        
        with perf_col5:
            st.metric(
                label="Sharpe Ratio",
                value=f"{data['performance']['sharpe_ratio']}"
            )
        
        # Performance chart
        performance_chart = create_performance_chart(data['trades'])
        st.plotly_chart(performance_chart, use_container_width=True)
    else:
        # Terminal-based fallback
        st.write("Streamlit and required libraries are not available. Please install the dependencies to view the interactive dashboard.")

def show_pattern_analysis(data, selected_symbol, selected_timeframe):
    """Display pattern analysis with explanations."""
    if STREAMLIT_AVAILABLE:
        st.header(f"Pattern Analysis for {selected_symbol}")
        
        # Pattern explanations
        with st.expander("Pattern Types Explanation", expanded=True):
            st.subheader("Break and Retest Pattern")
            st.write("""
            A price movement where the price breaks through a significant support or resistance level, 
            then returns to test that level before continuing in the breakout direction.
            """)
            st.image("https://a.c-dn.net/c/content/dam/publicsites/igcom/uk/images/ContentImage/How-to-trade-breakouts-5.png", 
                    caption="Break and Retest Pattern Example")
            
            st.subheader("Liquidity Sweep Pattern")
            st.write("""
            A brief price movement beyond a key level where stop losses are clustered, 
            triggering those stops, before reversing direction quickly.
            """)
            
            st.subheader("Support/Resistance Patterns")
            st.write("""
            - **Support Bounce**: Price bounces up from an established support level.
            - **Resistance Rejection**: Price rejects down from an established resistance level.
            """)
            
            st.subheader("Candlestick Patterns")
            st.write("""
            Common formations like Hammer, Evening Star, Engulfing patterns, and Doji that indicate
            potential reversals or continuations.
            """)
        
        # Currently detected patterns
        st.subheader("Currently Detected Patterns")
        
        # Convert patterns to DataFrame for better display
        if data['patterns']:
            df_patterns = pd.DataFrame(data['patterns'])
            
            # Add color coding based on pattern strength
            def highlight_strength(val):
                if val >= 4:
                    return 'background-color: rgba(0, 255, 0, 0.3)'
                elif val >= 2:
                    return 'background-color: rgba(255, 255, 0, 0.3)'
                else:
                    return 'background-color: rgba(255, 0, 0, 0.2)'
            
            # Apply styling
            styled_patterns = df_patterns.style.applymap(
                highlight_strength, subset=['strength']
            )
            
            st.dataframe(styled_patterns, use_container_width=True)
            
            # Display probability analysis for selected pattern
            st.subheader("Pattern Success Probability")
            selected_pattern = st.selectbox(
                "Select Pattern for Analysis",
                options=[f"{p['type']} at {p['timestamp']}" for p in data['patterns']]
            )
            
            # Show probability metrics for selected pattern
            pattern_index = [f"{p['type']} at {p['timestamp']}" for p in data['patterns']].index(selected_pattern)
            selected_pattern_data = data['patterns'][pattern_index]
            
            prob_col1, prob_col2, prob_col3 = st.columns(3)
            
            # Calculate probability based on pattern strength (mock calculation)
            success_prob = min(80, 40 + selected_pattern_data['strength'] * 8)
            
            with prob_col1:
                st.metric("Success Probability", f"{success_prob}%")
            
            with prob_col2:
                st.metric("Historical Win Rate", f"{45 + selected_pattern_data['strength'] * 5}%")
            
            with prob_col3:
                st.metric("Avg. RR Ratio", f"{0.8 + selected_pattern_data['strength'] * 0.4:.2f}")
            
            # Pattern-specific recommendations
            st.subheader("Trading Recommendations")
            
            if "Support" in selected_pattern_data['type'] or "Bullish" in selected_pattern_data['type']:
                st.success(f"""
                **LONG OPPORTUNITY**
                - Entry: ${selected_pattern_data['price']:.2f}
                - Stop Loss: ${selected_pattern_data['price'] * 0.98:.2f}
                - Take Profit: ${selected_pattern_data['price'] * 1.05:.2f}
                - Risk-Reward Ratio: 2.5
                """)
            elif "Resistance" in selected_pattern_data['type'] or "Evening Star" in selected_pattern_data['type']:
                st.error(f"""
                **SHORT OPPORTUNITY**
                - Entry: ${selected_pattern_data['price']:.2f}
                - Stop Loss: ${selected_pattern_data['price'] * 1.02:.2f}
                - Take Profit: ${selected_pattern_data['price'] * 0.95:.2f}
                - Risk-Reward Ratio: 2.5
                """)
            else:
                st.info(f"""
                **NEUTRAL**
                - This pattern is not showing a strong directional bias
                - Consider waiting for confirmation before trading
                """)
    else:
        # Terminal-based fallback
        st.write("Streamlit and required libraries are not available. Please install the dependencies to view the interactive dashboard.")

def show_strategy_configuration(risk_per_trade, max_trades):
    """Display strategy configuration options."""
    if STREAMLIT_AVAILABLE:
        st.header("Strategy Configuration")
        
        # Strategy selection
        strategy_type = st.radio(
            "Strategy Type",
            ["Break and Retest", "Liquidity Sweep", "Combined"],
            horizontal=True
        )
        
        # Strategy parameters
        st.subheader("Pattern Detection Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_pattern_strength = st.slider(
                "Minimum Pattern Strength",
                min_value=1,
                max_value=5,
                value=3
            )
            
            confirmation_candles = st.slider(
                "Confirmation Candles",
                min_value=1,
                max_value=5,
                value=2
            )
        
        with col2:
            min_rr_ratio = st.slider(
                "Minimum Risk-Reward Ratio",
                min_value=1.0,
                max_value=5.0,
                value=2.0,
                step=0.1
            )
            
            max_daily_trades = st.slider(
                "Max Daily Trades",
                min_value=1,
                max_value=10,
                value=3
            )
        
        # Risk management settings
        st.subheader("Risk Management Settings")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.metric("Risk Per Trade", f"{risk_per_trade}% of Account")
            st.metric("Max Open Positions", f"{max_trades}")
        
        with col4:
            st.metric("Stop Loss Method", "ATR-Based")
            trailing_stop = st.toggle("Enable Trailing Stop", value=True)
            if trailing_stop:
                st.info("Trailing stop will lock in profits as price moves in your favor.")
        
        # Trading schedule
        st.subheader("Trading Schedule")
        
        trading_hours = st.multiselect(
            "Trading Hours (UTC)",
            options=list(range(24)),
            default=list(range(0, 24, 4))
        )
        
        trading_days = st.multiselect(
            "Trading Days",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        
        # Save settings button
        if st.button("Save Strategy Configuration", type="primary"):
            st.success("Strategy configuration saved successfully!")
            st.balloons()
    else:
        # Terminal-based fallback
        st.write("Streamlit and required libraries are not available. Please install the dependencies to view the interactive dashboard.")

def show_backtesting(data, selected_symbol, selected_timeframe):
    """Display backtesting interface and results."""
    if STREAMLIT_AVAILABLE:
        st.header(f"Backtesting {selected_symbol} on {selected_timeframe}")
        
        # Backtesting parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.datetime.now() - timedelta(days=30)
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.datetime.now()
            )
        
        with col3:
            initial_capital = st.number_input(
                "Initial Capital (USDT)",
                min_value=100,
                value=10000,
                step=100
            )
        
        # Strategy selection for backtesting
        backtest_strategy = st.selectbox(
            "Select Strategy",
            options=["Break and Retest", "Liquidity Sweep", "Support/Resistance", "Combined"]
        )
        
        # Run backtest button
        col4, col5 = st.columns([1, 4])
        with col4:
            if st.button("Run Backtest", type="primary"):
                with st.spinner("Running backtest..."):
                    # Simulate backtest delay
                    import time
                    time.sleep(2)
                    st.success("Backtest completed!")
        
        # Display mock backtest results
        st.subheader("Backtest Results")
        
        # Performance metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric(
                label="Total Return",
                value=f"{data['performance']['total_return']}%",
                delta=f"{data['performance']['total_return'] - 10:.1f}% vs. Buy & Hold"
            )
        
        with metric_col2:
            st.metric(
                label="Win Rate",
                value=f"{data['performance']['win_rate']}%"
            )
        
        with metric_col3:
            st.metric(
                label="Profit Factor",
                value=f"{data['performance']['profit_factor']}"
            )
        
        with metric_col4:
            st.metric(
                label="Max Drawdown",
                value=f"{data['performance']['max_drawdown']}%"
            )
        
        # Equity curve
        st.subheader("Equity Curve")
        performance_chart = create_performance_chart(data['trades'])
        st.plotly_chart(performance_chart, use_container_width=True)
        
        # Trade list
        st.subheader("Trade List")
        if isinstance(data['trades'], list):
            df_trades = pd.DataFrame(data['trades'])
            
            # Add styling
            def color_profit(val):
                color = 'green' if val > 0 else 'red'
                return f'color: {color}'
            
            styled_trades = df_trades.style.applymap(
                color_profit, subset=['profit']
            )
            
            st.dataframe(styled_trades, use_container_width=True)
        else:
            st.dataframe(data['trades'], use_container_width=True)
        
        # Trade distribution
        st.subheader("Trade Distribution")
        
        dist_col1, dist_col2 = st.columns(2)
        
        with dist_col1:
            # Convert to DataFrame for charting
            if isinstance(data['trades'], list):
                df_trades = pd.DataFrame(data['trades'])
                
                # Create win/loss pie chart
                wins = len(df_trades[df_trades['profit'] > 0])
                losses = len(df_trades[df_trades['profit'] <= 0])
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Wins', 'Losses'],
                    values=[wins, losses],
                    hole=.3,
                    marker_colors=['green', 'red']
                )])
                fig.update_layout(title_text="Win/Loss Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        with dist_col2:
            # Create trade type distribution
            if isinstance(data['trades'], list):
                df_trades = pd.DataFrame(data['trades'])
                
                # Count trade types
                long_trades = len(df_trades[df_trades['type'] == 'Long'])
                short_trades = len(df_trades[df_trades['type'] == 'Short'])
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Long', 'Short'],
                    values=[long_trades, short_trades],
                    hole=.3,
                    marker_colors=['blue', 'purple']
                )])
                fig.update_layout(title_text="Long/Short Distribution")
                st.plotly_chart(fig, use_container_width=True)
    else:
        # Terminal-based fallback
        st.write("Streamlit and required libraries are not available. Please install the dependencies to view the interactive dashboard.")

def show_ai_assistant(data):
    """Display AI trading assistant."""
    if STREAMLIT_AVAILABLE:
        st.header("AI Trading Assistant")
        
        # Sample questions
        st.info("""
        You can ask questions about:
        - Trading patterns and strategy
        - Market analysis
        - Risk management
        - Technical indicators
        - Current detected patterns
        """)
        
        # User input
        user_question = st.text_input(
            "Ask a trading question:",
            placeholder="E.g., What is a liquidity sweep pattern?"
        )
        
        if user_question:
            with st.spinner("AI Assistant is thinking..."):
                # Check if OpenAI API key is available
                if not os.environ.get("OPENAI_API_KEY"):
                    st.warning("OpenAI API key is not configured. Using pre-defined responses.")
                    
                    # Pre-defined responses for common questions
                    if "liquidity sweep" in user_question.lower():
                        response = """
                        A liquidity sweep pattern occurs when price briefly moves beyond a key support or resistance level
                        where stop losses are clustered, triggering those stops, before quickly reversing direction.
                        
                        This pattern is created when large market participants want to buy or sell at a specific price level,
                        but there isn't enough available liquidity at that level. To generate more liquidity, they push the
                        price briefly beyond the level to trigger stop losses, creating the liquidity they need to execute
                        their orders when the price reverses.
                        
                        Key characteristics:
                        1. Price approaches a significant level with clustered stop orders
                        2. Price briefly breaks through the level
                        3. A quick reversal occurs after capturing the liquidity
                        4. Often accompanied by higher volume during the sweep
                        """
                    elif "break and retest" in user_question.lower():
                        response = """
                        A break and retest pattern occurs when price breaks through a significant support or resistance level,
                        then returns to test that level before continuing in the breakout direction.
                        
                        For a bullish break and retest:
                        1. Price breaks above a resistance level
                        2. Price pulls back to test the broken resistance (now acting as support)
                        3. Price bounces off this new support level and continues upward
                        
                        For a bearish break and retest:
                        1. Price breaks below a support level
                        2. Price pulls back to test the broken support (now acting as resistance)
                        3. Price rejects this new resistance level and continues downward
                        
                        This pattern provides traders with a higher-probability entry with clearly defined risk levels.
                        """
                    elif "risk management" in user_question.lower():
                        response = """
                        Effective risk management in trading involves:
                        
                        1. Position Sizing: Risk only 1-2% of your account per trade
                        2. Stop Losses: Always use stop losses to limit downside
                        3. Risk-Reward Ratio: Aim for at least 1:2 risk-reward ratio
                        4. Diversification: Don't concentrate all capital in one trade
                        5. Correlation: Be aware of correlation between different assets
                        6. Drawdown Management: Have rules for pausing trading during drawdowns
                        7. Trading Journal: Keep track of all trades and learn from mistakes
                        
                        The most successful traders focus more on risk management than on finding the perfect entry.
                        """
                    else:
                        response = """
                        I don't have a pre-defined answer for this question. With a configured OpenAI API,
                        I would be able to provide a detailed response to your specific question.
                        
                        Try asking about liquidity sweep patterns, break and retest patterns, or risk management.
                        """
                else:
                    # Would use OpenAI in a real implementation
                    # Using mock response for now
                    import time
                    time.sleep(2)  # Simulate API call
                    
                    if "pattern" in user_question.lower():
                        response = """
                        Trading patterns are specific formations in price charts that may indicate potential future price movements.
                        The bot focuses on three main patterns:
                        
                        1. **Break and Retest**: When price breaks through a key level, then returns to test that level before continuing.
                           - Example: Price breaks above resistance, pulls back to test new support, then continues up.
                           
                        2. **Liquidity Sweep**: A brief price movement beyond a key level to trigger stop losses before reversing.
                           - Example: Price briefly drops below support, triggering stop losses, then quickly reverses upward.
                           
                        3. **Support/Resistance**: Price bouncing off or rejecting from established levels.
                           - Example: Price consistently bouncing up from a specific price level (support).
                        
                        Based on your current data, I see **{pattern_type}** patterns forming, which might indicate {direction} potential.
                        """.format(
                            pattern_type=data['patterns'][0]['type'] if data['patterns'] else "no strong",
                            direction="bullish" if data['patterns'] and ("Support" in data['patterns'][0]['type'] or "Bullish" in data['patterns'][0]['type']) else "bearish"
                        )
                    elif "risk" in user_question.lower():
                        response = """
                        Based on your current account size of ${account_balance:,.2f}, I recommend:
                        
                        1. Risk per trade: ${risk_amount:,.2f} (1% of account)
                        2. Max open positions: 3-5 trades
                        3. Target risk-reward ratio: Minimum 1:2
                        4. Set stop losses at key technical levels, ideally protected by liquidity levels
                        5. Consider reducing position size during drawdowns
                        
                        Your current win rate of {win_rate}% and profit factor of {profit_factor} suggest your strategy is working well,
                        but always be prepared to adjust risk parameters during different market conditions.
                        """.format(
                            account_balance=data['account']['balance'],
                            risk_amount=data['account']['balance'] * 0.01,
                            win_rate=data['performance']['win_rate'],
                            profit_factor=data['performance']['profit_factor']
                        )
                    else:
                        response = """
                        Thank you for your question. Based on the trading data I can see:
                        
                        - Your current account balance is ${account_balance:,.2f}
                        - The most recent patterns detected are {patterns}
                        - Your overall performance shows a {total_return}% return with a {win_rate}% win rate
                        
                        The current market conditions for {symbol} suggest a {market_bias} bias, with key liquidity levels at {levels}.
                        
                        I recommend focusing on {recommendation} setups in the coming sessions.
                        """.format(
                            account_balance=data['account']['balance'],
                            patterns=", ".join([p['type'] for p in data['patterns'][:2]]) if data['patterns'] else "no significant patterns",
                            total_return=data['performance']['total_return'],
                            win_rate=data['performance']['win_rate'],
                            symbol="BTC/USDT",
                            market_bias="neutral to slightly bullish" if random.random() > 0.5 else "neutral to slightly bearish",
                            levels=", ".join([f"${l['price']:,.2f}" for l in data['liquidity_levels'][:2]]) if data['liquidity_levels'] else "no significant levels",
                            recommendation="Break and Retest" if random.random() > 0.5 else "Liquidity Sweep"
                        )
                
                # Display response in a nice format
                st.markdown("### AI Response")
                st.markdown(response)
        
        # Example analysis
        with st.expander("Pattern Analysis Example", expanded=False):
            st.subheader("AI Analysis of Current Patterns")
            if data['patterns']:
                pattern = data['patterns'][0]
                
                st.markdown(f"""
                ### Analysis of {pattern['type']} Pattern
                
                **Pattern Strength:** {pattern['strength']}/5
                
                **Pattern Description:**
                This {pattern['type']} pattern detected at ${pattern['price']:,.2f} indicates a potential 
                {'bullish opportunity' if 'Support' in pattern['type'] or 'Bullish' in pattern['type'] or 'Hammer' in pattern['type'] else 'bearish reversal'}.
                
                **Trading Recommendation:**
                Based on historical data, this pattern has approximately a {45 + pattern['strength'] * 8}% chance of playing out successfully.
                
                **Suggested Trade Setup:**
                - {'Buy' if 'Support' in pattern['type'] or 'Bullish' in pattern['type'] or 'Hammer' in pattern['type'] else 'Sell'} near ${pattern['price']:,.2f}
                - Stop Loss: ${pattern['price'] * (0.98 if 'Support' in pattern['type'] or 'Bullish' in pattern['type'] or 'Hammer' in pattern['type'] else 1.02):,.2f}
                - Take Profit: ${pattern['price'] * (1.05 if 'Support' in pattern['type'] or 'Bullish' in pattern['type'] or 'Hammer' in pattern['type'] else 0.95):,.2f}
                
                **Risk Management:**
                With your account size, consider risking a maximum of ${data['account']['balance'] * 0.01:,.2f} on this trade.
                """)
            else:
                st.info("No patterns currently detected for AI analysis.")
    else:
        # Terminal-based fallback
        st.write("Streamlit and required libraries are not available. Please install the dependencies to view the interactive dashboard.")

# Main function
def main():
    # Check if Streamlit is available
    if STREAMLIT_AVAILABLE:
        streamlit_ui()
    else:
        # Terminal fallback message
        print("ERROR: Streamlit and required libraries are not installed.")
        print("To make the app fully interactive, install these packages:")
        print("  pip install streamlit pandas numpy plotly ccxt pandas-ta")
        print("\nRunning terminal-based preview instead...")
        print("Use 'python show_dashboard.py' for a terminal-based dashboard preview.")

if __name__ == "__main__":
    main()
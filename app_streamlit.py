import streamlit as st
import os
import random
import json
from datetime import timedelta, datetime
import time

# Import environment variable loader
from utils.env_loader import loaded_env_vars

# Configure page
st.set_page_config(
    page_title="Crypto Trading Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .pattern-high {color: #0fad58;}
    .pattern-medium {color: #5aa9e6;}
    .pattern-low {color: #7e909a;}
    .positive {color: #0fad58;}
    .negative {color: #f94144;}
    .centered {text-align: center;}
    .metric-value {font-size: 2.5rem !important; font-weight: bold;}
    .metric-label {font-size: 1rem; color: #888;}
    .stTabs [data-baseweb="tab-list"] {gap: 24px;}
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e0f7fa;
        border-bottom: 2px solid #00c4cc;
    }
</style>
""", unsafe_allow_html=True)

# API Status Check
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

def generate_mock_data(selected_symbol="BTC/USDT"):
    """Generate mock data for demonstration."""
    # Mock candlestick data
    num_candles = 100
    today = datetime.now()
    dates = [(today - timedelta(hours=i)).strftime("%Y-%m-%d %H:00") for i in range(num_candles)]
    dates.reverse()
    
    # Start with a base price and generate realistic-looking price movement
    # Use different price ranges for different trading pairs
    if "BTC" in selected_symbol:
        base_price = 65000
    elif "ETH" in selected_symbol:
        base_price = 3300
    elif "WIF" in selected_symbol:
        base_price = 2.75
    elif "SOL" in selected_symbol:
        base_price = 180
    elif "BNB" in selected_symbol:
        base_price = 580
    else:
        base_price = 1000
        
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
    symbols = ["BTC/USDT", "ETH/USDT", "WIF/USDT", "SOL/USDT", "BNB/USDT"]
    
    for i in range(10):
        entry_idx = random.randint(0, num_candles - 20)
        exit_idx = entry_idx + random.randint(5, 15)
        if exit_idx >= num_candles:
            exit_idx = num_candles - 1
            
        entry_price = price_data[entry_idx]["close"]
        exit_price = price_data[exit_idx]["close"]
        profit = round((exit_price - entry_price) / entry_price * 100, 2)
        
        trade = {
            "id": i + 1,
            "symbol": symbols[i % len(symbols)],
            "entry_date": price_data[entry_idx]["date"],
            "exit_date": price_data[exit_idx]["date"],
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": round(random.uniform(0.1, 0.5), 2),
            "profit": profit,
            "profit_usd": round(profit * entry_price * 0.01, 2),
            "type": "Long" if random.random() > 0.3 else "Short"
        }
        trades.append(trade)
    
    # Sort trades by date
    trades.sort(key=lambda x: x["entry_date"], reverse=True)
    
    # Mock liquidity levels
    liquidity_levels = []
    for i in range(3):
        level_price = base_price * (1 + random.uniform(-5, 5)/100)
        liquidity_levels.append({
            "price": round(level_price, 2),
            "strength": round(random.uniform(1, 5), 2),
            "type": "Support" if i % 2 == 0 else "Resistance"
        })
    
    return {
        "price_data": price_data,
        "patterns": patterns,
        "account": account,
        "performance": performance,
        "trades": trades,
        "liquidity_levels": liquidity_levels
    }

# Simulated pattern descriptions
pattern_descriptions = {
    "Break and Retest": """
    A Break and Retest pattern occurs when price breaks through a significant support or resistance level, 
    then returns to test that level before continuing in the breakout direction. For a bullish break and retest, 
    price breaks above resistance, pulls back to test the broken resistance (now support), and then continues upward. 
    
    For a bearish break and retest, price breaks below support, pulls back to test the broken support (now resistance), 
    and then continues downward. These patterns are valuable because they offer traders a higher-probability entry 
    with a clearly defined risk level.
    """,
    
    "Liquidity Sweep": """
    A Liquidity Sweep pattern occurs when price briefly moves beyond a significant level where stop losses are likely 
    clustered, triggering those stops, before quickly reversing direction. This pattern is engineered by larger market 
    participants to access liquidity before making the actual move in the opposite direction.
    
    Key characteristics include:
    1. Price approaching a level with clustered stop losses
    2. Brief penetration of that level with increased volume
    3. Quick rejection and reversal
    4. Continued movement in the reversed direction
    
    Liquidity sweeps often occur at previous support/resistance levels, recent highs/lows, or significant round numbers.
    """,
    
    "Support Bounce": """
    A Support Bounce pattern occurs when price approaches a previously established support level and bounces 
    upward from it, confirming the validity of the support. This often presents a buying opportunity with 
    a well-defined risk level (placing a stop loss just below the support).
    
    The strength of a support bounce depends on:
    1. The number of times the support has been tested previously
    2. The volume during the bounce
    3. The price action formation at the support (e.g., hammer candlesticks)
    4. The speed and magnitude of the bounce
    """,
    
    "Resistance Rejection": """
    A Resistance Rejection pattern occurs when price approaches a previously established resistance level and 
    gets rejected downward, confirming the strength of the resistance. This often presents a selling opportunity 
    with a well-defined risk level (placing a stop loss just above the resistance).
    
    The strength of a resistance rejection depends on:
    1. The number of times the resistance has been tested previously
    2. The volume during the rejection
    3. The price action formation at the resistance (e.g., shooting star candlesticks)
    4. The speed and magnitude of the rejection
    """
}

# Main application
def main():
    # Sidebar
    st.sidebar.title("Crypto Trading Bot")
    st.sidebar.image("static/images/stock-exchange.svg", width=80)
    
    api_status = check_api_status()
    
    # Display API status
    st.sidebar.subheader("API Configuration")
    if api_status["openai"]:
        st.sidebar.success("OpenAI API: Connected ✓")
    else:
        st.sidebar.error("OpenAI API: Not Connected ✗")
        
    if api_status["bitget"]:
        st.sidebar.success("Bitget API: Connected ✓")
    else:
        st.sidebar.error("Bitget API: Not Connected ✗")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Pattern Analysis", "Strategy Configuration", "Backtesting", "AI Assistant"])
    
    # Trading symbols selection
    st.sidebar.title("Trading Pair")
    selected_symbol = st.sidebar.selectbox(
        "Select trading pair", 
        ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "WIF/USDT"]
    )
    
    # Timeframe selection
    st.sidebar.title("Timeframe")
    selected_timeframe = st.sidebar.selectbox("Select timeframe", ["5m", "15m", "30m", "1h", "4h", "1d"])
    
    # Risk management settings
    st.sidebar.title("Risk Settings")
    risk_per_trade = st.sidebar.slider("Risk per trade (%)", 0.1, 3.0, 1.0, 0.1)
    max_trades = st.sidebar.slider("Max concurrent trades", 1, 5, 3, 1)
    
    # Generate mock data for demonstration
    data = generate_mock_data(selected_symbol)
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard(data, selected_symbol, selected_timeframe)
    elif page == "Pattern Analysis":
        show_pattern_analysis(data, selected_symbol, selected_timeframe)
    elif page == "Strategy Configuration":
        show_strategy_configuration(risk_per_trade, max_trades)
    elif page == "Backtesting":
        show_backtesting(data, selected_symbol, selected_timeframe)
    elif page == "AI Assistant":
        show_ai_assistant(data)

def show_dashboard(data, selected_symbol, selected_timeframe):
    st.title(f"Dashboard - {selected_symbol} ({selected_timeframe})")
    
    # Account metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"<div class='metric-label'>Account Balance</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>${data['account']['balance']:,.2f}</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"<div class='metric-label'>Open Positions</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{data['account']['open_positions']}</div>", unsafe_allow_html=True)
        
    with col3:
        pnl_class = "positive" if data['account']['unrealized_pnl'] >= 0 else "negative"
        st.markdown(f"<div class='metric-label'>Unrealized P&L</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value {pnl_class}'>${data['account']['unrealized_pnl']:,.2f}</div>", unsafe_allow_html=True)
        
    with col4:
        daily_class = "positive" if data['account']['daily_pnl'] >= 0 else "negative"
        st.markdown(f"<div class='metric-label'>Daily P&L</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value {daily_class}'>${data['account']['daily_pnl']:,.2f}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Price chart (simplified for this demo)
    st.subheader("Price Chart")
    st.info("In the full application, an interactive candlestick chart would be displayed here with technical indicators.")
    
    # Display price data summary
    recent_prices = data['price_data'][-5:]
    
    price_table = "<div style='overflow-x: auto;'><table style='width:100%'>"
    price_table += "<tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th></tr>"
    
    for candle in recent_prices:
        price_table += f"<tr>"
        price_table += f"<td>{candle['date']}</td>"
        price_table += f"<td>${candle['open']:,.2f}</td>"
        price_table += f"<td>${candle['high']:,.2f}</td>"
        price_table += f"<td>${candle['low']:,.2f}</td>"
        price_table += f"<td>${candle['close']:,.2f}</td>"
        price_table += f"<td>{candle['volume']:,.2f}</td>"
        price_table += f"</tr>"
    
    price_table += "</table></div>"
    st.markdown(price_table, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent patterns and signals
    st.subheader("Recent Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for i, pattern in enumerate(data['patterns'][:3]):
            strength_class = "pattern-high" if pattern['strength'] >= 4 else "pattern-medium" if pattern['strength'] >= 2 else "pattern-low"
            st.markdown(f"<div><b class='{strength_class}'>{pattern['type']}</b> at ${pattern['price']:,.2f} (Strength: {pattern['strength']})</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.8em; color:#888;'>{pattern['timestamp']}</div>", unsafe_allow_html=True)
            if i < 2:
                st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("Liquidity Levels")
        for level in data['liquidity_levels']:
            level_class = "positive" if level['type'] == "Support" else "negative"
            st.markdown(f"<div><b class='{level_class}'>{level['type']}</b>: ${level['price']:,.2f} (Strength: {level['strength']})</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent trades
    st.subheader("Recent Trades")
    
    trades_table = "<div style='overflow-x: auto;'><table style='width:100%'>"
    trades_table += "<tr><th>Date</th><th>Symbol</th><th>Type</th><th>Entry</th><th>Exit</th><th>Size</th><th>Profit</th></tr>"
    
    for trade in data['trades'][:5]:
        profit_class = "positive" if trade['profit'] >= 0 else "negative"
        profit_sign = "+" if trade['profit'] >= 0 else ""
        
        trades_table += f"<tr>"
        trades_table += f"<td>{trade['entry_date']}</td>"
        trades_table += f"<td>{trade['symbol']}</td>"
        trades_table += f"<td>{trade['type']}</td>"
        trades_table += f"<td>${trade['entry_price']:,.2f}</td>"
        trades_table += f"<td>${trade['exit_price']:,.2f}</td>"
        
        # Adjust the display text based on the trading pair
        if "BTC" in trade['symbol']:
            size_text = f"{trade['size']} BTC"
        elif "ETH" in trade['symbol']:
            size_text = f"{trade['size']} ETH"
        elif "WIF" in trade['symbol']:
            size_text = f"{trade['size']} WIF"
        else:
            size_text = f"{trade['size']}"
            
        trades_table += f"<td>{size_text}</td>"
        trades_table += f"<td class='{profit_class}'>{profit_sign}{trade['profit']}% (${trade['profit_usd']:,.2f})</td>"
        trades_table += f"</tr>"
    
    trades_table += "</table></div>"
    st.markdown(trades_table, unsafe_allow_html=True)

def show_pattern_analysis(data, selected_symbol, selected_timeframe):
    st.title(f"Pattern Analysis - {selected_symbol}")
    
    # Pattern explanation
    st.subheader("Pattern Types")
    
    pattern_tabs = st.tabs(["Break and Retest", "Liquidity Sweep", "Support/Resistance", "Candlestick Patterns"])
    
    with pattern_tabs[0]:
        st.markdown(pattern_descriptions["Break and Retest"])
        st.image("static/images/break-retest.svg", caption="Break and Retest Pattern Illustration")
    
    with pattern_tabs[1]:
        st.markdown(pattern_descriptions["Liquidity Sweep"])
        st.image("static/images/liquidity-sweep.svg", caption="Liquidity Sweep Pattern Illustration")
    
    with pattern_tabs[2]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Support Bounce")
            st.markdown(pattern_descriptions["Support Bounce"])
        with col2:
            st.markdown("### Resistance Rejection")
            st.markdown(pattern_descriptions["Resistance Rejection"])
            
    with pattern_tabs[3]:
        st.markdown("""
        ### Common Candlestick Patterns
        
        - **Hammer**: A bullish reversal pattern that forms during a downtrend, signaling a potential bottom.
        - **Evening Star**: A bearish reversal pattern that forms at the top of an uptrend, signaling a potential top.
        - **Engulfing Pattern**: A two-candle pattern where the second candle completely engulfs the first, signaling a potential reversal.
        - **Doji**: A candle with a small body, indicating indecision in the market.
        """)
        st.image("static/images/candlestick-patterns.svg", caption="Common Candlestick Patterns")
    
    st.markdown("---")
    
    # Currently detected patterns
    st.subheader("Detected Patterns")
    
    detected_patterns = "<ul style='list-style-type:none; padding-left:0;'>"
    
    for pattern in data['patterns']:
        strength_class = "pattern-high" if pattern['strength'] >= 4 else "pattern-medium" if pattern['strength'] >= 2 else "pattern-low"
        detected_patterns += f"<li style='margin-bottom:15px;'>"
        detected_patterns += f"<div><b class='{strength_class}'>{pattern['type']}</b> at ${pattern['price']:,.2f} (Strength: {pattern['strength']})</div>"
        detected_patterns += f"<div style='font-size:0.9em;'>Time: {pattern['timestamp']}</div>"
        detected_patterns += f"<div style='font-size:0.9em;'>{pattern['description']}</div>"
        detected_patterns += f"</li>"
    
    detected_patterns += "</ul>"
    st.markdown(detected_patterns, unsafe_allow_html=True)
    
    # Sample pattern probability analysis
    st.subheader("Pattern Probability Analysis")
    st.info("The full application would include AI-powered analysis of pattern probability based on historical performance.")
    
    # Create columns for the stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Break and Retest Success Rate", "68%", "+5%")
        
    with col2:
        st.metric("Liquidity Sweep Success Rate", "72%", "+3%")
        
    with col3:
        st.metric("Pattern Detection Accuracy", "84%", "-2%")

def show_strategy_configuration(risk_per_trade, max_trades):
    st.title("Strategy Configuration")
    
    # Main strategy settings
    st.subheader("Trading Strategies")
    
    strategy_tabs = st.tabs(["Break and Retest", "Liquidity Sweep", "Combined Strategy"])
    
    with strategy_tabs[0]:
        st.markdown("### Break and Retest Strategy Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.slider("Breakout Confirmation (%)", 0.5, 3.0, 1.0, 0.1)
            st.slider("Retest Zone Width (%)", 0.2, 2.0, 0.5, 0.1)
            st.selectbox("Entry Condition", ["On Rejection", "After Confirmation Candle", "Limit Order at Level"])
        
        with col2:
            st.slider("Stop Loss Placement (%)", 0.5, 3.0, 1.5, 0.1)
            st.selectbox("Take Profit Method", ["Fixed Risk:Reward", "At Next Resistance/Support", "Trailing Stop"])
            st.slider("Risk:Reward Ratio", 1.0, 5.0, 2.0, 0.5)
    
    with strategy_tabs[1]:
        st.markdown("### Liquidity Sweep Strategy Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.slider("Sweep Depth Required (%)", 0.2, 2.0, 0.5, 0.1)
            st.slider("Reversal Confirmation (%)", 0.3, 2.0, 0.7, 0.1)
            st.selectbox("Entry Timing", ["Immediate on Reversal", "After Confirmation Candle", "Retracement to Level"])
        
        with col2:
            st.slider("Sweep Stop Loss (%)", 0.5, 3.0, 1.2, 0.1)
            st.selectbox("Take Profit Strategy", ["Fixed Risk:Reward", "Previous Structure", "Trailing Stop"])
            st.slider("Sweep Risk:Reward", 1.5, 5.0, 3.0, 0.5)
    
    with strategy_tabs[2]:
        st.markdown("### Combined Strategy Settings")
        
        st.markdown("""
        The combined strategy uses both Break and Retest and Liquidity Sweep patterns,
        prioritizing trades based on pattern strength and market conditions.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Pattern Priority", ["Equal Weighting", "Favor Liquidity Sweeps", "Favor Break and Retest"])
            st.slider("Minimum Pattern Strength", 1, 5, 3)
        
        with col2:
            st.checkbox("Allow Multiple Concurrent Setups", True)
            st.number_input("Max Trades Per Pattern Type", 1, 5, 2)
    
    st.markdown("---")
    
    # Risk management settings
    st.subheader("Risk Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"Risk Per Trade: **{risk_per_trade}%** of account")
        st.markdown(f"Maximum Concurrent Trades: **{max_trades}**")
        st.markdown("Maximum Daily Drawdown: **4%** of account")
        
    with col2:
        st.selectbox("Position Sizing Method", ["Fixed Risk Percentage", "Kelly Criterion", "Fixed Lot Size"])
        st.selectbox("Exit Strategy", ["Set Risk:Reward", "Technical Levels", "Trailing Stop Loss"])
        st.checkbox("Enable Advanced Risk Management", True)
    
    # Strategy performance simulator
    st.markdown("---")
    st.subheader("Strategy Performance Simulator")
    st.info("The full application would include a strategy simulator to evaluate expected performance under different market conditions.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Expected Win Rate", f"{random.randint(58, 68)}%")
        
    with col2:
        st.metric("Expected Profit Factor", f"{random.uniform(1.8, 2.4):.2f}")
        
    with col3:
        st.metric("Expected Annual Return", f"{random.randint(35, 65)}%")

def show_backtesting(data, selected_symbol, selected_timeframe):
    st.title(f"Backtesting - {selected_symbol}")
    
    # Backtesting controls
    st.subheader("Backtest Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.date_input("Start Date", datetime.now() - timedelta(days=90))
        st.selectbox("Trading Strategy", ["Break and Retest", "Liquidity Sweep", "Combined Strategy"])
        
    with col2:
        st.date_input("End Date", datetime.now())
        st.selectbox("Initial Balance", ["$10,000", "$25,000", "$50,000", "$100,000"])
        
    with col3:
        st.selectbox("Risk Per Trade", ["0.5%", "1%", "2%", "3%"])
        st.button("Run Backtest")
    
    st.markdown("---")
    
    # Backtest results
    st.subheader("Backtest Results")
    st.info("The full application would display actual backtest results with performance metrics and trade analytics.")
    
    # Sample backtest performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Return", f"{data['performance']['total_return']}%", "Compared to 12% Market")
        
    with col2:
        st.metric("Win Rate", f"{data['performance']['win_rate']}%")
        
    with col3:
        st.metric("Profit Factor", f"{data['performance']['profit_factor']}")
        
    with col4:
        st.metric("Max Drawdown", f"{data['performance']['max_drawdown']}%")
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sharpe Ratio", f"{data['performance']['sharpe_ratio']}")
        
    with col2:
        st.metric("Total Trades", f"{random.randint(85, 120)}")
        
    with col3:
        st.metric("Average Hold Time", f"{random.randint(8, 24)} hours")
        
    with col4:
        st.metric("Best Trade", f"+{random.uniform(20, 45):.2f}%")
    
    st.markdown("---")
    
    # Trade distribution
    st.subheader("Trade Performance Distribution")
    
    st.markdown("""
    <div style="background-color:#f8f9fa; padding:10px; border-radius:5px; margin-bottom:20px;">
        <p>The full application would include detailed performance charts including:</p>
        <ul>
            <li>Equity curve over time</li>
            <li>Trade P&L distribution</li>
            <li>Performance by pattern type</li>
            <li>Drawdown periods</li>
            <li>Monthly/weekly returns</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample trades table
    st.subheader("Backtest Trades")
    
    trades_table = "<div style='overflow-x: auto;'><table style='width:100%'>"
    trades_table += "<tr><th>Date</th><th>Pattern</th><th>Entry</th><th>Exit</th><th>Hold Time</th><th>Result</th></tr>"
    
    for i in range(5):
        # Create some sample backtest trades
        entry_date = (datetime.now() - timedelta(days=random.randint(10, 90))).strftime("%Y-%m-%d %H:%M")
        hold_hours = random.randint(4, 72)
        exit_date = (datetime.strptime(entry_date, "%Y-%m-%d %H:%M") + timedelta(hours=hold_hours)).strftime("%Y-%m-%d %H:%M")
        pattern = random.choice(["Break and Retest", "Liquidity Sweep", "Support Bounce", "Resistance Rejection"])
        entry_price = random.uniform(30000, 70000)
        exit_price = entry_price * (1 + random.uniform(-0.05, 0.1))
        result_pct = (exit_price - entry_price) / entry_price * 100
        
        result_class = "positive" if result_pct >= 0 else "negative"
        result_sign = "+" if result_pct >= 0 else ""
        
        trades_table += f"<tr>"
        trades_table += f"<td>{entry_date}</td>"
        trades_table += f"<td>{pattern}</td>"
        trades_table += f"<td>${entry_price:,.2f}</td>"
        trades_table += f"<td>${exit_price:,.2f}</td>"
        trades_table += f"<td>{hold_hours} hours</td>"
        trades_table += f"<td class='{result_class}'>{result_sign}{result_pct:.2f}%</td>"
        trades_table += f"</tr>"
    
    trades_table += "</table></div>"
    st.markdown(trades_table, unsafe_allow_html=True)

def show_ai_assistant(data):
    st.title("AI Trading Assistant")
    
    # Sample questions
    st.subheader("Ask a Trading Question")
    
    user_question = st.text_input("Enter your question about trading, patterns, or market analysis:", 
                               placeholder="Example: What is a good entry strategy for a break and retest pattern?")
    
    sample_questions = [
        "What is a break and retest pattern?",
        "How can I identify a good liquidity sweep setup?",
        "What are the key differences between trading WIF/USDT vs. BTC/USDT?"
    ]
    
    sample_q_tabs = st.tabs(["Sample Q1", "Sample Q2", "Sample Q3"])
    
    for i, tab in enumerate(sample_q_tabs):
        with tab:
            st.markdown(f"**Q: {sample_questions[i]}**")
            if i == 0:
                st.markdown("""
                **A:** A break and retest pattern occurs when price breaks through a significant support or resistance level, then returns to test that level before continuing in the breakout direction. For a bullish break and retest, price breaks above resistance, pulls back to test the broken resistance (now support), and then continues upward. For a bearish break and retest, price breaks below support, pulls back to test the broken support (now resistance), and then continues downward. These patterns are valuable because they offer traders a higher-probability entry with a clearly defined risk level.
                """)
            elif i == 1:
                st.markdown("""
                **A:** A good liquidity sweep setup can be identified by these characteristics:
                
                1. Price approaching a level with clustered stop losses (often below recent lows for longs or above recent highs for shorts)
                2. Strong rejection after sweeping the level (quick reversal)
                3. Higher than average volume during the sweep, showing strong participation
                4. Price closing back beyond the swept level on the reversal candle
                5. Previous market structure that suggests accumulation or distribution
                
                The best setups occur at key technical levels where many traders would place stops, creating a pool of liquidity that larger players might target. Watch for price briefly breaking these levels before quickly reversing with strength, suggesting the sweep was engineered to collect liquidity before the actual move.
                """)
            elif i == 2:
                st.markdown("""
                **A:** Trading WIF/USDT vs. BTC/USDT involves several key differences:

                1. Volatility: WIF typically exhibits higher volatility than BTC, which creates both greater opportunity and risk. Price swings in WIF can be more extreme percentage-wise.

                2. Liquidity: BTC/USDT pairs generally have much higher liquidity, meaning tighter spreads and less slippage when entering and exiting positions. WIF may experience more significant price impact with larger orders.

                3. Market forces: BTC often leads the broader crypto market, while WIF and other altcoins may follow BTC's general direction but with amplified movements. This creates potential for both larger gains and losses.

                4. Market information: BTC has more extensive market analysis, institutional coverage, and on-chain data available compared to WIF, which may have less reliable signals and indicators.

                5. Risk profile: WIF generally represents a higher risk, potentially higher reward opportunity compared to the relatively more established Bitcoin market.

                Consider position sizing appropriately when trading WIF to account for the increased volatility and risk.
                """)
    
    # If user enters a question, show a response
    if user_question:
        st.markdown("---")
        st.subheader("AI Assistant Response")
        
        # Show a loading spinner to simulate AI processing
        with st.spinner("Analyzing your question..."):
            time.sleep(1)  # Simulate processing time
        
        if "pattern" in user_question.lower() or "setup" in user_question.lower():
            st.markdown("""
            Trading patterns are probabilistic setups that can help identify potential trading opportunities with defined risk. 
            Remember that no pattern is 100% accurate, and proper risk management is crucial.
            
            For the best results with pattern trading:
            1. Look for patterns with strong confirmation signals
            2. Ensure the pattern aligns with the overall market structure
            3. Use proper position sizing (no more than 1-2% risk per trade)
            4. Always use stop losses to protect your capital
            5. Consider the current market volatility when setting profit targets
            
            The most reliable patterns tend to form on higher timeframes (4h and above) and during trending markets rather than ranging conditions.
            """)
        elif "strategy" in user_question.lower() or "trading plan" in user_question.lower():
            st.markdown("""
            A solid trading strategy should include these key components:
            
            1. Entry criteria - specific conditions that must be met before entering a trade
            2. Exit criteria - predetermined levels for taking profit and cutting losses
            3. Position sizing - rules for determining trade size based on account risk
            4. Market conditions - when to be active vs. when to stay on the sidelines
            5. Performance metrics - how to measure success and areas for improvement
            
            For cryptocurrency trading specifically, consider adding:
            - Correlation monitoring with Bitcoin (as it often leads the market)
            - Liquidity analysis (avoid low liquidity pairs/times)
            - Volatility adjustments (adjust position sizing during high volatility)
            
            The most successful traders I've seen focus more on risk management than on finding the perfect entry.
            """)
        elif "wif" in user_question.lower():
            st.markdown("""
            WIF (Wrapped Bitcoin) trading requires some specific considerations:
            
            1. Higher volatility - WIF can experience more dramatic price swings than more established cryptocurrencies
            2. Lower liquidity - This can lead to wider spreads and more slippage on larger orders
            3. Higher correlation with Bitcoin - WIF often follows Bitcoin's movements but with amplified reactions
            4. Project-specific risks - Stay updated on development progress and community activity
            
            For WIF trading specifically:
            - Use smaller position sizes (perhaps 50-75% of your normal size)
            - Consider wider stop losses to account for higher volatility
            - Watch for liquidity gaps that could lead to sharp price movements
            - Pay attention to Bitcoin's direction as it often leads market sentiment
            
            Despite the higher risk, WIF can offer excellent trading opportunities due to its volatility and technical pattern formation.
            """)
        else:
            st.markdown("""
            Thank you for your question. In a complete implementation, this AI assistant would:
            
            1. Analyze your specific question using OpenAI's advanced language models
            2. Consider market context, trading history, and detected patterns
            3. Provide personalized guidance based on your trading preferences and history
            4. Include relevant examples, charts, or data visualizations
            5. Offer actionable advice with specific parameters when appropriate
            
            The assistant would combine pattern recognition, market analysis, and risk management principles to help you make more informed trading decisions.
            """)
    
    st.markdown("---")
    
    # Pattern analysis
    st.subheader("Recent Pattern Analysis")
    st.info("The full implementation would include AI-powered analysis of recently detected patterns.")
    
    if data['patterns']:
        pattern = data['patterns'][0]  # Get the most recent pattern
        
        st.markdown(f"### Analysis of {pattern['type']} pattern at ${pattern['price']:,.2f}")
        
        st.markdown(f"""
        **Pattern Strength**: {pattern['strength']}/5
        
        **AI Analysis**:
        This {pattern['type']} pattern shows {'strong' if pattern['strength'] >= 4 else 'moderate' if pattern['strength'] >= 2 else 'weak'} potential for a {'continuation' if random.random() > 0.5 else 'reversal'} move. Based on historical patterns of this type, there is approximately a {random.randint(60, 85)}% probability of reaching the first target.
        
        **Suggested Action**:
        {'Consider a long entry with stop loss below the pattern low' if random.random() > 0.5 else 'Consider a short entry with stop loss above the pattern high'} with a risk:reward ratio of 1:{random.randint(2, 4)}.
        
        **Key Levels to Watch**:
        - Support: ${pattern['price']*(1-random.uniform(0.03, 0.08)):.2f}
        - Resistance: ${pattern['price']*(1+random.uniform(0.03, 0.08)):.2f}
        - Target 1: ${pattern['price']*(1+random.uniform(0.05, 0.15)):.2f}
        - Target 2: ${pattern['price']*(1+random.uniform(0.15, 0.25)):.2f}
        """)

if __name__ == "__main__":
    main()
import streamlit as st
import os
import random
import datetime
import json
from datetime import timedelta, datetime

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
</style>
""", unsafe_allow_html=True)

# API Status Check
def check_api_status():
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    bitget_api_key = os.environ.get("BITGET_API_KEY", "")
    bitget_api_secret = os.environ.get("BITGET_API_SECRET", "")
    bitget_api_password = os.environ.get("BITGET_API_PASSWORD", "")
    
    api_status = {}
    api_status["openai"] = bool(openai_api_key)
    api_status["bitget"] = bool(bitget_api_key and bitget_api_secret and bitget_api_password)
    
    return api_status

# Generate mock data for UI demonstration
def generate_mock_data():
    # Mock candlestick data
    num_candles = 100
    today = datetime.now()
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
            "symbol": "BTC/USDT",
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
    st.sidebar.image("https://img.icons8.com/fluency/96/000000/stock-exchange.png", width=80)
    
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
    selected_symbol = st.sidebar.selectbox("Select trading pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"])
    
    # Timeframe selection
    st.sidebar.title("Timeframe")
    selected_timeframe = st.sidebar.selectbox("Select timeframe", ["5m", "15m", "30m", "1h", "4h", "1d"])
    
    # Risk management settings
    st.sidebar.title("Risk Settings")
    risk_per_trade = st.sidebar.slider("Risk per trade (%)", 0.1, 3.0, 1.0, 0.1)
    max_trades = st.sidebar.slider("Max concurrent trades", 1, 5, 3, 1)
    
    # Generate mock data for demonstration
    data = generate_mock_data()
    
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
    st.write("*Note: In the full application, an interactive candlestick chart would be displayed here with technical indicators.*")
    
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
        trades_table += f"<td>{trade['size']} BTC</td>"
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
        st.image("https://a.c-dn.net/c/content/dam/publicsites/igcom/uk/images/ContentImage/How-to-trade-breakouts.png", caption="Break and Retest Pattern Illustration")
    
    with pattern_tabs[1]:
        st.markdown(pattern_descriptions["Liquidity Sweep"])
        st.image("https://forextraininggroup.com/wp-content/uploads/2016/11/Liquidity-Sweep-Trade-Example.png", caption="Liquidity Sweep Pattern Illustration")
    
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
        - **Evening Star**: A bearish reversal pattern consisting of three candles, signaling a potential top.
        - **Engulfing Patterns**: When a candle completely engulfs the previous candle, signaling potential reversal.
        - **Doji**: Represents indecision in the market with nearly equal open and close prices.
        """)
    
    st.markdown("---")
    
    # Currently detected patterns
    st.subheader("Currently Detected Patterns")
    
    for pattern in data['patterns']:
        with st.expander(f"{pattern['type']} at ${pattern['price']:,.2f} (Strength: {pattern['strength']})"):
            st.markdown(f"**Time**: {pattern['timestamp']}")
            st.markdown(f"**Description**: {pattern['description']}")
            
            # In a full implementation, this would include a zoomed chart of the pattern
            st.markdown("*A zoomed chart of this pattern would be displayed here in the full application.*")
    
    st.markdown("---")
    
    # Pattern settings
    st.subheader("Pattern Detection Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.slider("Minimum pattern strength", 1, 5, 2)
        st.slider("Look-back period (days)", 1, 30, 7)
        
    with col2:
        st.multiselect("Pattern types to detect", 
                      ["Break and Retest", "Liquidity Sweep", "Support Bounce", "Resistance Rejection",
                       "Engulfing", "Hammer", "Evening Star", "Doji"],
                      ["Break and Retest", "Liquidity Sweep", "Support Bounce", "Resistance Rejection"])
        
        st.checkbox("Automatically generate trade signals", True)
    
    st.button("Update Pattern Settings")

def show_strategy_configuration(risk_per_trade, max_trades):
    st.title("Strategy Configuration")
    
    # Strategy selection
    st.subheader("Trading Strategy")
    selected_strategy = st.selectbox("Select primary strategy", 
                                     ["Break and Retest + Liquidity Sweep", 
                                      "Support/Resistance Bounce", 
                                      "Trend Following", 
                                      "Mean Reversion"])
    
    # Risk management settings
    st.subheader("Risk Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Risk per trade**: {risk_per_trade}% of account balance")
        
        take_profit_multiplier = st.slider("Take profit (risk multiple)", 1.0, 5.0, 2.0, 0.5)
        st.markdown(f"For a trade with 1% risk, take profit will be set at {take_profit_multiplier}% gain")
        
        max_daily_risk = st.slider("Maximum daily risk (%)", 1.0, 10.0, 3.0, 0.5)
        
    with col2:
        st.markdown(f"**Maximum concurrent trades**: {max_trades}")
        
        dynamic_position_sizing = st.checkbox("Use dynamic position sizing based on pattern strength", True)
        
        trailing_stop = st.checkbox("Use trailing stop loss", True)
        if trailing_stop:
            activation_percentage = st.slider("Trailing stop activation (%)", 0.5, 3.0, 1.0, 0.1)
            
    # Trading conditions
    st.subheader("Trading Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.multiselect("Trading days", 
                      ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                      ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        trading_hours = st.slider("Trading hours (UTC)", 0, 23, (0, 23))
        st.write(f"Trading between {trading_hours[0]}:00 and {trading_hours[1]}:00 UTC")
        
    with col2:
        st.selectbox("Trade execution mode", ["Manual confirmation", "Semi-automatic", "Fully automatic"])
        
        st.selectbox("Order types", ["Limit orders only", "Market orders only", "Smart (context dependent)"])
        
        st.checkbox("Avoid trading before major news events", True)
    
    # Save settings
    if st.button("Save Strategy Configuration"):
        st.success("Strategy configuration saved successfully!")

def show_backtesting(data, selected_symbol, selected_timeframe):
    st.title(f"Strategy Backtesting - {selected_symbol}")
    
    # Backtest parameters
    st.subheader("Backtest Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.date_input("Start date", datetime.now() - timedelta(days=30))
    
    with col2:
        st.date_input("End date", datetime.now())
        
    with col3:
        st.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h", "1d"], 
                    index=["5m", "15m", "30m", "1h", "4h", "1d"].index(selected_timeframe))
    
    # Strategy selection
    selected_strategy = st.selectbox("Strategy to test", 
                                    ["Break and Retest + Liquidity Sweep", 
                                     "Support/Resistance Bounce", 
                                     "Trend Following", 
                                     "Mean Reversion"])
    
    initial_capital = st.number_input("Initial capital (USD)", min_value=1000, max_value=1000000, value=10000, step=1000)
    
    # Run backtest button
    if st.button("Run Backtest"):
        st.info("Backtest running... This would process historical data in the full application.")
        
        # Show performance metrics
        st.subheader("Backtest Results")
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", f"{data['performance']['total_return']}%")
            
        with col2:
            st.metric("Win Rate", f"{data['performance']['win_rate']}%")
            
        with col3:
            st.metric("Profit Factor", f"{data['performance']['profit_factor']}")
            
        with col4:
            st.metric("Max Drawdown", f"{data['performance']['max_drawdown']}%")
        
        # Performance chart placeholder
        st.subheader("Equity Curve")
        st.write("*An interactive equity curve chart would be displayed here in the full application.*")
        
        # Trade list
        st.subheader("Trade List")
        
        trades_table = "<div style='overflow-x: auto;'><table style='width:100%'>"
        trades_table += "<tr><th>Entry Date</th><th>Exit Date</th><th>Type</th><th>Entry</th><th>Exit</th><th>Profit</th><th>Result</th></tr>"
        
        for trade in data['trades']:
            profit_class = "positive" if trade['profit'] >= 0 else "negative"
            profit_sign = "+" if trade['profit'] >= 0 else ""
            result = "Win" if trade['profit'] >= 0 else "Loss"
            
            trades_table += f"<tr>"
            trades_table += f"<td>{trade['entry_date']}</td>"
            trades_table += f"<td>{trade['exit_date']}</td>"
            trades_table += f"<td>{trade['type']}</td>"
            trades_table += f"<td>${trade['entry_price']:,.2f}</td>"
            trades_table += f"<td>${trade['exit_price']:,.2f}</td>"
            trades_table += f"<td class='{profit_class}'>{profit_sign}{trade['profit']}%</td>"
            trades_table += f"<td class='{profit_class}'>{result}</td>"
            trades_table += f"</tr>"
        
        trades_table += "</table></div>"
        st.markdown(trades_table, unsafe_allow_html=True)
        
        # Strategy optimization
        st.subheader("Strategy Optimization")
        st.write("*In the full application, you would be able to optimize strategy parameters here.*")
        
        # Export results
        st.download_button("Export Results to CSV", "This would download backtest results in the full application", "backtest_results.csv")

def show_ai_assistant(data):
    st.title("AI Trading Assistant")
    
    # Assistant interface
    st.markdown("""
    The AI Trading Assistant can help you with:
    - Analyzing trading patterns
    - Explaining trading concepts
    - Providing market insights
    - Reviewing your trading strategy
    - Answering questions about risk management
    """)
    
    # Example questions
    st.subheader("Common Questions")
    
    example_questions = [
        "What is a break and retest pattern?",
        "How can I identify a good liquidity sweep setup?",
        "What's the difference between support and resistance?",
        "How should I manage risk with this strategy?",
        "Which indicators work well with break and retest patterns?"
    ]
    
    selected_question = st.selectbox("Select a question or type your own below", 
                                    [""] + example_questions)
    
    # Question input
    user_question = st.text_area("Your question", selected_question, height=100)
    
    # Include context options
    st.subheader("Include Context")
    col1, col2 = st.columns(2)
    
    with col1:
        include_trade_history = st.checkbox("Include recent trade history", False)
        include_patterns = st.checkbox("Include detected patterns", True)
        
    with col2:
        include_market_data = st.checkbox("Include current market data", True)
        include_strategy_settings = st.checkbox("Include strategy settings", False)
    
    # Ask button
    if st.button("Ask Assistant") and user_question:
        st.markdown("---")
        
        if user_question == "What is a break and retest pattern?":
            answer = """
            A break and retest pattern occurs when price breaks through a significant support or resistance level, 
            then returns to test that level before continuing in the breakout direction. 
            
            For a bullish break and retest:
            1. Price breaks above a resistance level
            2. Price pulls back to test the broken resistance (which now acts as support)
            3. Price bounces off this new support and continues upward
            
            For a bearish break and retest:
            1. Price breaks below a support level
            2. Price pulls back to test the broken support (which now acts as resistance)
            3. Price rejects off this new resistance and continues downward
            
            These patterns are valuable because they:
            - Offer higher-probability entries compared to breakouts without retests
            - Provide clearly defined risk levels (stop loss just beyond the retest point)
            - Often lead to strong momentum in the breakout direction
            
            When trading break and retest patterns, look for confirmation such as:
            - Rejection candlestick patterns at the retest level
            - Lower volume during the retest compared to the breakout
            - Confluence with other technical factors
            """
        
        elif user_question == "How can I identify a good liquidity sweep setup?":
            answer = """
            A good liquidity sweep setup can be identified by these characteristics:
            
            1. Price approaching a level with clustered stop losses (often below recent lows for longs or above recent highs for shorts)
            2. Strong rejection after sweeping the level (quick reversal)
            3. Higher than average volume during the sweep, showing strong participation
            4. Price closing back beyond the swept level on the reversal candle
            5. Previous market structure that suggests accumulation or distribution
            
            The best setups occur at key technical levels where many traders would place stops, creating a pool of liquidity that larger players might target. Watch for price briefly breaking these levels before quickly reversing with strength, suggesting the sweep was engineered to collect liquidity before the actual move.
            
            Some common liquidity sweep zones include:
            - Just below recent swing lows
            - Just above recent swing highs
            - Below obvious support levels
            - Above obvious resistance levels
            - Around key psychological price levels (round numbers)
            
            When you identify a potential liquidity sweep:
            - Wait for confirmation of the reversal
            - Enter in the direction of the reversal
            - Place stop loss beyond the extreme of the sweep
            - Target previous swing points in the direction of the trade
            """
        
        elif user_question == "What's the difference between support and resistance?":
            answer = """
            Support and resistance are key price levels where buying or selling pressure has historically been strong enough to stop or reverse price movement.
            
            **Support**:
            - A price level where buying pressure is strong enough to stop or reverse a downtrend
            - Acts as a "floor" that prevents price from falling further
            - Created by traders willing to buy at that level
            - When broken downward, support often becomes resistance
            
            **Resistance**:
            - A price level where selling pressure is strong enough to stop or reverse an uptrend
            - Acts as a "ceiling" that prevents price from rising further
            - Created by traders willing to sell at that level
            - When broken upward, resistance often becomes support
            
            Key differences:
            - Support is below the current price, resistance is above
            - Support is created by buyers, resistance by sellers
            - Support stops downward movement, resistance stops upward movement
            
            The strength of support and resistance depends on:
            1. The number of times price has respected the level
            2. The timeframe (higher timeframes = stronger levels)
            3. The volume at the level
            4. The recency of the level
            
            Trading strategies using support and resistance:
            - Bounces: Buy at support, sell at resistance
            - Breakouts: Buy when price breaks above resistance, sell when price breaks below support
            - Break and retest: Enter after price returns to test a broken level
            """
        
        elif user_question == "How should I manage risk with this strategy?":
            answer = """
            Effective risk management for break and retest / liquidity sweep strategies:
            
            **Position Sizing**:
            - Risk only 1-2% of your account per trade
            - Calculate position size based on your stop loss placement
            - For smaller accounts, consider risking slightly higher (max 3%) but take fewer trades
            
            **Stop Loss Placement**:
            - For break and retest: Place stop loss just beyond the retest level
            - For liquidity sweeps: Place stop loss beyond the sweep's extreme point
            - Add a small buffer (0.5-1%) to avoid getting stopped out by normal volatility
            
            **Take Profit Strategies**:
            - Use a minimum risk:reward ratio of 1:2
            - Consider scaling out at multiple targets (e.g., 50% at 1:2, 25% at 1:3, 25% at 1:4)
            - For stronger setups, aim for higher risk:reward ratios (1:3 or higher)
            
            **Additional Risk Controls**:
            - Limit maximum open trades (2-3 recommended)
            - Set a maximum daily loss limit (e.g., 4-5% of account)
            - Reduce position size after consecutive losses
            - Do not revenge trade or average down on losing positions
            
            **Market Conditions**:
            - Be more selective in ranging or choppy markets
            - Take larger positions in trending markets with clear direction
            - Reduce position size during major news events or extreme volatility
            
            **Advanced Risk Management**:
            - Use trailing stops once trade moves 1:1 in your favor
            - Move stop loss to breakeven after price achieves 1:1 risk:reward
            - Consider correlations when taking multiple positions
            
            Remember that preservation of capital is your primary goal. Consistent small wins with proper risk management will compound over time.
            """
        
        elif user_question == "Which indicators work well with break and retest patterns?":
            answer = """
            Indicators that work well with break and retest patterns:
            
            **Trend Confirmation Indicators**:
            - Moving Averages (50 EMA, 200 EMA) - to confirm overall trend direction
            - MACD - for trend strength and momentum
            - ADX - to measure trend strength (>25 indicates strong trend)
            
            **Volume Indicators**:
            - Volume - higher volume on breakout, lower on retest is ideal
            - On-Balance Volume (OBV) - to confirm breakout strength
            - Volume Profile - to identify significant price levels
            
            **Support/Resistance Identification**:
            - Fibonacci Retracement - to identify potential retest levels
            - Pivot Points - for key support/resistance levels
            - Bollinger Bands - for dynamic support/resistance
            
            **Momentum Confirmation**:
            - RSI - look for bullish/bearish divergence during retest
            - Stochastic - identify oversold/overbought conditions at retest points
            - Money Flow Index - to confirm buying/selling pressure
            
            **Best Combinations**:
            1. Price action + Volume + Moving Averages
              - Simple but effective for identifying quality breakouts and retests
              
            2. Fibonacci Retracement + RSI + Volume
              - Helps identify precise retest levels and confirm strength
              
            3. EMA (20, 50, 200) + MACD + Volume
              - Good for trend confirmation and momentum evaluation
            
            The most important factor is price action itself - indicators should complement, not replace, your analysis of candlestick patterns and market structure.
            
            Focus on using 2-3 indicators from different categories rather than multiple indicators that provide the same information. This prevents analysis paralysis and conflicting signals.
            """
        
        else:
            answer = """
            In the full application, this would connect to OpenAI to generate a real-time response to your specific question.
            
            The AI assistant would analyze:
            - Your question context
            - Current market conditions
            - Recent pattern detection results
            - Historical trading performance
            
            And provide personalized advice based on your trading strategy and preferences.
            """
        
        st.markdown(f"### Answer:")
        st.markdown(answer)
        
        # Feedback buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.button("👍 Helpful")
        with col2:
            st.button("👎 Not Helpful")

# Run the app
if __name__ == "__main__":
    main()
import os
import random
import datetime
from datetime import timedelta

def print_colored(text, color):
    """Print colored text in the terminal."""
    color_codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "end": "\033[0m"
    }
    print(f"{color_codes.get(color, '')}{text}{color_codes['end']}")

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
    num_candles = 20  # Reduced number for terminal display
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
    for i in range(5):  # Reduced for terminal display
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

def show_dashboard(data, selected_symbol, selected_timeframe):
    """Display dashboard in terminal."""
    print("\n")
    print_colored(f"=== DASHBOARD - {selected_symbol} ({selected_timeframe}) ===", "bold")
    print("\n")
    
    # Account metrics
    print_colored("ACCOUNT METRICS:", "blue")
    print(f"Account Balance: ${data['account']['balance']:,.2f}")
    print(f"Open Positions: {data['account']['open_positions']}")
    
    pnl_color = "green" if data['account']['unrealized_pnl'] >= 0 else "red"
    pnl_sign = "+" if data['account']['unrealized_pnl'] >= 0 else ""
    print(f"Unrealized P&L: ", end="")
    print_colored(f"{pnl_sign}${data['account']['unrealized_pnl']:,.2f}", pnl_color)
    
    daily_color = "green" if data['account']['daily_pnl'] >= 0 else "red"
    daily_sign = "+" if data['account']['daily_pnl'] >= 0 else ""
    print(f"Daily P&L: ", end="")
    print_colored(f"{daily_sign}${data['account']['daily_pnl']:,.2f}", daily_color)
    
    print("\n")
    
    # Recent price data
    print_colored("RECENT PRICE DATA:", "blue")
    
    # Headers
    print(f"{'Date':<22} | {'Open':<10} | {'High':<10} | {'Low':<10} | {'Close':<10} | {'Volume':<8}")
    print("-" * 80)
    
    # Show recent candles
    for candle in data['price_data'][-5:]:
        print(f"{candle['date']:<22} | ${candle['open']:<9,.2f} | ${candle['high']:<9,.2f} | ${candle['low']:<9,.2f} | ${candle['close']:<9,.2f} | {candle['volume']:<8,.2f}")
    
    print("\n")
    
    # Recent patterns
    print_colored("RECENT PATTERNS:", "blue")
    
    for pattern in data['patterns'][:3]:
        strength_color = "green" if pattern['strength'] >= 4 else "yellow" if pattern['strength'] >= 2 else "white"
        print(f"Pattern: ", end="")
        print_colored(f"{pattern['type']}", strength_color, end="")
        print(f" at ${pattern['price']:,.2f} (Strength: {pattern['strength']})")
        print(f"Time: {pattern['timestamp']}")
        print("-" * 40)
    
    print("\n")
    
    # Liquidity levels
    print_colored("LIQUIDITY LEVELS:", "blue")
    
    for level in data['liquidity_levels']:
        level_color = "green" if level['type'] == "Support" else "red"
        print(f"{level['type']}: ", end="")
        print_colored(f"${level['price']:,.2f}", level_color, end="")
        print(f" (Strength: {level['strength']})")
    
    print("\n")
    
    # Recent trades
    print_colored("RECENT TRADES:", "blue")
    
    # Headers
    print(f"{'Date':<22} | {'Symbol':<8} | {'Type':<6} | {'Entry':<10} | {'Exit':<10} | {'Size':<6} | {'Profit':<15}")
    print("-" * 100)
    
    for trade in data['trades'][:3]:
        profit_color = "green" if trade['profit'] >= 0 else "red"
        profit_sign = "+" if trade['profit'] >= 0 else ""
        
        print(f"{trade['entry_date']:<22} | {trade['symbol']:<8} | {trade['type']:<6} | ${trade['entry_price']:<9,.2f} | ${trade['exit_price']:<9,.2f} | {trade['size']:<6} | ", end="")
        print_colored(f"{profit_sign}{trade['profit']}% (${trade['profit_usd']:,.2f})", profit_color)

def show_pattern_analysis(data):
    """Display pattern analysis in terminal."""
    print("\n")
    print_colored("=== PATTERN ANALYSIS ===", "bold")
    print("\n")
    
    # Pattern explanations
    print_colored("PATTERN TYPES:", "blue")
    print("\n1. Break and Retest Pattern:")
    print("   A price movement where the price breaks through a significant support or")
    print("   resistance level, then returns to test that level before continuing in")
    print("   the breakout direction.")
    print("\n2. Liquidity Sweep Pattern:")
    print("   A brief price movement beyond a key level where stop losses are clustered,")
    print("   triggering those stops, before reversing direction quickly.")
    print("\n3. Support/Resistance Patterns:")
    print("   Support Bounce: Price bounces up from an established support level.")
    print("   Resistance Rejection: Price rejects down from an established resistance level.")
    print("\n4. Candlestick Patterns:")
    print("   Common formations like Hammer, Evening Star, Engulfing patterns, and Doji")
    print("   that indicate potential reversals or continuations.")
    
    print("\n")
    
    # Currently detected patterns
    print_colored("CURRENTLY DETECTED PATTERNS:", "blue")
    
    for pattern in data['patterns']:
        strength_color = "green" if pattern['strength'] >= 4 else "yellow" if pattern['strength'] >= 2 else "white"
        print_colored(f"► {pattern['type']} at ${pattern['price']:,.2f} (Strength: {pattern['strength']})", strength_color)
        print(f"  Time: {pattern['timestamp']}")
        print(f"  Description: {pattern['description']}")
        print("-" * 60)

def show_strategy_configuration():
    """Display strategy configuration in terminal."""
    print("\n")
    print_colored("=== STRATEGY CONFIGURATION ===", "bold")
    print("\n")
    
    # Strategy selection
    print_colored("TRADING STRATEGY:", "blue")
    print("Selected: Break and Retest + Liquidity Sweep")
    print("\n")
    
    # Risk management
    print_colored("RISK MANAGEMENT:", "blue")
    print("Risk per trade: 1.0% of account balance")
    print("Take profit multiplier: 2.5x risk")
    print("Maximum concurrent trades: 3")
    print("Use trailing stop loss: Yes (Activation at 1.0%)")
    print("\n")
    
    # Trading conditions
    print_colored("TRADING CONDITIONS:", "blue")
    print("Trading days: Monday, Tuesday, Wednesday, Thursday, Friday")
    print("Trading hours: 00:00 - 23:00 UTC")
    print("Trade execution mode: Semi-automatic")
    print("Order types: Smart (context dependent)")
    print("Avoid trading before major news events: Yes")

def show_backtesting(data):
    """Display backtesting in terminal."""
    print("\n")
    print_colored("=== STRATEGY BACKTESTING ===", "bold")
    print("\n")
    
    # Backtest parameters
    print_colored("BACKTEST PARAMETERS:", "blue")
    print(f"Start date: {(datetime.datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}")
    print(f"End date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    print("Timeframe: 1h")
    print("Strategy: Break and Retest + Liquidity Sweep")
    print("Initial capital: $10,000")
    print("\n")
    
    # Performance metrics
    print_colored("BACKTEST RESULTS:", "blue")
    print(f"Total Return: {data['performance']['total_return']}%")
    print(f"Win Rate: {data['performance']['win_rate']}%")
    print(f"Profit Factor: {data['performance']['profit_factor']}")
    print(f"Max Drawdown: {data['performance']['max_drawdown']}%")
    print(f"Sharpe Ratio: {data['performance']['sharpe_ratio']}")
    print("\n")
    
    # Trade list
    print_colored("TRADE LIST:", "blue")
    
    # Headers
    print(f"{'Entry Date':<22} | {'Exit Date':<22} | {'Type':<6} | {'Entry':<10} | {'Exit':<10} | {'Profit':<15}")
    print("-" * 100)
    
    for trade in data['trades']:
        profit_color = "green" if trade['profit'] >= 0 else "red"
        profit_sign = "+" if trade['profit'] >= 0 else ""
        
        print(f"{trade['entry_date']:<22} | {trade['exit_date']:<22} | {trade['type']:<6} | ${trade['entry_price']:<9,.2f} | ${trade['exit_price']:<9,.2f} | ", end="")
        print_colored(f"{profit_sign}{trade['profit']}%", profit_color)

def show_ai_assistant():
    """Display AI assistant in terminal."""
    print("\n")
    print_colored("=== AI TRADING ASSISTANT ===", "bold")
    print("\n")
    
    print("The AI Trading Assistant can help you with:")
    print("- Analyzing trading patterns")
    print("- Explaining trading concepts")
    print("- Providing market insights")
    print("- Reviewing your trading strategy")
    print("- Answering questions about risk management")
    print("\n")
    
    print_colored("EXAMPLE QUESTIONS:", "blue")
    print("1. What is a break and retest pattern?")
    print("2. How can I identify a good liquidity sweep setup?")
    print("3. What's the difference between support and resistance?")
    print("4. How should I manage risk with this strategy?")
    print("5. Which indicators work well with break and retest patterns?")
    print("\n")
    
    print_colored("SAMPLE RESPONSE:", "blue")
    print('Q: What is a break and retest pattern?')
    print('A: A break and retest pattern occurs when price breaks through a significant')
    print('   support or resistance level, then returns to test that level before')
    print('   continuing in the breakout direction. For a bullish break and retest,')
    print('   price breaks above resistance, pulls back to test the broken resistance')
    print('   (now support), and then continues upward. For a bearish break and retest,')
    print('   price breaks below support, pulls back to test the broken support')
    print('   (now resistance), and then continues downward. These patterns are valuable')
    print('   because they offer traders a higher-probability entry with a clearly')
    print('   defined risk level.')

def main():
    """Main function to run the terminal-based UI preview."""
    # Clear screen
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print_colored("██████╗ ██╗████████╗ ██████╗ ███████╗████████╗", "cyan")
    print_colored("██╔══██╗██║╚══██╔══╝██╔════╝ ██╔════╝╚══██╔══╝", "cyan")
    print_colored("██████╔╝██║   ██║   ██║  ███╗█████╗     ██║   ", "cyan")
    print_colored("██╔══██╗██║   ██║   ██║   ██║██╔══╝     ██║   ", "cyan")
    print_colored("██████╔╝██║   ██║   ╚██████╔╝███████╗   ██║   ", "cyan")
    print_colored("╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ", "cyan")
    print_colored("CRYPTO TRADING BOT - TERMINAL PREVIEW", "bold")
    print("\n")
    
    # Check API status
    api_status = check_api_status()
    
    print_colored("API CONFIGURATION:", "blue")
    if api_status["openai"]:
        print_colored("OpenAI API: Connected ✓", "green")
    else:
        print_colored("OpenAI API: Not Connected ✗", "red")
        
    if api_status["bitget"]:
        print_colored("Bitget API: Connected ✓", "green")
    else:
        print_colored("Bitget API: Not Connected ✗", "red")
    
    print("\n")
    print("This is a terminal-based preview of the Crypto Trading Bot interface.")
    print("The full application would include interactive charts and real-time data.")
    print("\n")
    
    # Generate mock data
    data = generate_mock_data()
    
    # Menu system
    while True:
        print_colored("MAIN MENU:", "bold")
        print("1. Dashboard")
        print("2. Pattern Analysis")
        print("3. Strategy Configuration")
        print("4. Backtesting")
        print("5. AI Assistant")
        print("0. Exit Preview")
        print("\n")
        
        choice = input("Select option (0-5): ")
        
        # Clear screen
        os.system('clear' if os.name != 'nt' else 'cls')
        
        if choice == "1":
            show_dashboard(data, "BTC/USDT", "1h")
        elif choice == "2":
            show_pattern_analysis(data)
        elif choice == "3":
            show_strategy_configuration()
        elif choice == "4":
            show_backtesting(data)
        elif choice == "5":
            show_ai_assistant()
        elif choice == "0":
            print("Exiting preview. Thank you for using the Crypto Trading Bot!")
            break
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to return to the main menu...")
        
        # Clear screen
        os.system('clear' if os.name != 'nt' else 'cls')

if __name__ == "__main__":
    main()
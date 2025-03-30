import os
import random
import datetime
from datetime import timedelta

def print_colored(text, color, end="\n"):
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
    print(f"{color_codes.get(color, '')}{text}{color_codes['end']}", end=end)

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

# Main function - show all preview sections at once
def main():
    # Clear screen
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print_colored("██████╗ ██╗████████╗ ██████╗ ███████╗████████╗", "cyan")
    print_colored("██╔══██╗██║╚══██╔══╝██╔════╝ ██╔════╝╚══██╔══╝", "cyan")
    print_colored("██████╔╝██║   ██║   ██║  ███╗█████╗     ██║   ", "cyan")
    print_colored("██╔══██╗██║   ██║   ██║   ██║██╔══╝     ██║   ", "cyan")
    print_colored("██████╔╝██║   ██║   ╚██████╔╝███████╗   ██║   ", "cyan")
    print_colored("╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ", "cyan")
    print_colored("CRYPTO TRADING BOT - DASHBOARD PREVIEW", "bold")
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
    print("This is a preview of the Crypto Trading Bot's Dashboard interface.")
    print("The full application would include interactive charts and real-time data.")
    print("\n")
    
    # Generate mock data
    data = generate_mock_data()
    
    # Show the dashboard
    show_dashboard(data, "BTC/USDT", "1h")
    
    # Show pattern analysis
    show_pattern_analysis(data)
    
    print_colored("\n=== FULL APPLICATION FEATURES ===", "bold")
    print("\nThe complete application would include:")
    print("1. Interactive price charts with technical indicators")
    print("2. Real-time data from Bitget Exchange")
    print("3. Automated trading based on detected patterns")
    print("4. Strategy backtesting and optimization")
    print("5. AI-powered trading insights using OpenAI")
    print("6. Performance tracking and analytics")
    print("\nThank you for previewing the Crypto Trading Bot!")

if __name__ == "__main__":
    main()
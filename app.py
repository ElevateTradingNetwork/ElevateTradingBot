import os
import sys
import random
from datetime import datetime, timedelta
import time

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

def generate_mock_data(selected_symbol="BTC/USDT"):
    """Generate mock data for demonstration."""
    # Mock candlestick data
    num_candles = 20  # Reduced number for terminal display
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
    symbols = ["BTC/USDT", "ETH/USDT", "WIF/USDT"]
    
    for i in range(5):  # Reduced for terminal display
        entry_idx = random.randint(0, len(price_data) - 2)
        exit_idx = entry_idx + random.randint(1, len(price_data) - entry_idx - 1)
        
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

def show_dashboard(data, selected_symbol, selected_timeframe):
    """Display dashboard in terminal."""
    os.system('clear' if os.name != 'nt' else 'cls')
    print_colored("██████╗ ██╗████████╗ ██████╗ ███████╗████████╗", "cyan")
    print_colored("██╔══██╗██║╚══██╔══╝██╔════╝ ██╔════╝╚══██╔══╝", "cyan")
    print_colored("██████╔╝██║   ██║   ██║  ███╗█████╗     ██║   ", "cyan")
    print_colored("██╔══██╗██║   ██║   ██║   ██║██╔══╝     ██║   ", "cyan")
    print_colored("██████╔╝██║   ██║   ╚██████╔╝███████╗   ██║   ", "cyan")
    print_colored("╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ", "cyan")
    print_colored("CRYPTO TRADING BOT - INTERACTIVE DASHBOARD", "bold")
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
    os.system('clear' if os.name != 'nt' else 'cls')
    print_colored("██████╗ ██╗████████╗ ██████╗ ███████╗████████╗", "cyan")
    print_colored("██╔══██╗██║╚══██╔══╝██╔════╝ ██╔════╝╚══██╔══╝", "cyan")
    print_colored("██████╔╝██║   ██║   ██║  ███╗█████╗     ██║   ", "cyan")
    print_colored("██╔══██╗██║   ██║   ██║   ██║██╔══╝     ██║   ", "cyan")
    print_colored("██████╔╝██║   ██║   ╚██████╔╝███████╗   ██║   ", "cyan")
    print_colored("╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ", "cyan")
    print_colored("CRYPTO TRADING BOT - PATTERN ANALYSIS", "bold")
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

def show_ai_assistant():
    """Display AI trading assistant in terminal."""
    os.system('clear' if os.name != 'nt' else 'cls')
    print_colored("██████╗ ██╗████████╗ ██████╗ ███████╗████████╗", "cyan")
    print_colored("██╔══██╗██║╚══██╔══╝██╔════╝ ██╔════╝╚══██╔══╝", "cyan")
    print_colored("██████╔╝██║   ██║   ██║  ███╗█████╗     ██║   ", "cyan")
    print_colored("██╔══██╗██║   ██║   ██║   ██║██╔══╝     ██║   ", "cyan")
    print_colored("██████╔╝██║   ██║   ╚██████╔╝███████╗   ██║   ", "cyan")
    print_colored("╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ", "cyan")
    print_colored("CRYPTO TRADING BOT - AI ASSISTANT", "bold")
    print("\n")
    
    print_colored("=== AI TRADING ASSISTANT ===", "bold")
    print("\n")
    
    # Example questions and responses
    questions_and_answers = [
        (
            "What is a break and retest pattern?",
            "A break and retest pattern occurs when price breaks through a significant support or resistance level, then returns to test that level before continuing in the breakout direction. For a bullish break and retest, price breaks above resistance, pulls back to test the broken resistance (now support), and then continues upward. For a bearish break and retest, price breaks below support, pulls back to test the broken support (now resistance), and then continues downward. These patterns are valuable because they offer traders a higher-probability entry with a clearly defined risk level."
        ),
        (
            "How can I identify a good liquidity sweep setup?",
            "A good liquidity sweep setup can be identified by these characteristics:\n\n1. Price approaching a level with clustered stop losses (often below recent lows for longs or above recent highs for shorts)\n2. Strong rejection after sweeping the level (quick reversal)\n3. Higher than average volume during the sweep, showing strong participation\n4. Price closing back beyond the swept level on the reversal candle\n5. Previous market structure that suggests accumulation or distribution\n\nThe best setups occur at key technical levels where many traders would place stops, creating a pool of liquidity that larger players might target. Watch for price briefly breaking these levels before quickly reversing with strength, suggesting the sweep was engineered to collect liquidity before the actual move."
        ),
        (
            "What are the key differences between trading WIF/USDT vs. BTC/USDT?",
            "Trading WIF/USDT vs. BTC/USDT involves several key differences:\n\n1. Volatility: WIF typically exhibits higher volatility than BTC, which creates both greater opportunity and risk. Price swings in WIF can be more extreme percentage-wise.\n\n2. Liquidity: BTC/USDT pairs generally have much higher liquidity, meaning tighter spreads and less slippage when entering and exiting positions. WIF may experience more significant price impact with larger orders.\n\n3. Market forces: BTC often leads the broader crypto market, while WIF and other altcoins may follow BTC's general direction but with amplified movements. This creates potential for both larger gains and losses.\n\n4. Market information: BTC has more extensive market analysis, institutional coverage, and on-chain data available compared to WIF, which may have less reliable signals and indicators.\n\n5. Risk profile: WIF generally represents a higher risk, potentially higher reward opportunity compared to the relatively more established Bitcoin market.\n\nConsider position sizing appropriately when trading WIF to account for the increased volatility and risk."
        )
    ]
    
    # Show simulated QA
    for i, (q, a) in enumerate(questions_and_answers):
        print_colored(f"Question {i+1}: {q}", "yellow")
        print(f"\nAnswer: {a}")
        print("\n" + "-" * 80 + "\n")

def interactive_menu():
    """Display an interactive menu for the trading bot."""
    symbols = ["BTC/USDT", "ETH/USDT", "WIF/USDT"]
    timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
    
    selected_symbol = "BTC/USDT"
    selected_timeframe = "1h"
    
    data = generate_mock_data(selected_symbol)
    
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print_colored("██████╗ ██╗████████╗ ██████╗ ███████╗████████╗", "cyan")
        print_colored("██╔══██╗██║╚══██╔══╝██╔════╝ ██╔════╝╚══██╔══╝", "cyan")
        print_colored("██████╔╝██║   ██║   ██║  ███╗█████╗     ██║   ", "cyan")
        print_colored("██╔══██╗██║   ██║   ██║   ██║██╔══╝     ██║   ", "cyan")
        print_colored("██████╔╝██║   ██║   ╚██████╔╝███████╗   ██║   ", "cyan")
        print_colored("╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ", "cyan")
        print_colored("CRYPTO TRADING BOT - INTERACTIVE MODE", "bold")
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
        
        print(f"Currently Selected: {selected_symbol} - {selected_timeframe}")
        print("\nMAIN MENU")
        print("1. Dashboard")
        print("2. Pattern Analysis")
        print("3. AI Trading Assistant")
        print("4. Change Trading Pair")
        print("5. Change Timeframe")
        print("6. Refresh Data")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            # Dashboard
            show_dashboard(data, selected_symbol, selected_timeframe)
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            # Pattern Analysis
            show_pattern_analysis(data)
            input("\nPress Enter to return to menu...")
        elif choice == "3":
            # AI Trading Assistant
            show_ai_assistant()
            input("\nPress Enter to return to menu...")
        elif choice == "4":
            # Change Trading Pair
            os.system('clear' if os.name != 'nt' else 'cls')
            print("Available Trading Pairs:")
            for i, symbol in enumerate(symbols):
                print(f"{i+1}. {symbol}")
            
            symbol_choice = input("\nSelect trading pair (1-3): ")
            try:
                idx = int(symbol_choice) - 1
                if 0 <= idx < len(symbols):
                    selected_symbol = symbols[idx]
                    data = generate_mock_data(selected_symbol)
                    print(f"\nSwitch to {selected_symbol} successful!")
                    time.sleep(1)
            except ValueError:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
        elif choice == "5":
            # Change Timeframe
            os.system('clear' if os.name != 'nt' else 'cls')
            print("Available Timeframes:")
            for i, tf in enumerate(timeframes):
                print(f"{i+1}. {tf}")
            
            tf_choice = input("\nSelect timeframe (1-6): ")
            try:
                idx = int(tf_choice) - 1
                if 0 <= idx < len(timeframes):
                    selected_timeframe = timeframes[idx]
                    print(f"\nSwitch to {selected_timeframe} timeframe successful!")
                    time.sleep(1)
            except ValueError:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
        elif choice == "6":
            # Refresh data
            print("\nRefreshing market data...")
            data = generate_mock_data(selected_symbol)
            time.sleep(1)
            print("Data refreshed successfully!")
            time.sleep(1)
        elif choice == "7":
            # Exit
            print("\nExiting Crypto Trading Bot. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    interactive_menu()
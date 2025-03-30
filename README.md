# Crypto Trading Bot

A cryptocurrency trading bot using break, retest, and liquidity sweep strategies with Bitget integration and interactive analysis capabilities.

## Overview

This trading bot is designed to identify and trade specific technical patterns in cryptocurrency markets:

1. **Break and Retest Patterns**: When price breaks through a support/resistance level and then returns to test it before continuing in the breakout direction.
2. **Liquidity Sweep Patterns**: When price briefly breaks a key level to trigger stops before reversing direction.
3. **Support/Resistance Bounces**: When price reacts strongly at established support or resistance levels.

The bot connects to the Bitget exchange API to fetch real-time data, identify trading opportunities, and optionally execute trades based on detected patterns.

## Features

- **Pattern Recognition**: Automated detection of break and retest patterns, liquidity sweeps, and candlestick patterns
- **Bitget Exchange Integration**: Real-time price data and trading capabilities
- **AI-Powered Analysis**: OpenAI integration for trading strategy insights and pattern analysis
- **Backtesting**: Test strategies against historical data with performance metrics
- **Interactive Interface**: Visual representation of patterns and trading signals (when using Streamlit UI)

## Files Structure

- `basic_demo.py` - Command-line demonstration of key features
- `simple_app.py` - Text-based preview of the Streamlit interface
- `app.py` - Full Streamlit web interface (requires additional dependencies)
- `utils/` - Core functionality modules:
  - `api_client.py` - Bitget exchange API integration
  - `pattern_recognition.py` - Technical pattern detection algorithms
  - `strategy.py` - Trading strategy implementation
  - `backtester.py` - Backtesting engine
  - `chart_utils.py` - Visualization utilities
  - `ai_assistant.py` - OpenAI integration for trading insights
  - `performance_tracker.py` - Strategy performance metrics

## Requirements

- Python 3.8+
- API keys for Bitget exchange
- OpenAI API key (for AI-powered trading assistance)

### Dependencies

- pandas
- numpy
- ccxt (for exchange API integration)
- openai
- streamlit (for web interface)
- plotly (for interactive charts)
- pandas-ta (for technical indicators)

## Getting Started

1. Clone the repository
2. Set up environment variables for API keys:
   ```
   export BITGET_API_KEY="your_api_key"
   export BITGET_API_SECRET="your_api_secret"
   export BITGET_API_PASSWORD="your_api_password"
   export OPENAI_API_KEY="your_openai_key"
   ```

3. Install dependencies:
   ```
   pip install pandas numpy ccxt openai streamlit plotly pandas-ta
   ```

4. Run the basic demo:
   ```
   python basic_demo.py
   ```

5. Or run the full application:
   ```
   streamlit run app.py
   ```

## Trading Strategies

### Break and Retest Strategy

The Break and Retest strategy identifies when price breaks through a significant support or resistance level, then returns to test that level before continuing in the breakout direction. The strategy enters trades after the retest is confirmed with a defined stop loss below/above the retest point.

### Liquidity Sweep Strategy

The Liquidity Sweep strategy identifies when price briefly breaks beyond a significant level where stop losses are clustered, then quickly reverses. The strategy enters trades after confirming the rejection and reversal, with stop loss beyond the sweep's extreme point.

## Risk Management

The bot incorporates position sizing based on account risk percentage, with default settings:
- 1% risk per trade
- Maximum of 3 concurrent open trades
- Risk:reward ratios from 1:2 to 1:5 depending on pattern strength

## Disclaimer

Trading cryptocurrencies carries significant risk. This trading bot is provided for educational and research purposes only. Always test thoroughly in a demo environment before using with real funds. Past performance is not indicative of future results.
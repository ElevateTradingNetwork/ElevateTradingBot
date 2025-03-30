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

- Python 3.11+
- API keys for Bitget exchange
- OpenAI API key (for AI-powered trading assistance)

### Dependencies

The project uses Poetry for dependency management. All dependencies are defined in the `pyproject.toml` file:

- pandas
- numpy
- ccxt (for exchange API integration)
- openai
- streamlit (for web interface)
- plotly (for interactive charts)
- pandas-ta (for technical indicators)
- joblib (for data persistence)

## Getting Started

1. Clone the repository

2. Set up environment variables by creating a `.env` file:
   ```
   # Copy the example file
   cp .env.example .env
   
   # Edit with your actual API keys
   nano .env
   ```
   
   Your `.env` file should contain:
   ```
   BITGET_API_KEY=your_api_key
   BITGET_API_SECRET=your_api_secret
   BITGET_API_PASSWORD=your_api_password
   OPENAI_API_KEY=your_openai_key
   ```

3. Install dependencies using Poetry:
   ```
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install
   ```
   
   Or install the dependencies directly:
   ```
   pip install streamlit pandas numpy plotly ccxt pandas-ta joblib openai
   ```

4. Run the basic demo:
   ```
   # Using Poetry
   poetry run demo
   
   # Or directly
   python basic_demo.py
   ```

5. Run the dashboard preview:
   ```
   # Using Poetry
   poetry run dashboard
   
   # Or directly
   python show_dashboard.py
   ```

6. Run the full Streamlit application:
   ```
   # Using Poetry
   poetry run streamlit run app.py --server.port 5000
   
   # Or directly
   streamlit run app.py --server.port 5000
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

## Development

### Development with Poetry

This project uses Poetry for dependency management and packaging. Here are some useful commands for development:

```bash
# Activate the virtual environment
poetry shell

# Add a new dependency
poetry add package_name

# Add a development dependency
poetry add --group dev package_name

# Update dependencies
poetry update

# Run a script in the virtual environment without activating it
poetry run python script.py

# Build the package
poetry build
```

### Project Scripts

The project has the following configured scripts:

- `poetry run demo` - Run the basic demo (basic_demo.py)
- `poetry run dashboard` - Run the dashboard preview (show_dashboard.py)
- `poetry run trading-bot` - Run the interactive app (app.py)

## Deployment on Render

This project is configured for easy deployment on Render. Follow these steps:

1. **Sign up for a Render account** at [render.com](https://render.com) if you don't already have one.

2. **Fork or push this repository** to your GitHub, GitLab, or Bitbucket account.

3. **Create a new Web Service** on Render:
   - Click "New" and select "Web Service"
   - Connect your repository
   - Name your service (e.g., "crypto-trading-bot")
   - Select the "Python 3" runtime environment
   - Leave the build command as `pip install -r requirements.txt`
   - Set the start command to: `streamlit run app_streamlit.py --server.port $PORT --server.address 0.0.0.0`

4. **Set up environment variables**:
   - In the Render dashboard, go to your web service
   - Navigate to "Environment" tab
   - Add the following environment variables:
     - `BITGET_API_KEY` - Your Bitget API key
     - `BITGET_API_SECRET` - Your Bitget API secret
     - `BITGET_API_PASSWORD` - Your Bitget API password
     - `OPENAI_API_KEY` - Your OpenAI API key

5. **Deploy the service**:
   - Click "Create Web Service"
   - Render will build and deploy your application

Alternatively, if you have the Render CLI installed, you can deploy using the included render.yaml file:

```bash
render deploy
```

### Render Features

When using Render for deployment, you get these benefits:
- Automatic HTTPS/TLS certificate
- Global CDN for faster loading
- Continuous deployment from GitHub/GitLab
- Automatic scaling
- Real-time logs and metrics

## Disclaimer

Trading cryptocurrencies carries significant risk. This trading bot is provided for educational and research purposes only. Always test thoroughly in a demo environment before using with real funds. Past performance is not indicative of future results.
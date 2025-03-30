import os
from openai import OpenAI

class TradingAssistant:
    """
    An AI assistant that can answer trading related questions.
    """
    
    def __init__(self):
        """
        Initialize the trading assistant.
        """
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = """
        You are a cryptocurrency trading assistant specializing in break, retest, and liquidity sweep strategies.
        
        Your knowledge includes:
        1. Technical analysis of cryptocurrency markets
        2. Pattern recognition for breakouts, retests, and liquidity sweeps
        3. Risk management for crypto trading
        4. Market structure and order flow concepts
        5. Trading psychology and discipline
        
        When answering questions:
        - Be specific and practical, avoid generic advice
        - Explain concepts clearly with examples when possible
        - If asked about specific charts or patterns, ask for more information if needed
        - Always emphasize risk management principles
        - Don't make price predictions or give financial advice
        - If you don't know something, be honest and don't make up information
        
        Your goal is to help traders understand the concepts and strategies they're using,
        but not to make trading decisions for them.
        """
    
    def ask_question(self, question, trading_history=None, current_patterns=None):
        """
        Ask a question to the trading assistant.
        
        Args:
            question (str): The user's question
            trading_history (dict, optional): Recent trading history for context
            current_patterns (list, optional): Currently identified patterns
            
        Returns:
            str: The assistant's response
        """
        if not self.api_key:
            return "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        
        # Prepare context from trading history and patterns if available
        context = ""
        if trading_history:
            context += "\nRecent trading performance:\n"
            if 'metrics' in trading_history:
                metrics = trading_history['metrics']
                context += f"Win rate: {metrics.get('win_rate', 0):.2%}\n"
                context += f"Profit factor: {metrics.get('profit_factor', 0):.2f}\n"
                context += f"Total trades: {metrics.get('total_trades', 0)}\n"
                context += f"Average profit: {metrics.get('average_profit', 0):.2f}\n"
                context += f"Average loss: {metrics.get('average_loss', 0):.2f}\n"
            
            if 'trades' in trading_history and trading_history['trades']:
                context += "\nLast 3 trades:\n"
                for i, trade in enumerate(trading_history['trades'][:3]):
                    context += f"Trade {i+1}: {trade['type']} {trade['entry_price']} -> {trade['exit_price']}, Profit: {trade['profit']:.2f}\n"
        
        if current_patterns:
            context += "\nCurrently identified patterns:\n"
            for i, pattern in enumerate(current_patterns[:5]):
                context += f"Pattern {i+1}: {pattern['type']} at price {pattern['price']:.2f} with strength {pattern.get('strength', 0)}\n"
        
        # Construct the full prompt
        full_prompt = f"{question}\n\n{context}" if context else question
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with the AI assistant: {str(e)}"
    
    def analyze_pattern(self, pattern_data):
        """
        Get an AI-powered analysis of a specific trading pattern.
        
        Args:
            pattern_data (dict): Data about the pattern
            
        Returns:
            str: Analysis of the pattern
        """
        if not self.api_key:
            return "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        
        # Construct a prompt describing the pattern
        pattern_prompt = f"""
        Please analyze this trading pattern:
        
        Pattern type: {pattern_data.get('type', 'Unknown')}
        Price level: {pattern_data.get('price', 0):.2f}
        Strength: {pattern_data.get('strength', 0)}
        Additional information: {pattern_data.get('subtype', '')}
        
        Provide a brief analysis of:
        1. What this pattern typically indicates
        2. Key levels to watch
        3. Potential risk management approach
        4. Common mistakes traders make with this pattern
        """
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": pattern_prompt}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing pattern: {str(e)}"
    
    def evaluate_trading_plan(self, strategy_settings, performance_metrics):
        """
        Get AI feedback on a trading plan and performance.
        
        Args:
            strategy_settings (dict): Current strategy settings
            performance_metrics (dict): Current performance metrics
            
        Returns:
            str: Analysis and suggestions
        """
        if not self.api_key:
            return "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        
        # Construct a prompt analyzing the strategy and performance
        prompt = f"""
        Please evaluate this trading plan and performance:
        
        Strategy Settings:
        Risk percentage per trade: {strategy_settings.get('risk_percentage', 1.0)}%
        Max open trades: {strategy_settings.get('max_open_trades', 3)}
        
        Performance Metrics:
        Win rate: {performance_metrics.get('win_rate', 0):.2%}
        Profit factor: {performance_metrics.get('profit_factor', 0):.2f}
        Total trades: {performance_metrics.get('total_trades', 0)}
        Average profit: {performance_metrics.get('average_profit', 0):.2f}
        Average loss: {performance_metrics.get('average_loss', 0):.2f}
        Max drawdown: {performance_metrics.get('max_drawdown', 0):.2%}
        Sharpe ratio: {performance_metrics.get('sharpe_ratio', 0):.2f}
        
        Please provide:
        1. An analysis of the current performance
        2. Areas of strength in the strategy
        3. Areas that need improvement
        4. Specific suggestions for optimizing the strategy parameters
        5. Risk management advice based on these metrics
        """
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error evaluating trading plan: {str(e)}"

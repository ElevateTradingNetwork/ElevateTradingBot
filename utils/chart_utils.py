import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class ChartUtils:
    """
    Utility functions for creating interactive charts.
    """
    
    @staticmethod
    def create_candlestick_chart(df, title='Price Chart', show_volume=True, patterns=None, liquidity_levels=None, trades=None):
        """
        Create an interactive candlestick chart with technical indicators.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV and indicator data
            title (str): Chart title
            show_volume (bool): Whether to show volume
            patterns (list): List of identified patterns
            liquidity_levels (list): List of liquidity levels
            trades (list): List of trades for visualization
            
        Returns:
            plotly.graph_objects.Figure: Interactive chart
        """
        if df.empty:
            return go.Figure()
        
        # Create subplots: price with indicators and volume
        row_heights = [0.7, 0.3] if show_volume else [1]
        rows = 2 if show_volume else 1
        
        fig = make_subplots(
            rows=rows, 
            cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=[title, 'Volume'] if show_volume else [title]
        )
        
        # Convert timestamp to datetime if it exists
        if 'timestamp' in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            x = df['timestamp']
        else:
            x = df.index
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=x,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Add EMAs if they exist
        if 'ema20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=df['ema20'],
                    line=dict(color='blue', width=1),
                    name='EMA 20'
                ),
                row=1, col=1
            )
        
        if 'ema50' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=df['ema50'],
                    line=dict(color='orange', width=1),
                    name='EMA 50'
                ),
                row=1, col=1
            )
        
        if 'ema100' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=df['ema100'],
                    line=dict(color='purple', width=1),
                    name='EMA 100'
                ),
                row=1, col=1
            )
        
        # Add Bollinger Bands if they exist
        if 'BBL_20_2.0' in df.columns and 'BBU_20_2.0' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=df['BBU_20_2.0'],
                    line=dict(color='rgba(0,128,0,0.3)', width=1),
                    name='Upper BB',
                    hoverinfo='none'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=df['BBL_20_2.0'],
                    line=dict(color='rgba(0,128,0,0.3)', width=1),
                    name='Lower BB',
                    fill='tonexty',
                    fillcolor='rgba(0,128,0,0.1)',
                    hoverinfo='none'
                ),
                row=1, col=1
            )
        
        # Add support and resistance levels if they exist
        if 'support' in df.columns:
            support_levels = df[~df['support'].isna()]
            if not support_levels.empty:
                for idx, row in support_levels.iterrows():
                    fig.add_shape(
                        type="line",
                        x0=x[0],
                        y0=row['support'],
                        x1=x.iloc[-1] if hasattr(x, 'iloc') else x[-1],
                        y1=row['support'],
                        line=dict(color="green", width=1, dash="dot"),
                        row=1, col=1
                    )
        
        if 'resistance' in df.columns:
            resistance_levels = df[~df['resistance'].isna()]
            if not resistance_levels.empty:
                for idx, row in resistance_levels.iterrows():
                    fig.add_shape(
                        type="line",
                        x0=x[0],
                        y0=row['resistance'],
                        x1=x.iloc[-1] if hasattr(x, 'iloc') else x[-1],
                        y1=row['resistance'],
                        line=dict(color="red", width=1, dash="dot"),
                        row=1, col=1
                    )
        
        # Add liquidity levels if provided
        if liquidity_levels:
            for level in liquidity_levels:
                fig.add_shape(
                    type="line",
                    x0=x[0],
                    y0=level['price'],
                    x1=x.iloc[-1] if hasattr(x, 'iloc') else x[-1],
                    y1=level['price'],
                    line=dict(
                        color="rgba(255, 165, 0, 0.7)",
                        width=2,
                        dash="solid"
                    ),
                    row=1, col=1
                )
                
                # Add annotation for liquidity level
                fig.add_annotation(
                    x=x.iloc[-1] if hasattr(x, 'iloc') else x[-1],
                    y=level['price'],
                    text=f"Liquidity ({level['strength']:.1f})",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="orange",
                    arrowsize=1,
                    arrowwidth=1,
                    ax=40,
                    ay=0,
                    row=1, col=1
                )
        
        # Add pattern markers if provided
        if patterns:
            for pattern in patterns:
                marker_color = 'green' if pattern['signal'] == 'buy' else 'red'
                
                fig.add_trace(
                    go.Scatter(
                        x=[pattern['date']],
                        y=[pattern['price']],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up' if pattern['signal'] == 'buy' else 'triangle-down',
                            size=12,
                            color=marker_color,
                            line=dict(width=1, color='black')
                        ),
                        name=pattern['type'],
                        text=f"{pattern['type']} {pattern['signal']}",
                        hoverinfo="text"
                    ),
                    row=1, col=1
                )
                
                # Add stop loss and take profit lines
                if 'stop_loss' in pattern:
                    fig.add_shape(
                        type="line",
                        x0=pattern['date'],
                        y0=pattern['stop_loss'],
                        x1=x.iloc[-1] if hasattr(x, 'iloc') else x[-1],
                        y1=pattern['stop_loss'],
                        line=dict(color="red", width=1, dash="dash"),
                        row=1, col=1
                    )
                
                if 'take_profit' in pattern:
                    fig.add_shape(
                        type="line",
                        x0=pattern['date'],
                        y0=pattern['take_profit'],
                        x1=x.iloc[-1] if hasattr(x, 'iloc') else x[-1],
                        y1=pattern['take_profit'],
                        line=dict(color="green", width=1, dash="dash"),
                        row=1, col=1
                    )
        
        # Add trade markers if provided
        if trades:
            for trade in trades:
                entry_color = 'green' if trade['type'] == 'long' else 'red'
                exit_color = 'red' if trade['type'] == 'long' and trade['profit'] < 0 else 'green'
                exit_color = 'green' if trade['type'] == 'short' and trade['profit'] < 0 else exit_color
                
                # Entry marker
                fig.add_trace(
                    go.Scatter(
                        x=[trade['entry_date']],
                        y=[trade['entry_price']],
                        mode='markers',
                        marker=dict(
                            symbol='circle',
                            size=10,
                            color=entry_color,
                            line=dict(width=1, color='black')
                        ),
                        name=f"{trade['type']} Entry",
                        text=f"{trade['type']} Entry at {trade['entry_price']:.2f}",
                        hoverinfo="text"
                    ),
                    row=1, col=1
                )
                
                # Exit marker
                fig.add_trace(
                    go.Scatter(
                        x=[trade['exit_date']],
                        y=[trade['exit_price']],
                        mode='markers',
                        marker=dict(
                            symbol='circle',
                            size=10,
                            color=exit_color,
                            line=dict(width=1, color='black')
                        ),
                        name=f"{trade['type']} Exit",
                        text=f"{trade['type']} Exit at {trade['exit_price']:.2f}, Profit: {trade['profit']:.2f}",
                        hoverinfo="text"
                    ),
                    row=1, col=1
                )
                
                # Line connecting entry and exit
                fig.add_trace(
                    go.Scatter(
                        x=[trade['entry_date'], trade['exit_date']],
                        y=[trade['entry_price'], trade['exit_price']],
                        mode='lines',
                        line=dict(color='rgba(0,0,0,0.5)', width=1, dash='dot'),
                        showlegend=False,
                        hoverinfo="none"
                    ),
                    row=1, col=1
                )
        
        # Add volume chart
        if show_volume and 'volume' in df.columns:
            colors = ['green' if df['close'][i] >= df['open'][i] else 'red' for i in range(len(df))]
            
            fig.add_trace(
                go.Bar(
                    x=x,
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    marker_line_width=0
                ),
                row=2, col=1
            )
            
            # Add volume MA if it exists
            if 'volume_sma' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=df['volume_sma'],
                        line=dict(color='blue', width=1),
                        name='Volume MA'
                    ),
                    row=2, col=1
                )
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            height=800,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Set y-axis for candlestick
        fig.update_yaxes(title_text="Price", row=1, col=1)
        
        # Set y-axis for volume
        if show_volume:
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_performance_chart(equity_curve, trades=None, title='Performance'):
        """
        Create a performance chart showing equity curve and trades.
        
        Args:
            equity_curve (list): List of equity values over time
            trades (list): List of trades
            title (str): Chart title
            
        Returns:
            plotly.graph_objects.Figure: Interactive chart
        """
        if not equity_curve:
            return go.Figure()
        
        # Convert equity curve to DataFrame
        df_equity = pd.DataFrame(equity_curve)
        
        # Create figure
        fig = make_subplots(
            rows=2, 
            cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=[title, 'Drawdown']
        )
        
        # Add equity curve
        fig.add_trace(
            go.Scatter(
                x=df_equity['date'],
                y=df_equity['equity'],
                line=dict(color='blue', width=2),
                name='Equity'
            ),
            row=1, col=1
        )
        
        # Calculate drawdown
        df_equity['peak'] = df_equity['equity'].cummax()
        df_equity['drawdown'] = ((df_equity['peak'] - df_equity['equity']) / df_equity['peak']) * 100
        
        # Add drawdown chart
        fig.add_trace(
            go.Scatter(
                x=df_equity['date'],
                y=df_equity['drawdown'],
                line=dict(color='red', width=1),
                fill='tozeroy',
                fillcolor='rgba(255,0,0,0.1)',
                name='Drawdown %'
            ),
            row=2, col=1
        )
        
        # Add trade markers if provided
        if trades:
            for trade in trades:
                marker_color = 'green' if trade['profit'] > 0 else 'red'
                
                fig.add_trace(
                    go.Scatter(
                        x=[trade['exit_date']],
                        y=[df_equity.loc[df_equity['date'] == trade['exit_date'], 'equity'].iloc[0] 
                           if not df_equity[df_equity['date'] == trade['exit_date']].empty else None],
                        mode='markers',
                        marker=dict(
                            symbol='circle',
                            size=8,
                            color=marker_color,
                            line=dict(width=1, color='black')
                        ),
                        name=f"{trade['type']} Trade",
                        text=f"{trade['type']} {trade['result']}: {trade['profit']:.2f}",
                        hoverinfo="text",
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Equity",
            height=700,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Set y-axis for equity
        fig.update_yaxes(title_text="Equity", row=1, col=1)
        
        # Set y-axis for drawdown
        fig.update_yaxes(title_text="Drawdown %", row=2, col=1)
        
        return fig

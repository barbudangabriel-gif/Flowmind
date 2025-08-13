import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import json
from typing import Dict, List, Any, Tuple

class OptionsStrategyChartGenerator:
    def __init__(self):
        # Set matplotlib style for professional charts
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'profit': '#22C55E',   # Green
            'loss': '#EF4444',     # Red  
            'breakeven': '#F59E0B', # Orange
            'current': '#3B82F6',   # Blue
            'background': '#1F2937' # Dark gray
        }
        
    def generate_strategy_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate both matplotlib and plotly charts for a strategy"""
        strategy_name = strategy.get('strategy_name', '').lower().replace(' ', '_')
        
        if strategy_name in ['bull_call_spread', 'bear_put_spread']:
            return self._generate_vertical_spread_chart(strategy)
        elif strategy_name in ['long_call', 'long_put']:
            return self._generate_directional_chart(strategy)
        elif strategy_name in ['long_straddle', 'long_strangle']:
            return self._generate_volatility_chart(strategy)
        elif strategy_name == 'iron_condor':
            return self._generate_iron_condor_chart(strategy)
        elif strategy_name in ['cash_secured_put', 'covered_call']:
            return self._generate_income_chart(strategy)
        else:
            return self._generate_generic_chart(strategy)
    
    def _generate_vertical_spread_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart for Bull Call Spread / Bear Put Spread"""
        ticker = strategy.get('ticker', 'STOCK')
        strategy_name = strategy.get('strategy_name', 'Vertical Spread')
        underlying_price = strategy.get('entry_logic', {}).get('underlying_price', 100)
        
        # Calculate strikes for spread
        is_call_spread = 'call' in strategy_name.lower()
        is_bull = 'bull' in strategy_name.lower()
        
        if is_bull:
            lower_strike = underlying_price * 0.98
            upper_strike = underlying_price * 1.05
        else:
            lower_strike = underlying_price * 0.95  
            upper_strike = underlying_price * 1.02
        
        # Generate price range
        price_range = np.linspace(underlying_price * 0.85, underlying_price * 1.15, 100)
        
        # Calculate P&L for vertical spread
        if is_call_spread:
            if is_bull:  # Bull Call Spread
                long_call_pl = np.maximum(price_range - lower_strike, 0) - 2  # Premium paid
                short_call_pl = -(np.maximum(price_range - upper_strike, 0) - 2)  # Premium received
                total_pl = long_call_pl + short_call_pl
            else:  # Bear Call Spread (short)
                long_call_pl = np.maximum(price_range - upper_strike, 0) - 1
                short_call_pl = -(np.maximum(price_range - lower_strike, 0) - 3)
                total_pl = long_call_pl + short_call_pl
        else:  # Put spread
            if not is_bull:  # Bear Put Spread
                long_put_pl = np.maximum(upper_strike - price_range, 0) - 2
                short_put_pl = -(np.maximum(lower_strike - price_range, 0) - 1)
                total_pl = long_put_pl + short_put_pl
            else:  # Bull Put Spread (short)
                long_put_pl = np.maximum(lower_strike - price_range, 0) - 1
                short_put_pl = -(np.maximum(upper_strike - price_range, 0) - 3)
                total_pl = long_put_pl + short_put_pl
        
        # Create Plotly chart
        fig = go.Figure()
        
        # Add P&L line
        fig.add_trace(go.Scatter(
            x=price_range.tolist(), 
            y=(total_pl * 100).tolist(),  # Convert to dollars
            mode='lines',
            name='P&L',
            line=dict(color='#3B82F6', width=3),
            hovertemplate='<b>Price: $%{x:.2f}</b><br>P&L: $%{y:.0f}<extra></extra>'
        ))
        
        # Add breakeven lines
        breakeven_points = []
        for i, pl in enumerate(total_pl):
            if abs(pl) < 0.1:  # Close to breakeven
                breakeven_points.append(float(price_range[i]))
        
        # Limit to 2 breakeven points and ensure they're floats
        breakeven_points = breakeven_points[:2]
        for be in breakeven_points:
            fig.add_vline(x=be, line_dash="dash", line_color='#F59E0B', 
                         annotation_text=f"BE: ${be:.2f}")
        
        # Add profit/loss zones
        fig.add_hline(y=0, line_dash="solid", line_color='white', line_width=1)
        
        # Style the chart
        fig.update_layout(
            title=f'{strategy_name} - {ticker}<br><sub>Max Risk vs Max Reward Analysis</sub>',
            xaxis_title='Stock Price at Expiration ($)',
            yaxis_title='Profit/Loss ($)',
            template='plotly_dark',
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add annotations for key levels
        max_profit = np.max(total_pl) * 100
        max_loss = np.min(total_pl) * 100
        
        fig.add_annotation(
            x=underlying_price * 1.1, 
            y=max_profit * 0.8,
            text=f"Max Profit: ${max_profit:.0f}",
            showarrow=False,
            bgcolor='rgba(34, 197, 94, 0.8)',
            bordercolor='#22C55E',
            font=dict(color='white')
        )
        
        fig.add_annotation(
            x=underlying_price * 0.9,
            y=max_loss * 0.8,
            text=f"Max Loss: ${abs(max_loss):.0f}",
            showarrow=False,
            bgcolor='rgba(239, 68, 68, 0.8)', 
            bordercolor='#EF4444',
            font=dict(color='white')
        )
        
        # Convert to JSON for frontend
        plotly_json = fig.to_json()
        
        return {
            'plotly_chart': plotly_json,
            'chart_type': 'vertical_spread',
            'max_profit': float(max_profit),
            'max_loss': float(abs(max_loss)),
            'breakeven_points': breakeven_points
        }
    
    def _generate_directional_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart for Long Call / Long Put"""
        ticker = strategy.get('ticker', 'STOCK')
        strategy_name = strategy.get('strategy_name', 'Directional Play')
        underlying_price = strategy.get('entry_logic', {}).get('underlying_price', 100)
        
        is_call = 'call' in strategy_name.lower()
        strike = underlying_price * (1.02 if is_call else 0.98)
        premium = 3  # Assumed premium
        
        # Generate price range
        price_range = np.linspace(underlying_price * 0.8, underlying_price * 1.2, 100)
        
        # Calculate P&L
        if is_call:
            total_pl = np.maximum(price_range - strike, 0) - premium
        else:
            total_pl = np.maximum(strike - price_range, 0) - premium
        
        # Create Plotly chart
        fig = go.Figure()
        
        # Add P&L line with color coding
        colors = ['#EF4444' if pl < 0 else '#22C55E' for pl in total_pl]
        
        fig.add_trace(go.Scatter(
            x=price_range.tolist(),
            y=(total_pl * 100).tolist(),
            mode='lines',
            name='P&L',
            line=dict(color='#3B82F6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)',
            hovertemplate='<b>Price: $%{x:.2f}</b><br>P&L: $%{y:.0f}<extra></extra>'
        ))
        
        # Add breakeven line
        breakeven = strike + premium if is_call else strike - premium
        fig.add_vline(x=breakeven, line_dash="dash", line_color='#F59E0B',
                     annotation_text=f"Breakeven: ${breakeven:.2f}")
        
        # Add zero line
        fig.add_hline(y=0, line_dash="solid", line_color='white', line_width=1)
        
        # Style the chart
        fig.update_layout(
            title=f'{strategy_name} - {ticker}<br><sub>Unlimited {"Upside" if is_call else "Downside"} Potential</sub>',
            xaxis_title='Stock Price at Expiration ($)',
            yaxis_title='Profit/Loss ($)',
            template='plotly_dark',
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add annotations
        max_loss = premium * 100
        
        fig.add_annotation(
            x=underlying_price * 0.85,
            y=-max_loss * 0.5,
            text=f"Max Loss: ${max_loss:.0f}<br>(Premium Paid)",
            showarrow=False,
            bgcolor='rgba(239, 68, 68, 0.8)',
            bordercolor='#EF4444',
            font=dict(color='white')
        )
        
        fig.add_annotation(
            x=underlying_price * (1.15 if is_call else 0.85),
            y=max_loss * 2,
            text="Unlimited Profit Potential",
            showarrow=False,
            bgcolor='rgba(34, 197, 94, 0.8)',
            bordercolor='#22C55E', 
            font=dict(color='white')
        )
        
        plotly_json = fig.to_json()
        
        return {
            'plotly_chart': plotly_json,
            'chart_type': 'directional',
            'max_loss': float(max_loss),
            'breakeven': float(breakeven)
        }
    
    def _generate_volatility_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart for Long Straddle / Long Strangle"""
        ticker = strategy.get('ticker', 'STOCK')
        strategy_name = strategy.get('strategy_name', 'Volatility Play')
        underlying_price = strategy.get('entry_logic', {}).get('underlying_price', 100)
        
        is_straddle = 'straddle' in strategy_name.lower()
        
        # Set strikes
        if is_straddle:
            call_strike = put_strike = underlying_price
            total_premium = 6  # Both ATM options
        else:  # Strangle
            call_strike = underlying_price * 1.05
            put_strike = underlying_price * 0.95
            total_premium = 4  # OTM options cheaper
        
        # Generate price range
        price_range = np.linspace(underlying_price * 0.7, underlying_price * 1.3, 100)
        
        # Calculate P&L
        call_pl = np.maximum(price_range - call_strike, 0)
        put_pl = np.maximum(put_strike - price_range, 0)
        total_pl = call_pl + put_pl - total_premium
        
        # Create Plotly chart
        fig = go.Figure()
        
        # Add P&L line
        fig.add_trace(go.Scatter(
            x=price_range.tolist(),
            y=(total_pl * 100).tolist(),
            mode='lines',
            name='P&L',
            line=dict(color='#8B5CF6', width=3),
            hovertemplate='<b>Price: $%{x:.2f}</b><br>P&L: $%{y:.0f}<extra></extra>'
        ))
        
        # Add breakeven lines
        upper_breakeven = call_strike + total_premium
        lower_breakeven = put_strike - total_premium
        
        fig.add_vline(x=upper_breakeven, line_dash="dash", line_color='#F59E0B',
                     annotation_text=f"Upper BE: ${upper_breakeven:.2f}")
        fig.add_vline(x=lower_breakeven, line_dash="dash", line_color='#F59E0B',
                     annotation_text=f"Lower BE: ${lower_breakeven:.2f}")
        
        # Add zero line
        fig.add_hline(y=0, line_dash="solid", line_color='white', line_width=1)
        
        # Add profit zones with shading
        fig.add_vrect(
            x0=underlying_price * 0.7, x1=lower_breakeven,
            fillcolor="rgba(34, 197, 94, 0.2)", opacity=0.3,
            layer="below", line_width=0,
        )
        fig.add_vrect(
            x0=upper_breakeven, x1=underlying_price * 1.3,
            fillcolor="rgba(34, 197, 94, 0.2)", opacity=0.3,
            layer="below", line_width=0,
        )
        
        # Style the chart
        fig.update_layout(
            title=f'{strategy_name} - {ticker}<br><sub>Profit from Large Price Moves in Either Direction</sub>',
            xaxis_title='Stock Price at Expiration ($)',
            yaxis_title='Profit/Loss ($)',
            template='plotly_dark',
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add annotations
        max_loss = total_premium * 100
        
        fig.add_annotation(
            x=underlying_price,
            y=-max_loss * 0.8,
            text=f"Max Loss: ${max_loss:.0f}<br>(No Movement)",
            showarrow=False,
            bgcolor='rgba(239, 68, 68, 0.8)',
            bordercolor='#EF4444',
            font=dict(color='white')
        )
        
        fig.add_annotation(
            x=underlying_price * 1.2,
            y=max_loss * 1.5,
            text="Unlimited Profit<br>on Large Moves",
            showarrow=False,
            bgcolor='rgba(34, 197, 94, 0.8)',
            bordercolor='#22C55E',
            font=dict(color='white')
        )
        
        plotly_json = fig.to_json()
        
        return {
            'plotly_chart': plotly_json,
            'chart_type': 'volatility',
            'max_loss': float(max_loss),
            'breakeven_upper': float(upper_breakeven),
            'breakeven_lower': float(lower_breakeven)
        }
    
    def _generate_iron_condor_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart for Iron Condor"""
        ticker = strategy.get('ticker', 'STOCK')
        underlying_price = strategy.get('entry_logic', {}).get('underlying_price', 100)
        
        # Iron Condor strikes
        put_short_strike = underlying_price * 0.95
        put_long_strike = underlying_price * 0.85
        call_short_strike = underlying_price * 1.05  
        call_long_strike = underlying_price * 1.15
        
        net_credit = 2  # Net credit received
        
        # Generate price range
        price_range = np.linspace(underlying_price * 0.75, underlying_price * 1.25, 100)
        
        # Calculate P&L for Iron Condor
        put_spread_pl = np.minimum(0, put_short_strike - price_range) - np.minimum(0, put_long_strike - price_range)
        call_spread_pl = np.minimum(0, price_range - call_short_strike) - np.minimum(0, price_range - call_long_strike)
        total_pl = put_spread_pl + call_spread_pl + net_credit
        
        # Create Plotly chart
        fig = go.Figure()
        
        # Add P&L line
        fig.add_trace(go.Scatter(
            x=price_range.tolist(),
            y=(total_pl * 100).tolist(),
            mode='lines',
            name='P&L',
            line=dict(color='#F59E0B', width=3),
            hovertemplate='<b>Price: $%{x:.2f}</b><br>P&L: $%{y:.0f}<extra></extra>'
        ))
        
        # Add profit zone shading
        fig.add_vrect(
            x0=put_short_strike, x1=call_short_strike,
            fillcolor="rgba(34, 197, 94, 0.2)", opacity=0.3,
            layer="below", line_width=0,
        )
        
        # Add breakeven lines
        upper_breakeven = call_short_strike + net_credit
        lower_breakeven = put_short_strike - net_credit
        
        fig.add_vline(x=upper_breakeven, line_dash="dash", line_color='#F59E0B',
                     annotation_text=f"Upper BE: ${upper_breakeven:.2f}")
        fig.add_vline(x=lower_breakeven, line_dash="dash", line_color='#F59E0B', 
                     annotation_text=f"Lower BE: ${lower_breakeven:.2f}")
        
        # Add zero line
        fig.add_hline(y=0, line_dash="solid", line_color='white', line_width=1)
        
        # Style the chart
        fig.update_layout(
            title=f'Iron Condor - {ticker}<br><sub>Profit from Sideways Movement</sub>',
            xaxis_title='Stock Price at Expiration ($)',
            yaxis_title='Profit/Loss ($)',
            template='plotly_dark',
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add annotations
        max_profit = net_credit * 100
        max_loss = (call_short_strike - put_short_strike - net_credit) * 100
        
        fig.add_annotation(
            x=underlying_price,
            y=max_profit * 0.8,
            text=f"Max Profit: ${max_profit:.0f}<br>(Keep Premium)",
            showarrow=False,
            bgcolor='rgba(34, 197, 94, 0.8)',
            bordercolor='#22C55E',
            font=dict(color='white')
        )
        
        fig.add_annotation(
            x=underlying_price * 1.2,
            y=-max_loss * 0.8,
            text=f"Max Loss: ${max_loss:.0f}<br>(Big Moves)",
            showarrow=False,
            bgcolor='rgba(239, 68, 68, 0.8)',
            bordercolor='#EF4444',
            font=dict(color='white')
        )
        
        plotly_json = fig.to_json()
        
        return {
            'plotly_chart': plotly_json,
            'chart_type': 'iron_condor',
            'max_profit': max_profit,
            'max_loss': max_loss,
            'profit_range': (put_short_strike, call_short_strike)
        }
    
    def _generate_income_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart for Cash-Secured Put / Covered Call"""
        ticker = strategy.get('ticker', 'STOCK')
        strategy_name = strategy.get('strategy_name', 'Income Strategy')
        underlying_price = strategy.get('entry_logic', {}).get('underlying_price', 100)
        
        is_put = 'put' in strategy_name.lower()
        
        if is_put:  # Cash-Secured Put
            strike = underlying_price * 0.95
            premium = 2
        else:  # Covered Call
            strike = underlying_price * 1.05
            premium = 2
        
        # Generate price range
        price_range = np.linspace(underlying_price * 0.8, underlying_price * 1.2, 100)
        
        # Calculate P&L
        if is_put:
            # Short put P&L
            option_pl = premium - np.maximum(strike - price_range, 0)
            total_pl = option_pl
        else:
            # Covered call (assuming we own stock)
            stock_pl = price_range - underlying_price  # Stock position
            option_pl = premium - np.maximum(price_range - strike, 0)
            total_pl = stock_pl + option_pl
        
        # Create Plotly chart
        fig = go.Figure()
        
        # Add P&L line
        fig.add_trace(go.Scatter(
            x=price_range.tolist(),
            y=(total_pl * 100).tolist(),
            mode='lines',
            name='P&L',
            line=dict(color='#10B981', width=3),
            hovertemplate='<b>Price: $%{x:.2f}</b><br>P&L: $%{y:.0f}<extra></extra>'
        ))
        
        # Add breakeven line
        if is_put:
            breakeven = strike - premium
        else:
            breakeven = underlying_price - premium
            
        fig.add_vline(x=breakeven, line_dash="dash", line_color='#F59E0B',
                     annotation_text=f"Breakeven: ${breakeven:.2f}")
        
        # Add zero line
        fig.add_hline(y=0, line_dash="solid", line_color='white', line_width=1)
        
        # Style the chart
        fig.update_layout(
            title=f'{strategy_name} - {ticker}<br><sub>Generate Income from {"Put Sales" if is_put else "Covered Calls"}</sub>',
            xaxis_title='Stock Price at Expiration ($)',
            yaxis_title='Profit/Loss ($)',
            template='plotly_dark',
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add annotations
        if is_put:
            max_profit = premium * 100
            max_loss_price = underlying_price * 0.8
            max_loss = (strike - max_loss_price - premium) * 100
            
            fig.add_annotation(
                x=underlying_price * 1.1,
                y=max_profit * 0.8,
                text=f"Max Profit: ${max_profit:.0f}<br>(Keep Premium)",
                showarrow=False,
                bgcolor='rgba(34, 197, 94, 0.8)',
                bordercolor='#22C55E',
                font=dict(color='white')
            )
        else:
            max_profit = (strike - underlying_price + premium) * 100
            
            fig.add_annotation(
                x=strike * 1.05,
                y=max_profit * 0.8,
                text=f"Max Profit: ${max_profit:.0f}<br>(Stock Called Away)",
                showarrow=False,
                bgcolor='rgba(34, 197, 94, 0.8)',
                bordercolor='#22C55E',
                font=dict(color='white')
            )
        
        plotly_json = fig.to_json()
        
        return {
            'plotly_chart': plotly_json,
            'chart_type': 'income',
            'breakeven': breakeven
        }
    
    def _generate_generic_chart(self, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Generate a generic chart for unknown strategy types"""
        ticker = strategy.get('ticker', 'STOCK')
        strategy_name = strategy.get('strategy_name', 'Options Strategy')
        
        # Create a simple placeholder chart
        fig = go.Figure()
        
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f'{strategy_name}<br>Chart Coming Soon',
            showarrow=False,
            font=dict(size=24, color='white'),
            xref="paper", yref="paper"
        )
        
        fig.update_layout(
            title=f'{strategy_name} - {ticker}',
            template='plotly_dark',
            height=400,
            showlegend=False
        )
        
        plotly_json = fig.to_json()
        
        return {
            'plotly_chart': plotly_json,
            'chart_type': 'generic'
        }

# Global chart generator instance
chart_generator = OptionsStrategyChartGenerator()
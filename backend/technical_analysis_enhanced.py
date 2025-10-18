"""
Enhanced Technical Analysis Module for Investment Scoring
Includes: Overall Trend, Technical Indicators, Price Action Analysis
"""
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators_weights = {
            'trend_strength': 0.25, # Overall trend direction and strength
            'momentum_indicators': 0.25, # RSI, MACD, Stochastic
            'trend_indicators': 0.20, # SMA crossovers, EMA signals
            'volume_analysis': 0.15, # Volume confirmation
            'price_action': 0.15 # Support/resistance, candlestick patterns
        }
 
    async def analyze_stock_technical(self, symbol: str, period: str = "6mo") -> Dict[str, Any]:
        """Comprehensive technical analysis for a stock"""
        try:
            # Get historical data with extended period for better analysis
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if df.empty or len(df) < 50:
                return self._get_default_technical_analysis(symbol)
            
            # Calculate all technical indicators
            technical_data = {
                'symbol': symbol.upper(),
                'data_points': len(df),
                'analysis_period': period,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # 1. Overall Trend Analysis
            technical_data['trend_analysis'] = self._analyze_overall_trend(df)
            
            # 2. Technical Indicators Analysis
            technical_data['indicators'] = self._calculate_technical_indicators(df)
            
            # 3. Price Action Analysis
            technical_data['price_action'] = self._analyze_price_action(df)
            
            # 4. Volume Analysis
            technical_data['volume_analysis'] = self._analyze_volume_patterns(df)
            
            # 5. Support and Resistance Levels
            technical_data['support_resistance'] = self._find_support_resistance_levels(df)
            
            # 6. Calculate overall technical score
            technical_data['technical_score'] = self._calculate_technical_score(technical_data)
            
            # 7. Generate technical signals and recommendations
            technical_data['signals'] = self._generate_technical_signals(technical_data)
            
            return technical_data
        
        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {str(e)}")
            return self._get_default_technical_analysis(symbol)
 
    def _analyze_overall_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze overall trend direction and strength"""
        try:
            close_prices = df['Close']
            
            # Calculate trend over different periods
            short_trend = self._calculate_trend_strength(close_prices, 20) # 20-day trend
            medium_trend = self._calculate_trend_strength(close_prices, 50) # 50-day trend
            long_trend = self._calculate_trend_strength(close_prices, 100) # 100-day trend if available
            
            # Calculate moving averages for trend confirmation
            df['SMA20'] = ta.trend.sma_indicator(close_prices, window=20)
            df['SMA50'] = ta.trend.sma_indicator(close_prices, window=50)
            df['EMA12'] = ta.trend.ema_indicator(close_prices, window=12)
            df['EMA26'] = ta.trend.ema_indicator(close_prices, window=26)
            
            current_price = close_prices.iloc[-1]
            sma20 = df['SMA20'].iloc[-1] if not pd.isna(df['SMA20'].iloc[-1]) else current_price
            sma50 = df['SMA50'].iloc[-1] if not pd.isna(df['SMA50'].iloc[-1]) else current_price
            
            # Determine overall trend direction
            trend_direction = "NEUTRAL"
            if current_price > sma20 > sma50:
                trend_direction = "BULLISH"
            elif current_price < sma20 < sma50:
                trend_direction = "BEARISH"
            elif current_price > sma20:
                trend_direction = "BULLISH_WEAK"
            elif current_price < sma20:
                trend_direction = "BEARISH_WEAK"
            
            # Calculate trend strength (0-100)
            trend_strength = abs(short_trend['slope']) * 10
            trend_strength = min(100, max(0, trend_strength))
            
            return {
                'direction': trend_direction,
                'strength': trend_strength,
                'short_term': short_trend,
                'medium_term': medium_trend,
                'long_term': long_trend,
                'price_vs_sma20': ((current_price - sma20) / sma20) * 100,
                'price_vs_sma50': ((current_price - sma50) / sma50) * 100,
                'sma_alignment': sma20 > sma50 # True if bullish alignment
            }
        
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {'direction': 'NEUTRAL', 'strength': 50}
    
    def _calculate_trend_strength(self, prices: pd.Series, window: int) -> Dict[str, float]:
        """Calculate trend strength using linear regression"""
        try:
            if len(prices) < window:
                window = len(prices)
            
            recent_prices = prices.tail(window)
            x = np.arange(len(recent_prices))
            y = recent_prices.values
            
            # Linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Calculate R-squared for trend reliability
            y_pred = slope * x + intercept
            r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            return {
                'slope': slope,
                'r_squared': r_squared,
                'reliability': 'HIGH' if r_squared > 0.7 else 'MEDIUM' if r_squared > 0.4 else 'LOW'
            }
        except:
            return {'slope': 0, 'r_squared': 0, 'reliability': 'LOW'}
 
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            indicators = {}
            
            # RSI (Relative Strength Index)
            rsi = ta.momentum.rsi(close, window=14)
            indicators['rsi'] = {
                'current': rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50,
                'signal': self._interpret_rsi(rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50),
                'trend': 'RISING' if rsi.iloc[-1] > rsi.iloc[-5] else 'FALLING'
            }
            
            # MACD
            macd = ta.trend.macd(close)
            macd_signal = ta.trend.macd_signal(close)
            macd_histogram = ta.trend.macd_diff(close)
            
            indicators['macd'] = {
                'macd': macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0,
                'signal': macd_signal.iloc[-1] if not pd.isna(macd_signal.iloc[-1]) else 0,
                'histogram': macd_histogram.iloc[-1] if not pd.isna(macd_histogram.iloc[-1]) else 0,
                'crossover': 'BULLISH' if macd.iloc[-1] > macd_signal.iloc[-1] else 'BEARISH',
                'momentum': 'INCREASING' if macd_histogram.iloc[-1] > macd_histogram.iloc[-2] else 'DECREASING'
            }
            
            # Stochastic Oscillator
            stoch_k = ta.momentum.stoch(high, low, close, window=14, smooth_window=3)
            stoch_d = ta.momentum.stoch_signal(high, low, close, window=14, smooth_window=3)
            
            indicators['stochastic'] = {
                'k': stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50,
                'd': stoch_d.iloc[-1] if not pd.isna(stoch_d.iloc[-1]) else 50,
                'signal': self._interpret_stochastic(stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50)
            }
            
            # Bollinger Bands
            bb_high = ta.volatility.bollinger_hband(close)
            bb_low = ta.volatility.bollinger_lband(close)
            bb_mid = ta.volatility.bollinger_mavg(close)
            
            current_price = close.iloc[-1]
            bb_position = 0.5 # Default middle position
            if not pd.isna(bb_high.iloc[-1]) and not pd.isna(bb_low.iloc[-1]):
                bb_position = (current_price - bb_low.iloc[-1]) / (bb_high.iloc[-1] - bb_low.iloc[-1])
            
            indicators['bollinger_bands'] = {
                'position': bb_position,
                'signal': self._interpret_bollinger_position(bb_position),
                'squeeze': abs(bb_high.iloc[-1] - bb_low.iloc[-1]) < abs(bb_high.iloc[-10] - bb_low.iloc[-10]) if len(df) > 10 else False
            }
            
            # Williams %R
            williams_r = ta.momentum.williams_r(high, low, close, lbp=14)
            indicators['williams_r'] = {
                'current': williams_r.iloc[-1] if not pd.isna(williams_r.iloc[-1]) else -50,
                'signal': self._interpret_williams_r(williams_r.iloc[-1] if not pd.isna(williams_r.iloc[-1]) else -50)
            }
            
            return indicators
        
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}
 
    def _analyze_price_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price action patterns and signals"""
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            open_price = df['Open']
            volume = df['Volume']
            
            # Calculate price action metrics
            price_action = {}
            
            # Recent volatility
            returns = close.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) # Annualized volatility
            price_action['volatility'] = volatility
            
            # Price momentum
            momentum_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(close) > 5 else 0
            momentum_20d = (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(close) > 20 else 0
            
            price_action['momentum'] = {
                '5_day': momentum_5d,
                '20_day': momentum_20d,
                'signal': 'BULLISH' if momentum_5d > 0 and momentum_20d > 0 else 'BEARISH' if momentum_5d < 0 and momentum_20d < 0 else 'MIXED'
            }
            
            # Candlestick pattern analysis (simplified)
            recent_candles = df.tail(5)
            patterns = self._identify_candlestick_patterns(recent_candles)
            price_action['candlestick_patterns'] = patterns
            
            # Price gaps
            gaps = []
            for i in range(1, min(10, len(df))):
                prev_close = df['Close'].iloc[-(i+1)]
                curr_open = df['Open'].iloc[-i]
                gap = (curr_open - prev_close) / prev_close * 100
                if abs(gap) > 2: # Significant gap (>2%)
                    gaps.append({'days_ago': i, 'gap_percent': gap})
            
            price_action['recent_gaps'] = gaps
            
            return price_action
        
        except Exception as e:
            logger.error(f"Error in price action analysis: {str(e)}")
            return {'volatility': 0.3, 'momentum': {'signal': 'NEUTRAL'}}
 
    def _analyze_volume_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns and confirmations"""
        try:
            volume = df['Volume']
            close = df['Close']
            
            # Volume analysis
            avg_volume_20 = volume.tail(20).mean()
            recent_volume = volume.iloc[-1]
            volume_ratio = recent_volume / avg_volume_20
            
            # Volume trend
            volume_trend = ta.trend.sma_indicator(volume, window=10)
            volume_increasing = volume_trend.iloc[-1] > volume_trend.iloc[-5]
            
            # Price-Volume relationship
            price_change = close.pct_change().iloc[-1]
            volume_confirmation = (price_change > 0 and volume_ratio > 1.2) or (price_change < 0 and volume_ratio > 1.2)
            
            # On-Balance Volume (OBV)
            obv = ta.volume.on_balance_volume(close, volume)
            obv_trend = 'RISING' if obv.iloc[-1] > obv.iloc[-10] else 'FALLING' if len(obv) > 10 else 'NEUTRAL'
            
            return {
                'current_vs_average': volume_ratio,
                'trend': 'INCREASING' if volume_increasing else 'DECREASING',
                'price_volume_confirmation': volume_confirmation,
                'obv_trend': obv_trend,
                'signal': 'BULLISH' if volume_confirmation and volume_increasing else 'BEARISH' if volume_ratio < 0.8 else 'NEUTRAL'
            }
        
        except Exception as e:
            logger.error(f"Error in volume analysis: {str(e)}")
            return {'signal': 'NEUTRAL'}
    
    def _find_support_resistance_levels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Find key support and resistance levels"""
        try:
            high = df['High']
            low = df['Low']
            close = df['Close']
            
            current_price = close.iloc[-1]
            
            # Find recent highs and lows for support/resistance
            recent_highs = high.tail(50).nlargest(5).tolist()
            recent_lows = low.tail(50).nsmallest(5).tolist()
            
            # Find nearest support and resistance
            resistance_levels = [h for h in recent_highs if h > current_price]
            support_levels = [l for l in recent_lows if l < current_price]
            
            nearest_resistance = min(resistance_levels) if resistance_levels else current_price * 1.1
            nearest_support = max(support_levels) if support_levels else current_price * 0.9
            
            return {
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'support_strength': len([l for l in recent_lows if abs(l - nearest_support) / nearest_support < 0.02]),
                'resistance_strength': len([h for h in recent_highs if abs(h - nearest_resistance) / nearest_resistance < 0.02]),
                'distance_to_support': ((current_price - nearest_support) / current_price) * 100,
                'distance_to_resistance': ((nearest_resistance - current_price) / current_price) * 100
            }
        
        except Exception as e:
            logger.error(f"Error finding support/resistance: {str(e)}")
            return {}
 
    def _calculate_technical_score(self, technical_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall technical analysis score"""
        try:
            scores = {}
            
            # 1. Trend Score (0-100)
            trend = technical_data.get('trend_analysis', {})
            trend_score = 50 # Default neutral
            
            if trend.get('direction') == 'BULLISH':
                trend_score = 70 + min(30, trend.get('strength', 0) * 0.3)
            elif trend.get('direction') == 'BEARISH':
                trend_score = 30 - min(30, trend.get('strength', 0) * 0.3)
            elif trend.get('direction') in ['BULLISH_WEAK', 'BEARISH_WEAK']:
                trend_score = 50 + (10 if 'BULLISH' in trend.get('direction', '') else -10)
            
            scores['trend_score'] = max(0, min(100, trend_score))
            
            # 2. Momentum Indicators Score
            indicators = technical_data.get('indicators', {})
            momentum_score = 50
            
            # RSI contribution
            rsi_val = indicators.get('rsi', {}).get('current', 50)
            if 30 <= rsi_val <= 70:
                rsi_score = 70 # Neutral/good range
            elif rsi_val < 30:
                rsi_score = 40 # Oversold (could be bullish)
            elif rsi_val > 70:
                rsi_score = 40 # Overbought (could be bearish)
            else:
                rsi_score = 50
            
            # MACD contribution
            macd_data = indicators.get('macd', {})
            macd_score = 60 if macd_data.get('crossover') == 'BULLISH' else 40
            macd_score += 10 if macd_data.get('momentum') == 'INCREASING' else -10
            
            momentum_score = (rsi_score + macd_score) / 2
            scores['momentum_score'] = max(0, min(100, momentum_score))
            
            # 3. Volume Score
            volume_data = technical_data.get('volume_analysis', {})
            volume_signal = volume_data.get('signal', 'NEUTRAL')
            volume_score = 70 if volume_signal == 'BULLISH' else 30 if volume_signal == 'BEARISH' else 50
            scores['volume_score'] = volume_score
            
            # 4. Price Action Score
            price_action = technical_data.get('price_action', {})
            momentum_data = price_action.get('momentum', {})
            price_signal = momentum_data.get('signal', 'NEUTRAL')
            price_score = 70 if price_signal == 'BULLISH' else 30 if price_signal == 'BEARISH' else 50
            scores['price_action_score'] = price_score
            
            # 5. Support/Resistance Score
            sr_data = technical_data.get('support_resistance', {})
            distance_to_support = sr_data.get('distance_to_support', 10)
            distance_to_resistance = sr_data.get('distance_to_resistance', 10)
            
            # Score based on position relative to support/resistance
            if distance_to_support > 5 and distance_to_resistance > 5:
                sr_score = 60 # Good position, away from both levels
            elif distance_to_resistance > 10:
                sr_score = 70 # Close to support, bullish
            elif distance_to_support < 3:
                sr_score = 40 # Close to resistance, bearish
            else:
                sr_score = 50
            
            scores['support_resistance_score'] = sr_score
            
            # Calculate weighted total technical score
            total_score = (
                scores['trend_score'] * self.indicators_weights['trend_strength'] +
                scores['momentum_score'] * self.indicators_weights['momentum_indicators'] +
                scores['volume_score'] * self.indicators_weights['volume_analysis'] +
                scores['price_action_score'] * self.indicators_weights['price_action'] +
                scores['support_resistance_score'] * 0.10 # Additional weight for S/R
            )
            
            scores['total_technical_score'] = max(0, min(100, total_score))
            
            return scores
        
        except Exception as e:
            logger.error(f"Error calculating technical score: {str(e)}")
            return {'total_technical_score': 50}
 
    def _generate_technical_signals(self, technical_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable technical trading signals"""
        signals = []
        
        try:
            # Trend signals
            trend = technical_data.get('trend_analysis', {})
            if trend.get('direction') == 'BULLISH' and trend.get('strength', 0) > 60:
                signals.append({
                    'type': 'TREND',
                    'signal': 'BUY',
                    'description': f'Strong bullish trend with {trend.get("strength", 0):.1f}% strength',
                    'confidence': 'HIGH'
                })
            
            # RSI signals
            indicators = technical_data.get('indicators', {})
            rsi_val = indicators.get('rsi', {}).get('current', 50)
            if rsi_val < 30:
                signals.append({
                    'type': 'MOMENTUM',
                    'signal': 'BUY',
                    'description': f'RSI oversold at {rsi_val:.1f}',
                    'confidence': 'MEDIUM'
                })
            elif rsi_val > 70:
                signals.append({
                    'type': 'MOMENTUM',
                    'signal': 'SELL',
                    'description': f'RSI overbought at {rsi_val:.1f}',
                    'confidence': 'MEDIUM'
                })
            
            # MACD signals
            macd_data = indicators.get('macd', {})
            if macd_data.get('crossover') == 'BULLISH' and macd_data.get('momentum') == 'INCREASING':
                signals.append({
                    'type': 'MOMENTUM',
                    'signal': 'BUY',
                    'description': 'MACD bullish crossover with increasing momentum',
                    'confidence': 'HIGH'
                })
            
            # Volume confirmation signals
            volume_data = technical_data.get('volume_analysis', {})
            if volume_data.get('price_volume_confirmation'):
                signals.append({
                    'type': 'VOLUME',
                    'signal': 'CONFIRM',
                    'description': 'Volume confirms price movement',
                    'confidence': 'HIGH'
                })
            
            return signals[:5] # Return top 5 signals
        
        except Exception as e:
            logger.error(f"Error generating technical signals: {str(e)}")
            return []
    
    # Helper methods for signal interpretation
    def _interpret_rsi(self, rsi_val: float) -> str:
        if rsi_val < 30:
            return 'OVERSOLD'
        elif rsi_val > 70:
            return 'OVERBOUGHT'
        else:
            return 'NEUTRAL'
    
    def _interpret_stochastic(self, stoch_val: float) -> str:
        if stoch_val < 20:
            return 'OVERSOLD'
        elif stoch_val > 80:
            return 'OVERBOUGHT'
        else:
            return 'NEUTRAL'
    
    def _interpret_bollinger_position(self, position: float) -> str:
        if position < 0.2:
            return 'NEAR_LOWER_BAND'
        elif position > 0.8:
            return 'NEAR_UPPER_BAND'
        else:
            return 'MIDDLE_RANGE'
    
    def _interpret_williams_r(self, wr_val: float) -> str:
        if wr_val < -80:
            return 'OVERSOLD'
        elif wr_val > -20:
            return 'OVERBOUGHT'
        else:
            return 'NEUTRAL'
    
    def _identify_candlestick_patterns(self, df: pd.DataFrame) -> List[str]:
        """Simplified candlestick pattern identification"""
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        try:
            # Get last few candles
            recent = df.tail(3)
            
            for i, (_, candle) in enumerate(recent.iterrows()):
                body_size = abs(candle['Close'] - candle['Open'])
                candle_range = candle['High'] - candle['Low']
                
                if candle_range > 0:
                    body_ratio = body_size / candle_range
                    
                    # Doji pattern (small body)
                    if body_ratio < 0.1:
                        patterns.append('DOJI')
                    
                    # Long body candles
                    elif body_ratio > 0.7:
                        if candle['Close'] > candle['Open']:
                            patterns.append('LONG_BULLISH')
                        else:
                            patterns.append('LONG_BEARISH')
            
            return list(set(patterns)) # Remove duplicates
        
        except Exception as e:
            logger.error(f"Error identifying candlestick patterns: {str(e)}")
            return []
    
    def _get_default_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Return default technical analysis when data is unavailable"""
        return {
            'symbol': symbol.upper(),
            'data_points': 0,
            'trend_analysis': {'direction': 'NEUTRAL', 'strength': 50},
            'indicators': {},
            'price_action': {'momentum': {'signal': 'NEUTRAL'}},
            'volume_analysis': {'signal': 'NEUTRAL'},
            'support_resistance': {},
            'technical_score': {'total_technical_score': 50},
            'signals': [],
            'error': 'Insufficient data for technical analysis'
        }

# Global instance
technical_analyzer = TechnicalAnalyzer()
"""
Technical Analysis Expert Agent - Advanced Technical Analysis with Smart Money Concepts
Comprehensive technical analysis using multiple indicators, Smart Money Concepts, and multi-timeframe analysis.
"""

import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
from unusual_whales_service import UnusualWhalesService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalysisAgent:
    """
    Advanced Technical Analysis Agent implementing Smart Money Concepts,
    multiple technical indicators, and multi-timeframe analysis.
    """
    
    def __init__(self):
        self.uw_service = UnusualWhalesService()
        
        # Technical Analysis Weights
        self.analysis_weights = {
            'smart_money_concepts': 0.30,    # Order Blocks, FVG, Market Structure
            'trend_analysis': 0.25,          # EMA, MACD, ADX, Ichimoku
            'momentum_oscillators': 0.20,    # RSI, Stochastic, Williams %R
            'support_resistance': 0.15,      # Pivot Points, Fibonacci, Key levels
            'volume_analysis': 0.10          # OBV, Volume Profile, VWAP
        }
        
        # Smart Money Concept Parameters
        self.smc_params = {
            'order_block_threshold': 0.02,     # 2% price rejection for OB
            'fvg_min_size': 0.005,            # 0.5% minimum FVG size
            'liquidity_sweep_threshold': 0.01, # 1% for inducement detection
            'market_structure_lookback': 20,   # Bars for structure analysis
            'premium_discount_levels': [0.236, 0.382, 0.5, 0.618, 0.786]  # Fibonacci levels
        }
        
        # Technical Indicator Thresholds
        self.indicator_thresholds = {
            'rsi': {'oversold': 30, 'overbought': 70, 'extreme_oversold': 20, 'extreme_overbought': 80},
            'stochastic': {'oversold': 20, 'overbought': 80},
            'williams_r': {'oversold': -80, 'overbought': -20},
            'macd': {'divergence_threshold': 0.1},
            'adx': {'trending': 25, 'strong_trend': 40},
            'bollinger': {'squeeze_threshold': 0.02}
        }
        
        # Timeframe Analysis Weights
        self.timeframe_weights = {
            'weekly': 0.40,      # Primary trend
            'daily': 0.35,       # Intermediate trend  
            'hourly': 0.25       # Short-term confirmation
        }
    
    async def generate_technical_analysis(self, symbol: str, include_smc: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive technical analysis for a given symbol.
        
        Args:
            symbol: Stock ticker symbol
            include_smc: Include Smart Money Concepts analysis
            
        Returns:
            Dict containing technical analysis, signals, and recommendations
        """
        try:
            logger.info(f"Generating technical analysis for {symbol}")
            
            # 1. Fetch multi-timeframe price data
            price_data = await self._fetch_multi_timeframe_data(symbol)
            
            # 2. Smart Money Concepts Analysis
            if include_smc:
                smc_analysis = await self._analyze_smart_money_concepts(price_data, symbol)
            else:
                smc_analysis = {'score': 50.0, 'signals': []}
            
            # 3. Multi-Indicator Technical Analysis
            technical_scores = await self._analyze_technical_indicators(price_data, symbol)
            
            # 4. Multi-Timeframe Confluence
            timeframe_analysis = self._analyze_multi_timeframe_confluence(price_data)
            
            # 5. Support/Resistance Analysis
            sr_analysis = self._analyze_support_resistance_levels(price_data, symbol)
            
            # 6. Calculate composite technical score
            composite_score = self._calculate_technical_composite_score({
                **technical_scores,
                'smart_money_concepts': smc_analysis['score'],
                'support_resistance': sr_analysis['score']
            })
            
            # 7. Generate technical recommendation
            recommendation = self._generate_technical_recommendation(composite_score, technical_scores, smc_analysis)
            
            # 8. Calculate confidence level
            confidence = self._calculate_technical_confidence(technical_scores, timeframe_analysis)
            
            # 9. Extract key technical signals
            key_signals = self._extract_key_technical_signals(technical_scores, smc_analysis, sr_analysis)
            
            # 10. Risk/Entry analysis
            risk_entry_analysis = self._analyze_risk_entry_levels(price_data, sr_analysis)
            
            return {
                'symbol': symbol,
                'technical_score': round(composite_score, 1),
                'recommendation': recommendation,
                'confidence_level': confidence,
                'key_signals': key_signals,
                'smart_money_analysis': smc_analysis,
                'technical_breakdown': technical_scores,
                'timeframe_analysis': timeframe_analysis,
                'support_resistance': sr_analysis,
                'risk_entry_analysis': risk_entry_analysis,
                'timestamp': datetime.now().isoformat(),
                'agent_version': '1.0',
                'analysis_components': ['smart_money_concepts', 'multi_indicator', 'multi_timeframe', 'support_resistance', 'volume_analysis']
            }
            
        except Exception as e:
            logger.error(f"Error generating technical analysis for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': f"Failed to generate technical analysis: {str(e)}",
                'technical_score': 50.0,  # Neutral score on error
                'recommendation': 'HOLD',
                'confidence_level': 'low',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fetch_multi_timeframe_data(self, symbol: str) -> Dict[str, List[Dict]]:
        """Fetch price data for multiple timeframes (mock implementation)."""
        # In production, this would fetch real OHLCV data from market data provider
        mock_data = self._get_mock_price_data(symbol)
        
        return {
            'weekly': mock_data['weekly'],
            'daily': mock_data['daily'],
            'hourly': mock_data['hourly']
        }
    
    async def _analyze_smart_money_concepts(self, price_data: Dict[str, List[Dict]], symbol: str) -> Dict[str, Any]:
        """
        Analyze Smart Money Concepts: Order Blocks, FVG, Market Structure, Liquidity.
        """
        daily_data = price_data['daily']
        weekly_data = price_data['weekly']
        
        smc_signals = []
        smc_score = 50.0  # Start neutral
        
        # 1. Order Blocks Detection
        order_blocks = self._detect_order_blocks(daily_data)
        if order_blocks['bullish_ob']:
            smc_signals.append({
                'type': 'bullish_order_block',
                'strength': 'strong' if len(order_blocks['bullish_ob']) > 2 else 'moderate',
                'description': f"Found {len(order_blocks['bullish_ob'])} bullish order blocks",
                'impact': 15
            })
            smc_score += 15
        
        if order_blocks['bearish_ob']:
            smc_signals.append({
                'type': 'bearish_order_block', 
                'strength': 'strong' if len(order_blocks['bearish_ob']) > 2 else 'moderate',
                'description': f"Found {len(order_blocks['bearish_ob'])} bearish order blocks",
                'impact': -15
            })
            smc_score -= 15
        
        # 2. Fair Value Gaps (FVG) Detection
        fvg_analysis = self._detect_fair_value_gaps(daily_data)
        if fvg_analysis['unfilled_bullish']:
            smc_signals.append({
                'type': 'bullish_fvg',
                'strength': 'strong',
                'description': f"Unfilled bullish FVG at {fvg_analysis['unfilled_bullish'][-1]:.2f}",
                'impact': 12
            })
            smc_score += 12
        
        if fvg_analysis['unfilled_bearish']:
            smc_signals.append({
                'type': 'bearish_fvg',
                'strength': 'strong', 
                'description': f"Unfilled bearish FVG at {fvg_analysis['unfilled_bearish'][-1]:.2f}",
                'impact': -12
            })
            smc_score -= 12
        
        # 3. Market Structure Analysis
        market_structure = self._analyze_market_structure(daily_data, weekly_data)
        if market_structure['trend'] == 'bullish':
            smc_signals.append({
                'type': 'bullish_market_structure',
                'strength': market_structure['strength'],
                'description': f"Bullish market structure: {market_structure['description']}",
                'impact': 10
            })
            smc_score += 10
        elif market_structure['trend'] == 'bearish':
            smc_signals.append({
                'type': 'bearish_market_structure',
                'strength': market_structure['strength'],
                'description': f"Bearish market structure: {market_structure['description']}",
                'impact': -10
            })
            smc_score -= 10
        
        # 4. Liquidity Analysis
        liquidity_analysis = self._analyze_liquidity_zones(daily_data)
        if liquidity_analysis['swept_lows']:
            smc_signals.append({
                'type': 'liquidity_sweep_lows',
                'strength': 'moderate',
                'description': "Recent liquidity sweep of lows - potential reversal",
                'impact': 8
            })
            smc_score += 8
        
        if liquidity_analysis['swept_highs']:
            smc_signals.append({
                'type': 'liquidity_sweep_highs',
                'strength': 'moderate',
                'description': "Recent liquidity sweep of highs - potential reversal",
                'impact': -8
            })
            smc_score -= 8
        
        # 5. Premium/Discount Zone Analysis
        pd_analysis = self._analyze_premium_discount_zones(daily_data, weekly_data)
        if pd_analysis['zone'] == 'discount':
            smc_signals.append({
                'type': 'discount_zone',
                'strength': 'strong',
                'description': f"Price in discount zone ({pd_analysis['level']:.1%} of range)",
                'impact': 15
            })
            smc_score += 15
        elif pd_analysis['zone'] == 'premium':
            smc_signals.append({
                'type': 'premium_zone',
                'strength': 'strong',
                'description': f"Price in premium zone ({pd_analysis['level']:.1%} of range)",
                'impact': -15
            })
            smc_score -= 15
        
        # Normalize score
        smc_score = max(0, min(100, smc_score))
        
        logger.info(f"Smart Money Concepts for {symbol}: Score={smc_score:.1f}, Signals={len(smc_signals)}")
        
        return {
            'score': round(smc_score, 1),
            'signals': smc_signals,
            'order_blocks': order_blocks,
            'fair_value_gaps': fvg_analysis,
            'market_structure': market_structure,
            'liquidity_analysis': liquidity_analysis,
            'premium_discount': pd_analysis
        }
    
    async def _analyze_technical_indicators(self, price_data: Dict[str, List[Dict]], symbol: str) -> Dict[str, float]:
        """Analyze multiple technical indicators across timeframes."""
        daily_data = price_data['daily']
        
        indicator_scores = {}
        
        # 1. Momentum Oscillators
        indicator_scores['rsi'] = self._calculate_rsi_score(daily_data)
        indicator_scores['stochastic'] = self._calculate_stochastic_score(daily_data)
        indicator_scores['williams_r'] = self._calculate_williams_r_score(daily_data)
        
        # 2. Trend Indicators
        indicator_scores['macd'] = self._calculate_macd_score(daily_data)
        indicator_scores['ema_crossover'] = self._calculate_ema_crossover_score(daily_data)
        indicator_scores['adx'] = self._calculate_adx_score(daily_data)
        indicator_scores['ichimoku'] = self._calculate_ichimoku_score(daily_data)
        
        # 3. Volume Indicators
        indicator_scores['obv'] = self._calculate_obv_score(daily_data)
        indicator_scores['volume_trend'] = self._calculate_volume_trend_score(daily_data)
        indicator_scores['vwap'] = self._calculate_vwap_score(daily_data)
        
        # 4. Volatility Indicators
        indicator_scores['bollinger_bands'] = self._calculate_bollinger_score(daily_data)
        indicator_scores['atr'] = self._calculate_atr_score(daily_data)
        
        return indicator_scores
    
    def _detect_order_blocks(self, price_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Detect bullish and bearish order blocks."""
        bullish_ob = []
        bearish_ob = []
        
        for i in range(2, len(price_data) - 2):
            current = price_data[i]
            prev = price_data[i-1]
            next_candle = price_data[i+1]
            
            # Bullish Order Block: Strong rejection from low
            if (current['low'] < prev['low'] and 
                current['close'] > current['open'] and
                (current['high'] - current['low']) / current['low'] > self.smc_params['order_block_threshold']):
                
                bullish_ob.append({
                    'price_level': current['low'],
                    'timestamp': current['date'],
                    'strength': 'strong' if current['volume'] > prev['volume'] * 1.5 else 'moderate'
                })
        
            # Bearish Order Block: Strong rejection from high  
            if (current['high'] > prev['high'] and
                current['close'] < current['open'] and
                (current['high'] - current['low']) / current['low'] > self.smc_params['order_block_threshold']):
                
                bearish_ob.append({
                    'price_level': current['high'],
                    'timestamp': current['date'],
                    'strength': 'strong' if current['volume'] > prev['volume'] * 1.5 else 'moderate'
                })
        
        return {'bullish_ob': bullish_ob[-3:], 'bearish_ob': bearish_ob[-3:]}  # Last 3 OBs
    
    def _detect_fair_value_gaps(self, price_data: List[Dict]) -> Dict[str, List[float]]:
        """Detect Fair Value Gaps (imbalances)."""
        unfilled_bullish = []
        unfilled_bearish = []
        
        for i in range(1, len(price_data) - 1):
            prev = price_data[i-1]
            current = price_data[i]
            next_candle = price_data[i+1]
            
            # Bullish FVG: Gap between previous high and next low
            if (prev['high'] < next_candle['low'] and 
                (next_candle['low'] - prev['high']) / prev['high'] > self.smc_params['fvg_min_size']):
                gap_middle = (prev['high'] + next_candle['low']) / 2
                unfilled_bullish.append(gap_middle)
            
            # Bearish FVG: Gap between previous low and next high
            if (prev['low'] > next_candle['high'] and
                (prev['low'] - next_candle['high']) / next_candle['high'] > self.smc_params['fvg_min_size']):
                gap_middle = (prev['low'] + next_candle['high']) / 2
                unfilled_bearish.append(gap_middle)
        
        return {
            'unfilled_bullish': unfilled_bullish[-2:],  # Last 2 unfilled gaps
            'unfilled_bearish': unfilled_bearish[-2:]
        }
    
    def _analyze_market_structure(self, daily_data: List[Dict], weekly_data: List[Dict]) -> Dict[str, Any]:
        """Analyze market structure for trend direction."""
        # Look for Higher Highs/Higher Lows (bullish) or Lower Highs/Lower Lows (bearish)
        recent_daily = daily_data[-self.smc_params['market_structure_lookback']:]
        recent_weekly = weekly_data[-5:]  # Last 5 weeks
        
        # Daily structure
        daily_highs = [candle['high'] for candle in recent_daily]
        daily_lows = [candle['low'] for candle in recent_daily]
        
        # Check for higher highs and higher lows
        higher_highs = sum(1 for i in range(1, len(daily_highs)) if daily_highs[i] > daily_highs[i-1])
        higher_lows = sum(1 for i in range(1, len(daily_lows)) if daily_lows[i] > daily_lows[i-1])
        
        # Weekly confirmation
        weekly_trend = 'neutral'
        if len(recent_weekly) >= 2:
            if recent_weekly[-1]['close'] > recent_weekly[-2]['close']:
                weekly_trend = 'bullish'
            elif recent_weekly[-1]['close'] < recent_weekly[-2]['close']:
                weekly_trend = 'bearish'
        
        # Determine overall structure
        bullish_signals = higher_highs + higher_lows
        total_signals = len(daily_highs) - 1
        
        if bullish_signals > total_signals * 0.6:
            trend = 'bullish'
            strength = 'strong' if weekly_trend == 'bullish' else 'moderate'
            description = f"Higher highs and higher lows pattern ({bullish_signals}/{total_signals})"
        elif bullish_signals < total_signals * 0.4:
            trend = 'bearish'
            strength = 'strong' if weekly_trend == 'bearish' else 'moderate'
            description = f"Lower highs and lower lows pattern ({total_signals - bullish_signals}/{total_signals})"
        else:
            trend = 'neutral'
            strength = 'weak'
            description = "Sideways consolidation pattern"
        
        return {
            'trend': trend,
            'strength': strength,
            'description': description,
            'daily_structure': f"{bullish_signals}/{total_signals}",
            'weekly_confirmation': weekly_trend
        }
    
    def _analyze_liquidity_zones(self, price_data: List[Dict]) -> Dict[str, bool]:
        """Analyze liquidity sweeps at key levels."""
        recent_data = price_data[-20:]  # Last 20 candles
        
        # Find recent swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(recent_data) - 2):
            current = recent_data[i]
            
            # Swing high: higher than 2 candles on each side
            if (current['high'] > recent_data[i-1]['high'] and
                current['high'] > recent_data[i-2]['high'] and
                current['high'] > recent_data[i+1]['high'] and
                current['high'] > recent_data[i+2]['high']):
                swing_highs.append(current['high'])
            
            # Swing low: lower than 2 candles on each side
            if (current['low'] < recent_data[i-1]['low'] and
                current['low'] < recent_data[i-2]['low'] and
                current['low'] < recent_data[i+1]['low'] and
                current['low'] < recent_data[i+2]['low']):
                swing_lows.append(current['low'])
        
        # Check for recent sweeps
        latest_candles = recent_data[-5:]
        
        swept_lows = False
        swept_highs = False
        
        if swing_lows:
            recent_low = min(candle['low'] for candle in latest_candles)
            if recent_low < min(swing_lows) * (1 - self.smc_params['liquidity_sweep_threshold']):
                swept_lows = True
        
        if swing_highs:
            recent_high = max(candle['high'] for candle in latest_candles)
            if recent_high > max(swing_highs) * (1 + self.smc_params['liquidity_sweep_threshold']):
                swept_highs = True
        
        return {
            'swept_lows': swept_lows,
            'swept_highs': swept_highs,
            'swing_highs': swing_highs[-3:],  # Last 3 swing highs
            'swing_lows': swing_lows[-3:]     # Last 3 swing lows
        }
    
    def _analyze_premium_discount_zones(self, daily_data: List[Dict], weekly_data: List[Dict]) -> Dict[str, Any]:
        """Analyze if price is in premium or discount zone using weekly range."""
        # Use weekly data for primary range
        weekly_range_data = weekly_data[-20:]  # Last 20 weeks
        
        range_high = max(candle['high'] for candle in weekly_range_data)
        range_low = min(candle['low'] for candle in weekly_range_data)
        current_price = daily_data[-1]['close']
        
        # Calculate position in range
        range_size = range_high - range_low
        price_position = (current_price - range_low) / range_size
        
        # Determine zone based on Fibonacci levels
        if price_position <= 0.382:
            zone = 'discount'
            zone_strength = 'strong' if price_position <= 0.236 else 'moderate'
        elif price_position >= 0.618:
            zone = 'premium'
            zone_strength = 'strong' if price_position >= 0.786 else 'moderate'
        else:
            zone = 'equilibrium'
            zone_strength = 'weak'
        
        return {
            'zone': zone,
            'level': price_position,
            'strength': zone_strength,
            'range_high': range_high,
            'range_low': range_low,
            'current_price': current_price
        }
    
    def _get_mock_price_data(self, symbol: str) -> Dict[str, List[Dict]]:
        """Generate mock OHLCV data for different symbols and timeframes."""
        # Mock data for different market conditions
        base_price = {
            'AAPL': 231.59,
            'MSFT': 520.17,
            'NVDA': 142.50,
            'TSLA': 330.56,
            'META': 785.23,
            'GOOGL': 203.90
        }.get(symbol, 100.0)
        
        # Generate daily data (last 50 days)
        daily_data = []
        for i in range(50):
            # Simulate price movement
            volatility = 0.02  # 2% daily volatility
            change = (hash(f"{symbol}_{i}") % 200 - 100) / 100 * volatility
            
            if i == 0:
                open_price = base_price
            else:
                open_price = daily_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.01)
            low = open_price * (1 - abs(change) - 0.005)
            close = open_price * (1 + change)
            volume = 1000000 + (hash(f"{symbol}_vol_{i}") % 500000)
            
            daily_data.append({
                'date': (datetime.now() - timedelta(days=49-i)).strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate weekly data (last 20 weeks)
        weekly_data = []
        for i in range(20):
            week_start = i * 5
            week_data = daily_data[week_start:week_start+5] if week_start < len(daily_data) else daily_data[-5:]
            
            if week_data:
                weekly_data.append({
                    'date': week_data[0]['date'],
                    'open': week_data[0]['open'],
                    'high': max(d['high'] for d in week_data),
                    'low': min(d['low'] for d in week_data),
                    'close': week_data[-1]['close'],
                    'volume': sum(d['volume'] for d in week_data)
                })
        
        # Generate hourly data (last 100 hours)
        hourly_data = []
        for i in range(100):
            volatility = 0.005  # 0.5% hourly volatility
            change = (hash(f"{symbol}_h_{i}") % 100 - 50) / 100 * volatility
            
            if i == 0:
                open_price = base_price
            else:
                open_price = hourly_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.002)
            low = open_price * (1 - abs(change) - 0.001)
            close = open_price * (1 + change)
            volume = 50000 + (hash(f"{symbol}_hvol_{i}") % 25000)
            
            hourly_data.append({
                'date': (datetime.now() - timedelta(hours=99-i)).strftime('%Y-%m-%d %H:00'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        return {
            'daily': daily_data,
            'weekly': weekly_data,
            'hourly': hourly_data
        }
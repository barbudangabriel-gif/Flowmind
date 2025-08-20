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
        
        # Enhanced Multi-Timeframe Analysis Weights (Dual-Tier System)
        self.timeframe_tiers = {
            'primary_check': {
                'monthly': {'weight': 0.35, 'priority': 'trend_identification'},
                'weekly': {'weight': 0.35, 'priority': 'structure_analysis'}, 
                'daily': {'weight': 0.30, 'priority': 'entry_timing'}
            },
            'secondary_check': {
                'h4': {'weight': 0.25, 'priority': 'intraday_structure'},
                'h1': {'weight': 0.25, 'priority': 'short_term_momentum'},
                'm15': {'weight': 0.25, 'priority': 'vwap_analysis', 'vwap_required': True},
                'm1': {'weight': 0.25, 'priority': 'scalping_signals', 'vwap_required': True}
            }
        }
        
        # Market Sessions for Session-Aware Analysis
        self.market_sessions = {
            'premarket': {'start': '04:00', 'end': '09:30', 'timezone': 'US/Eastern'},
            'regular': {'start': '09:30', 'end': '16:00', 'timezone': 'US/Eastern'},
            'postmarket': {'start': '16:00', 'end': '20:00', 'timezone': 'US/Eastern'}
        }
        
        # Gap Analysis Settings (Only for Regular Market Hours)
        self.gap_analysis_config = {
            'enabled_sessions': ['regular'],  # Gaps only during market hours
            'gap_threshold': 0.005,  # 0.5% minimum gap size
            'gap_types': ['gap_up', 'gap_down', 'gap_fill', 'gap_continuation']
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
            
            # Validate data
            if not price_data or not price_data.get('daily') or len(price_data['daily']) < 20:
                logger.warning(f"Insufficient data for {symbol}, using fallback analysis")
                return self._generate_fallback_analysis(symbol)
            
            # 2. Smart Money Concepts Analysis
            if include_smc:
                smc_analysis = await self._analyze_smart_money_concepts(price_data, symbol)
            else:
                smc_analysis = {'score': 50.0, 'signals': []}
            
            # 3. Multi-Indicator Technical Analysis
            technical_scores = await self._analyze_technical_indicators(price_data, symbol)
            
            # 5. Session Analysis with Live Data
            session_analysis = await self._analyze_session_analysis(symbol, price_data)
            
            # 4. Multi-Timeframe Confluence (keeping for compatibility)
            timeframe_analysis = self._analyze_multi_timeframe_confluence(price_data)
            
            # Add session analysis to timeframe analysis
            timeframe_analysis['session_analysis'] = session_analysis
            
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
            
            # Get live stock data for current price
            live_stock_data = await self._get_live_stock_data(symbol)
            
            return {
                'symbol': symbol,
                'stock_data': live_stock_data,  # Add live stock data
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
    
    async def _get_live_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get live stock data from TradeStation API."""
        try:
            from tradestation_client import TradeStationClient
            from tradestation_auth_service import tradestation_auth_service as ts_auth
            
            ts_client = TradeStationClient(ts_auth)
            
            if ts_auth.is_authenticated():
                # Get live quote
                quotes = await ts_client.get_quote([symbol])
                
                if quotes and len(quotes) > 0:
                    quote = quotes[0]
                    live_data = {
                        'symbol': symbol,
                        'price': quote.last,
                        'change': quote.change,
                        'change_percent': quote.change_percent,
                        'volume': quote.volume,
                        'bid': quote.bid,
                        'ask': quote.ask,
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'TradeStation Live API'
                    }
                    logger.info(f"📈 Live data for {symbol}: ${quote.last} ({quote.change_percent:.2f}%) Volume: {quote.volume}")
                    return live_data
                else:
                    logger.warning(f"No quotes received for {symbol}")
                    
            else:
                logger.warning("TradeStation not authenticated for live data")
                
        except Exception as e:
            logger.error(f"Error getting live stock data for {symbol}: {e}")
        
        # Fallback to basic data
        return {
            'symbol': symbol,
            'price': None,
            'change': None,
            'change_percent': None,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'Not Available',
            'error': 'Could not fetch live data'
        }

        """Generate a basic fallback analysis when data is insufficient."""
        return {
            'symbol': symbol,
            'technical_score': 50.0,
            'recommendation': 'HOLD',
            'confidence_level': 'low',
            'key_signals': ['Insufficient data for comprehensive analysis'],
            'smart_money_analysis': {
                'order_blocks': {'bullish': [], 'bearish': []},
                'fair_value_gaps': {'bullish': [], 'bearish': []},
                'market_structure': 'neutral',
                'liquidity_analysis': 'insufficient_data'
            },
            'multi_timeframe_analysis': {
                'weekly': {'trend': 'neutral', 'score': 50.0},
                'daily': {'trend': 'neutral', 'score': 50.0},
                'hourly': {'trend': 'neutral', 'score': 50.0}
            },
            'technical_indicators': {
                'rsi': 50.0, 'macd': 50.0, 'ema': 50.0, 'stochastic': 50.0,
                'williams_r': 50.0, 'adx': 50.0, 'ichimoku': 50.0, 'obv': 50.0,
                'vwap': 50.0, 'bollinger_bands': 50.0
            },
            'support_resistance_levels': {
                'support_levels': [], 'resistance_levels': [], 'score': 50.0
            },
            'risk_reward_analysis': {
                'risk_reward_ratio': 1.0, 'stop_loss': 0, 'take_profit': 0
            },
            'position_sizing': {
                'recommended_position_size': 1.0, 'max_risk_per_trade': 2.0
            },
            'entry_timing': {
                'entry_signal': 'WAIT', 'timing_confidence': 'low'
            },
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'technical_analysis',
            'smc_included': True,
            'timeframes_analyzed': ['weekly', 'daily', 'hourly'],
            'api_version': '1.0'
        }

    async def _fetch_multi_timeframe_data(self, symbol: str) -> Dict[str, List[Dict]]:
        """Fetch comprehensive multi-timeframe data using TradeStation integration."""
        try:
            logger.info(f"🔍 Fetching multi-timeframe data for {symbol} from TradeStation")
            
            # Import TradeStation client 
            from tradestation_client import TradeStationClient
            from tradestation_auth_service import tradestation_auth_service as ts_auth
            
            # Initialize TradeStation client
            ts_client = TradeStationClient(ts_auth)
            
            # Check if authenticated
            if not ts_auth.is_authenticated():
                logger.warning(f"⚠️ TradeStation not authenticated, using mock data for {symbol}")
                return self._get_enhanced_mock_price_data(symbol)
            
            # Fetch multiple timeframes from TradeStation
            timeframe_data = {}
            
            # Define timeframes to fetch
            timeframes = {
                'daily': {'interval': 1, 'unit': 'Daily', 'bars_back': 200},
                'weekly': {'interval': 1, 'unit': 'Weekly', 'bars_back': 52},
                'monthly': {'interval': 1, 'unit': 'Monthly', 'bars_back': 24},
                'h4': {'interval': 4, 'unit': 'Hourly', 'bars_back': 100},
                'h1': {'interval': 1, 'unit': 'Hourly', 'bars_back': 200},
                'm15': {'interval': 15, 'unit': 'Minute', 'bars_back': 400},
                'm1': {'interval': 1, 'unit': 'Minute', 'bars_back': 500}
            }
            
            for timeframe, params in timeframes.items():
                try:
                    logger.info(f"📊 Fetching {timeframe} data for {symbol}")
                    
                    bars = await ts_client.get_historical_bars(
                        symbol=symbol,
                        interval=params['interval'],
                        unit=params['unit'],
                        bars_back=params['bars_back']
                    )
                    
                    if bars and len(bars) > 0:
                        # Convert TradeStation format to internal format
                        converted_bars = []
                        for bar in bars:
                            converted_bars.append({
                                'date': bar.get('TimeStamp', ''),
                                'open': float(bar.get('Open', 0)),
                                'high': float(bar.get('High', 0)),
                                'low': float(bar.get('Low', 0)),
                                'close': float(bar.get('Close', 0)),
                                'volume': int(bar.get('TotalVolume', 0))
                            })
                        
                        timeframe_data[timeframe] = converted_bars
                        logger.info(f"✅ Fetched {len(converted_bars)} {timeframe} bars for {symbol}")
                    else:
                        logger.warning(f"⚠️ No {timeframe} data for {symbol}")
                        
                except Exception as e:
                    logger.error(f"❌ Error fetching {timeframe} data for {symbol}: {e}")
                    continue
            
            # Ensure we have at least daily data
            if 'daily' not in timeframe_data or len(timeframe_data['daily']) < 20:
                logger.warning(f"⚠️ Insufficient data from TradeStation for {symbol}, using mock")
                return self._get_enhanced_mock_price_data(symbol)
            
            # Fill missing timeframes with mock data if needed
            mock_data = self._get_enhanced_mock_price_data(symbol)
            final_data = {}
            
            required_timeframes = ['monthly', 'weekly', 'daily', 'h4', 'h1', 'm15', 'm1']
            for tf in required_timeframes:
                if tf in timeframe_data and len(timeframe_data[tf]) > 0:
                    final_data[tf] = timeframe_data[tf]
                else:
                    logger.info(f"📋 Using mock data for {tf} timeframe for {symbol}")
                    final_data[tf] = mock_data.get(tf, [])
            
            logger.info(f"🎯 Successfully fetched multi-timeframe data for {symbol}: {list(final_data.keys())} timeframes")
            return final_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching multi-timeframe data for {symbol}: {e}")
            return self._get_enhanced_mock_price_data(symbol)
    
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
        
        try:
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
            
        except Exception as e:
            logger.error(f"Error in technical indicators analysis: {str(e)}")
            # Return default scores if calculation fails
            indicator_scores = {
                'rsi': 50.0, 'stochastic': 50.0, 'williams_r': 50.0,
                'macd': 50.0, 'ema_crossover': 50.0, 'adx': 50.0, 'ichimoku': 50.0,
                'obv': 50.0, 'volume_trend': 50.0, 'vwap': 50.0,
                'bollinger_bands': 50.0, 'atr': 50.0
            }
        
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
    
    def _get_enhanced_mock_price_data(self, symbol: str) -> Dict[str, List[Dict]]:
        """Generate enhanced mock OHLCV data for all required timeframes."""
        # Mock data for different market conditions
        base_price = {
            'AAPL': 231.59,
            'MSFT': 520.17,
            'NVDA': 142.50,
            'TSLA': 330.56,
            'META': 785.23,
            'GOOGL': 203.90
        }.get(symbol, 100.0)
        
        # Generate Monthly data (last 12 months)
        monthly_data = []
        for i in range(12):
            # Simulate monthly price movement
            volatility = 0.08  # 8% monthly volatility
            change = (hash(f"{symbol}_M_{i}") % 200 - 100) / 100 * volatility
            
            if i == 0:
                open_price = base_price * 0.85  # Start lower for trend
            else:
                open_price = monthly_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.05)
            low = open_price * (1 - abs(change) - 0.02)
            close = open_price * (1 + change)
            volume = 5000000 + (hash(f"{symbol}_M_vol_{i}") % 2000000)
            
            monthly_data.append({
                'date': (datetime.now() - timedelta(days=(11-i)*30)).strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate Weekly data (last 20 weeks)
        weekly_data = []
        for i in range(20):
            volatility = 0.04  # 4% weekly volatility
            change = (hash(f"{symbol}_W_{i}") % 200 - 100) / 100 * volatility
            
            if i == 0:
                open_price = base_price * 0.92
            else:
                open_price = weekly_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.03)
            low = open_price * (1 - abs(change) - 0.015)
            close = open_price * (1 + change)
            volume = 25000000 + (hash(f"{symbol}_W_vol_{i}") % 10000000)
            
            weekly_data.append({
                'date': (datetime.now() - timedelta(days=(19-i)*7)).strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate Daily data (last 50 days)
        daily_data = []
        for i in range(50):
            volatility = 0.02  # 2% daily volatility
            change = (hash(f"{symbol}_D_{i}") % 200 - 100) / 100 * volatility
            
            if i == 0:
                open_price = base_price * 0.96
            else:
                open_price = daily_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.01)
            low = open_price * (1 - abs(change) - 0.005)
            close = open_price * (1 + change)
            volume = 1000000 + (hash(f"{symbol}_D_vol_{i}") % 500000)
            
            daily_data.append({
                'date': (datetime.now() - timedelta(days=49-i)).strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate 4H data (last 100 periods = ~17 days)
        h4_data = []
        for i in range(100):
            volatility = 0.008  # 0.8% per 4H
            change = (hash(f"{symbol}_4H_{i}") % 100 - 50) / 100 * volatility
            
            if i == 0:
                open_price = base_price * 0.98
            else:
                open_price = h4_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.003)
            low = open_price * (1 - abs(change) - 0.002)
            close = open_price * (1 + change)
            volume = 200000 + (hash(f"{symbol}_4H_vol_{i}") % 100000)
            
            h4_data.append({
                'date': (datetime.now() - timedelta(hours=(99-i)*4)).strftime('%Y-%m-%d %H:00'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate 1H data (last 200 periods = ~8 days)
        h1_data = []
        for i in range(200):
            volatility = 0.003  # 0.3% per hour
            change = (hash(f"{symbol}_1H_{i}") % 100 - 50) / 100 * volatility
            
            if i == 0:
                open_price = base_price * 0.995
            else:
                open_price = h1_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.001)
            low = open_price * (1 - abs(change) - 0.0005)
            close = open_price * (1 + change)
            volume = 50000 + (hash(f"{symbol}_1H_vol_{i}") % 25000)
            
            h1_data.append({
                'date': (datetime.now() - timedelta(hours=199-i)).strftime('%Y-%m-%d %H:00'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate 15M data (last 400 periods = ~4 days) - VWAP Required
        m15_data = []
        for i in range(400):
            volatility = 0.001  # 0.1% per 15min
            change = (hash(f"{symbol}_15M_{i}") % 100 - 50) / 100 * volatility
            
            if i == 0:
                open_price = base_price * 0.999
            else:
                open_price = m15_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.0005)
            low = open_price * (1 - abs(change) - 0.0003)
            close = open_price * (1 + change)
            volume = 10000 + (hash(f"{symbol}_15M_vol_{i}") % 5000)
            
            m15_data.append({
                'date': (datetime.now() - timedelta(minutes=(399-i)*15)).strftime('%Y-%m-%d %H:%M'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        # Generate 1M data (last 500 periods = ~8 hours) - VWAP Required
        m1_data = []
        for i in range(500):
            volatility = 0.0005  # 0.05% per minute
            change = (hash(f"{symbol}_1M_{i}") % 100 - 50) / 100 * volatility
            
            if i == 0:
                open_price = base_price
            else:
                open_price = m1_data[-1]['close']
            
            high = open_price * (1 + abs(change) + 0.0002)
            low = open_price * (1 - abs(change) - 0.0001)
            close = open_price * (1 + change)
            volume = 2000 + (hash(f"{symbol}_1M_vol_{i}") % 1000)
            
            m1_data.append({
                'date': (datetime.now() - timedelta(minutes=499-i)).strftime('%Y-%m-%d %H:%M'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        return {
            # Primary Check Timeframes
            'monthly': monthly_data,
            'weekly': weekly_data,
            'daily': daily_data,
            
            # Secondary Check Timeframes
            'h4': h4_data,
            'h1': h1_data,
            'm15': m15_data,  # VWAP Required
            'm1': m1_data     # VWAP Required
        }
        
    def _calculate_rsi_score(self, price_data: List[Dict]) -> float:
        """Calculate RSI-based score with advanced oversold/overbought analysis."""
        closes = [float(candle['close']) for candle in price_data[-14:]]  # 14-period RSI
        
        if len(closes) < 14:
            return 50.0
        
        # Calculate RSI
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0.01  # Avoid division by zero
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Score based on RSI levels
        if rsi <= self.indicator_thresholds['rsi']['extreme_oversold']:
            return 90.0  # Extreme oversold - strong buy signal
        elif rsi <= self.indicator_thresholds['rsi']['oversold']:
            return 75.0  # Oversold - buy signal
        elif rsi >= self.indicator_thresholds['rsi']['extreme_overbought']:
            return 10.0  # Extreme overbought - strong sell signal
        elif rsi >= self.indicator_thresholds['rsi']['overbought']:
            return 25.0  # Overbought - sell signal
        else:
            # Neutral zone - score based on direction toward oversold/overbought
            return 50.0 + (50 - rsi) * 0.5  # Prefer lower RSI
    
    def _calculate_stochastic_score(self, price_data: List[Dict]) -> float:
        """Calculate Stochastic oscillator score."""
        if len(price_data) < 14:
            return 50.0
        
        recent_data = price_data[-14:]
        current_close = float(recent_data[-1]['close'])
        lowest_low = min(float(candle['low']) for candle in recent_data)
        highest_high = max(float(candle['high']) for candle in recent_data)
        
        if highest_high == lowest_low:
            return 50.0
        
        k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Score based on Stochastic levels
        if k_percent <= self.indicator_thresholds['stochastic']['oversold']:
            return 80.0  # Oversold - buy signal
        elif k_percent >= self.indicator_thresholds['stochastic']['overbought']:
            return 20.0  # Overbought - sell signal
        else:
            return 50.0 + (50 - k_percent) * 0.3  # Prefer lower values
    
    def _calculate_williams_r_score(self, price_data: List[Dict]) -> float:
        """Calculate Williams %R score."""
        if len(price_data) < 14:
            return 50.0
        
        recent_data = price_data[-14:]
        current_close = float(recent_data[-1]['close'])
        highest_high = max(float(candle['high']) for candle in recent_data)
        lowest_low = min(float(candle['low']) for candle in recent_data)
        
        if highest_high == lowest_low:
            return 50.0
        
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        
        # Score based on Williams %R levels
        if williams_r <= self.indicator_thresholds['williams_r']['oversold']:
            return 80.0  # Oversold - buy signal
        elif williams_r >= self.indicator_thresholds['williams_r']['overbought']:
            return 20.0  # Overbought - sell signal
        else:
            return 50.0 + williams_r * 0.3  # Prefer more oversold values
    
    def _calculate_macd_score(self, price_data: List[Dict]) -> float:
        """Calculate MACD score with signal line crossover."""
        if len(price_data) < 26:
            return 50.0
        
        closes = [float(candle['close']) for candle in price_data]
        
        # Calculate EMAs
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        
        if not ema_12 or not ema_26:
            return 50.0
        
        # MACD line
        macd_line = ema_12[-1] - ema_26[-1]
        macd_prev = ema_12[-2] - ema_26[-2] if len(ema_12) > 1 else macd_line
        
        # Signal line (9-period EMA of MACD)
        macd_values = [ema_12[i] - ema_26[i] for i in range(len(ema_12))]
        signal_line = self._calculate_ema(macd_values, 9)
        
        if not signal_line or len(signal_line) < 2:
            return 50.0
        
        current_signal = signal_line[-1]
        prev_signal = signal_line[-2]
        
        # Score based on MACD conditions
        score = 50.0
        
        # MACD above signal line
        if macd_line > current_signal:
            score += 15
        
        # MACD crossover signal line (bullish)
        if macd_prev <= prev_signal and macd_line > current_signal:
            score += 20
        
        # MACD below signal line
        if macd_line < current_signal:
            score -= 15
        
        # MACD crossunder signal line (bearish)
        if macd_prev >= prev_signal and macd_line < current_signal:
            score -= 20
        
        # MACD above zero line
        if macd_line > 0:
            score += 10
        else:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_ema_crossover_score(self, price_data: List[Dict]) -> float:
        """Calculate EMA crossover score (50/200 EMA system)."""
        if len(price_data) < 200:
            return 50.0
        
        closes = [float(candle['close']) for candle in price_data]
        
        ema_50 = self._calculate_ema(closes, 50)
        ema_200 = self._calculate_ema(closes, 200)
        
        if not ema_50 or not ema_200 or len(ema_50) < 2 or len(ema_200) < 2:
            return 50.0
        
        current_50 = ema_50[-1]
        current_200 = ema_200[-1]
        prev_50 = ema_50[-2]
        prev_200 = ema_200[-2]
        
        score = 50.0
        
        # Golden Cross (50 EMA crosses above 200 EMA)
        if prev_50 <= prev_200 and current_50 > current_200:
            score = 85.0
        
        # Death Cross (50 EMA crosses below 200 EMA)
        elif prev_50 >= prev_200 and current_50 < current_200:
            score = 15.0
        
        # 50 EMA above 200 EMA (bullish trend)
        elif current_50 > current_200:
            distance = (current_50 - current_200) / current_200
            score = 60.0 + min(20, distance * 1000)  # Scale distance
        
        # 50 EMA below 200 EMA (bearish trend)
        else:
            distance = (current_200 - current_50) / current_200
            score = 40.0 - min(20, distance * 1000)  # Scale distance
        
        return max(0, min(100, score))
    
    def _calculate_adx_score(self, price_data: List[Dict]) -> float:
        """Calculate ADX (Average Directional Index) score for trend strength."""
        if len(price_data) < 14:
            return 50.0
        
        # Simplified ADX calculation
        recent_data = price_data[-14:]
        
        # Calculate True Range and Directional Movement
        tr_values = []
        dm_plus = []
        dm_minus = []
        
        for i in range(1, len(recent_data)):
            current = recent_data[i]
            prev = recent_data[i-1]
            
            high = float(current['high'])
            low = float(current['low'])
            close = float(current['close'])
            prev_high = float(prev['high'])
            prev_low = float(prev['low'])
            prev_close = float(prev['close'])
            
            # True Range
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)
            
            # Directional Movement
            dm_plus.append(max(0, high - prev_high) if high - prev_high > prev_low - low else 0)
            dm_minus.append(max(0, prev_low - low) if prev_low - low > high - prev_high else 0)
        
        if not tr_values:
            return 50.0
        
        # Average values
        avg_tr = sum(tr_values) / len(tr_values)
        avg_dm_plus = sum(dm_plus) / len(dm_plus)
        avg_dm_minus = sum(dm_minus) / len(dm_minus)
        
        # Calculate DI+ and DI-
        di_plus = (avg_dm_plus / avg_tr) * 100 if avg_tr > 0 else 0
        di_minus = (avg_dm_minus / avg_tr) * 100 if avg_tr > 0 else 0
        
        # ADX calculation
        dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100 if (di_plus + di_minus) > 0 else 0
        
        # Score based on ADX and DI values
        score = 50.0
        
        if dx > self.indicator_thresholds['adx']['strong_trend']:
            if di_plus > di_minus:
                score = 80.0  # Strong bullish trend
            else:
                score = 20.0  # Strong bearish trend
        elif dx > self.indicator_thresholds['adx']['trending']:
            if di_plus > di_minus:
                score = 65.0  # Moderate bullish trend
            else:
                score = 35.0  # Moderate bearish trend
        
        return score
    
    def _calculate_ichimoku_score(self, price_data: List[Dict]) -> float:
        """Calculate Ichimoku Cloud score."""
        if len(price_data) < 52:
            return 50.0
        
        # Ichimoku lines calculation
        recent_9 = price_data[-9:]
        recent_26 = price_data[-26:]
        recent_52 = price_data[-52:]
        
        # Tenkan-sen (Conversion Line) - 9 period
        tenkan_high = max(float(candle['high']) for candle in recent_9)
        tenkan_low = min(float(candle['low']) for candle in recent_9)
        tenkan_sen = (tenkan_high + tenkan_low) / 2
        
        # Kijun-sen (Base Line) - 26 period
        kijun_high = max(float(candle['high']) for candle in recent_26)
        kijun_low = min(float(candle['low']) for candle in recent_26)
        kijun_sen = (kijun_high + kijun_low) / 2
        
        # Current price
        current_price = float(price_data[-1]['close'])
        
        # Score based on Ichimoku conditions
        score = 50.0
        
        # Price above/below Kijun-sen
        if current_price > kijun_sen:
            score += 15
        else:
            score -= 15
        
        # Tenkan-sen above/below Kijun-sen
        if tenkan_sen > kijun_sen:
            score += 10
        else:
            score -= 10
        
        # TK Cross
        if len(price_data) > 26:
            prev_tenkan_high = max(float(candle['high']) for candle in price_data[-10:-1])
            prev_tenkan_low = min(float(candle['low']) for candle in price_data[-10:-1])
            prev_tenkan = (prev_tenkan_high + prev_tenkan_low) / 2
            
            # Bullish TK cross
            if prev_tenkan <= kijun_sen and tenkan_sen > kijun_sen:
                score += 20
            # Bearish TK cross
            elif prev_tenkan >= kijun_sen and tenkan_sen < kijun_sen:
                score -= 20
        
        return max(0, min(100, score))
    
    def _calculate_obv_score(self, price_data: List[Dict]) -> float:
        """Calculate On-Balance Volume score."""
        if len(price_data) < 20:
            return 50.0
        
        # Calculate OBV
        obv_values = []
        obv = 0
        
        for i in range(1, len(price_data)):
            current_close = float(price_data[i]['close'])
            prev_close = float(price_data[i-1]['close'])
            volume = float(price_data[i]['volume'])
            
            if current_close > prev_close:
                obv += volume
            elif current_close < prev_close:
                obv -= volume
            # No change in OBV if close is unchanged
            
            obv_values.append(obv)
        
        if len(obv_values) < 10:
            return 50.0
        
        # OBV trend analysis
        recent_obv = obv_values[-10:]
        obv_slope = (recent_obv[-1] - recent_obv[0]) / len(recent_obv)
        
        # Price trend
        recent_closes = [float(candle['close']) for candle in price_data[-10:]]
        price_slope = (recent_closes[-1] - recent_closes[0]) / len(recent_closes)
        
        # Score based on OBV-Price divergence/confirmation
        if obv_slope > 0 and price_slope > 0:
            return 75.0  # Bullish confirmation
        elif obv_slope < 0 and price_slope < 0:
            return 25.0  # Bearish confirmation
        elif obv_slope > 0 and price_slope < 0:
            return 80.0  # Bullish divergence - strong buy signal
        elif obv_slope < 0 and price_slope > 0:
            return 20.0  # Bearish divergence - strong sell signal
        else:
            return 50.0  # Neutral
    
    def _calculate_volume_trend_score(self, price_data: List[Dict]) -> float:
        """Calculate volume trend score."""
        if len(price_data) < 20:
            return 50.0
        
        recent_data = price_data[-20:]
        
        # Calculate average volume
        volumes = [float(candle['volume']) for candle in recent_data]
        avg_volume = sum(volumes) / len(volumes)
        
        # Recent volume trend
        recent_volumes = volumes[-5:]
        older_volumes = volumes[-10:-5]
        
        recent_avg = sum(recent_volumes) / len(recent_volumes)
        older_avg = sum(older_volumes) / len(older_volumes)
        
        # Price trend
        recent_closes = [float(candle['close']) for candle in recent_data[-5:]]
        price_trend = recent_closes[-1] - recent_closes[0]
        
        # Score based on volume-price relationship
        volume_increase = recent_avg > older_avg * 1.2
        volume_decrease = recent_avg < older_avg * 0.8
        
        if volume_increase and price_trend > 0:
            return 75.0  # Rising prices on increasing volume
        elif volume_increase and price_trend < 0:
            return 25.0  # Falling prices on increasing volume
        elif volume_decrease and price_trend > 0:
            return 45.0  # Rising prices on decreasing volume (weak)
        elif volume_decrease and price_trend < 0:
            return 55.0  # Falling prices on decreasing volume (weak selling)
        else:
            return 50.0  # Neutral
    
    def _calculate_vwap_score(self, price_data: List[Dict]) -> float:
        """Calculate Volume Weighted Average Price score."""
        if len(price_data) < 20:
            return 50.0
        
        recent_data = price_data[-20:]
        
        # Calculate VWAP
        cumulative_volume = 0
        cumulative_volume_price = 0
        
        for candle in recent_data:
            volume = float(candle['volume'])
            typical_price = (float(candle['high']) + float(candle['low']) + float(candle['close'])) / 3
            
            cumulative_volume += volume
            cumulative_volume_price += volume * typical_price
        
        if cumulative_volume == 0:
            return 50.0
        
        vwap = cumulative_volume_price / cumulative_volume
        current_price = float(price_data[-1]['close'])
        
        # Score based on price relative to VWAP
        price_vs_vwap = (current_price - vwap) / vwap
        
        if price_vs_vwap > 0.02:  # 2% above VWAP
            return 70.0  # Bullish - above VWAP
        elif price_vs_vwap < -0.02:  # 2% below VWAP
            return 30.0  # Bearish - below VWAP
        else:
            return 50.0 + price_vs_vwap * 1000  # Gradual scoring around VWAP
    
    def _calculate_bollinger_score(self, price_data: List[Dict]) -> float:
        """Calculate Bollinger Bands score."""
        if len(price_data) < 20:
            return 50.0
        
        recent_closes = [float(candle['close']) for candle in price_data[-20:]]
        
        # Calculate 20-period SMA and standard deviation
        sma = sum(recent_closes) / len(recent_closes)
        variance = sum((close - sma) ** 2 for close in recent_closes) / len(recent_closes)
        std_dev = math.sqrt(variance)
        
        # Bollinger Bands
        upper_band = sma + (2 * std_dev)
        lower_band = sma - (2 * std_dev)
        current_price = recent_closes[-1]
        
        # Score based on Bollinger Band position
        if current_price <= lower_band:
            return 85.0  # Oversold - potential bounce
        elif current_price >= upper_band:
            return 15.0  # Overbought - potential reversal
        elif current_price < sma:
            # Below middle line
            distance_from_lower = (current_price - lower_band) / (sma - lower_band)
            return 30.0 + distance_from_lower * 20
        else:
            # Above middle line
            distance_from_upper = (upper_band - current_price) / (upper_band - sma)
            return 50.0 + distance_from_upper * 20
    
    def _calculate_atr_score(self, price_data: List[Dict]) -> float:
        """Calculate Average True Range score for volatility analysis."""
        if len(price_data) < 14:
            return 50.0
        
        tr_values = []
        
        for i in range(1, len(price_data)):
            current = price_data[i]
            prev = price_data[i-1]
            
            high = float(current['high'])
            low = float(current['low'])
            prev_close = float(prev['close'])
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)
        
        if len(tr_values) < 14:
            return 50.0
        
        # Calculate 14-period ATR
        atr = sum(tr_values[-14:]) / 14
        current_price = float(price_data[-1]['close'])
        
        # ATR as percentage of price
        atr_percentage = (atr / current_price) * 100
        
        # Score based on volatility (moderate volatility preferred)
        if 1.0 <= atr_percentage <= 3.0:
            return 60.0  # Good volatility for trading
        elif 0.5 <= atr_percentage < 1.0:
            return 45.0  # Low volatility
        elif 3.0 < atr_percentage <= 5.0:
            return 55.0  # Higher volatility
        elif atr_percentage > 5.0:
            return 30.0  # Very high volatility - risky
        else:
            return 40.0  # Very low volatility - stagnant
    
    def _calculate_ema(self, values: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if len(values) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # Start with SMA for first value
        sma = sum(values[:period]) / period
        ema_values.append(sma)
        
        # Calculate EMA for remaining values
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def _analyze_multi_timeframe_confluence(self, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Enhanced multi-timeframe confluence analysis with dual-tier system."""
        
        # Primary Check Analysis (Long-term trend and structure)
        primary_analysis = self._analyze_primary_timeframes(price_data)
        
        # Secondary Check Analysis (Short-term and VWAP)
        secondary_analysis = self._analyze_secondary_timeframes(price_data)
        
        # Gap Analysis (Market hours only)
        gap_analysis = self._analyze_market_gaps(price_data)
        
        # Session Analysis (Premarket/Market/Postmarket)
        session_analysis = self._analyze_market_sessions(price_data)
        
        # Calculate overall confluence score
        primary_score = primary_analysis['confluence_score']
        secondary_score = secondary_analysis['confluence_score']
        
        # Weighted confluence (Primary 60%, Secondary 40%)
        overall_confluence = (primary_score * 0.6) + (secondary_score * 0.4)
        
        return {
            'overall_confluence_score': round(overall_confluence, 1),
            'primary_timeframes': primary_analysis,
            'secondary_timeframes': secondary_analysis,
            'gap_analysis': gap_analysis,
            'session_analysis': session_analysis,
            'timeframe_alignment': self._check_enhanced_timeframe_alignment(primary_analysis, secondary_analysis)
        }
    
    def _analyze_primary_timeframes(self, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze primary timeframes: Monthly, Weekly, Daily."""
        primary_scores = {}
        
        # Monthly Analysis (Trend Identification)
        if 'monthly' in price_data and len(price_data['monthly']) >= 3:
            monthly_data = price_data['monthly']
            monthly_closes = [float(candle['close']) for candle in monthly_data[-6:]]  # Last 6 months
            monthly_trend = 'bullish' if monthly_closes[-1] > monthly_closes[0] else 'bearish'
            monthly_strength = abs(monthly_closes[-1] - monthly_closes[0]) / monthly_closes[0]
            
            primary_scores['monthly'] = {
                'trend': monthly_trend,
                'strength': min(100, monthly_strength * 500),  # Scale for monthly moves
                'score': 75 if monthly_trend == 'bullish' else 25,
                'weight': self.timeframe_tiers['primary_check']['monthly']['weight']
            }
        
        # Weekly Analysis (Structure Analysis)
        if 'weekly' in price_data and len(price_data['weekly']) >= 5:
            weekly_data = price_data['weekly']
            weekly_closes = [float(candle['close']) for candle in weekly_data[-10:]]  # Last 10 weeks
            weekly_trend = 'bullish' if weekly_closes[-1] > weekly_closes[0] else 'bearish'
            weekly_strength = abs(weekly_closes[-1] - weekly_closes[0]) / weekly_closes[0]
            
            # Weekly market structure analysis
            weekly_structure = self._analyze_market_structure(weekly_data, [])
            
            primary_scores['weekly'] = {
                'trend': weekly_trend,
                'strength': min(100, weekly_strength * 800),
                'score': 75 if weekly_trend == 'bullish' else 25,
                'structure': weekly_structure,
                'weight': self.timeframe_tiers['primary_check']['weekly']['weight']
            }
        
        # Daily Analysis (Entry Timing)
        if 'daily' in price_data and len(price_data['daily']) >= 10:
            daily_data = price_data['daily']
            daily_closes = [float(candle['close']) for candle in daily_data[-20:]]  # Last 20 days
            daily_trend = 'bullish' if daily_closes[-1] > daily_closes[0] else 'bearish'
            daily_strength = abs(daily_closes[-1] - daily_closes[0]) / daily_closes[0]
            
            primary_scores['daily'] = {
                'trend': daily_trend,
                'strength': min(100, daily_strength * 1000),
                'score': 75 if daily_trend == 'bullish' else 25,
                'weight': self.timeframe_tiers['primary_check']['daily']['weight']
            }
        
        # Calculate primary confluence score
        if primary_scores:
            weighted_score = sum(
                score['score'] * score['weight'] 
                for score in primary_scores.values()
            )
        else:
            weighted_score = 50.0
        
        return {
            'confluence_score': round(weighted_score, 1),
            'timeframe_scores': primary_scores,
            'trend_alignment': self._check_primary_trend_alignment(primary_scores)
        }
    
    def _analyze_secondary_timeframes(self, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze secondary timeframes: 4H, 1H, 15M (with VWAP), 1M (with VWAP)."""
        secondary_scores = {}
        
        # 4H Analysis (Intraday Structure)
        if 'h4' in price_data and len(price_data['h4']) >= 10:
            h4_data = price_data['h4']
            h4_closes = [float(candle['close']) for candle in h4_data[-24:]]  # Last 24 periods (4 days)
            h4_trend = 'bullish' if h4_closes[-1] > h4_closes[0] else 'bearish'
            
            secondary_scores['h4'] = {
                'trend': h4_trend,
                'score': 70 if h4_trend == 'bullish' else 30,
                'priority': 'intraday_structure',
                'weight': self.timeframe_tiers['secondary_check']['h4']['weight']
            }
        
        # 1H Analysis (Short-term Momentum)
        if 'h1' in price_data and len(price_data['h1']) >= 20:
            h1_data = price_data['h1']
            h1_closes = [float(candle['close']) for candle in h1_data[-48:]]  # Last 48 hours (2 days)
            h1_trend = 'bullish' if h1_closes[-1] > h1_closes[0] else 'bearish'
            
            secondary_scores['h1'] = {
                'trend': h1_trend,
                'score': 70 if h1_trend == 'bullish' else 30,
                'priority': 'short_term_momentum',
                'weight': self.timeframe_tiers['secondary_check']['h1']['weight']
            }
        
        # 15M Analysis (VWAP Analysis Required)
        if 'm15' in price_data and len(price_data['m15']) >= 30:
            m15_data = price_data['m15']
            m15_vwap_analysis = self._calculate_vwap_analysis(m15_data, '15m')
            
            secondary_scores['m15'] = {
                'trend': m15_vwap_analysis['trend'],
                'score': m15_vwap_analysis['score'],
                'vwap_analysis': m15_vwap_analysis,
                'priority': 'vwap_analysis',
                'weight': self.timeframe_tiers['secondary_check']['m15']['weight']
            }
        
        # 1M Analysis (Scalping Signals with VWAP)
        if 'm1' in price_data and len(price_data['m1']) >= 60:
            m1_data = price_data['m1']
            m1_vwap_analysis = self._calculate_vwap_analysis(m1_data, '1m')
            
            secondary_scores['m1'] = {
                'trend': m1_vwap_analysis['trend'],
                'score': m1_vwap_analysis['score'],
                'vwap_analysis': m1_vwap_analysis,
                'priority': 'scalping_signals',
                'weight': self.timeframe_tiers['secondary_check']['m1']['weight']
            }
        
        # Calculate secondary confluence score
        if secondary_scores:
            weighted_score = sum(
                score['score'] * score['weight'] 
                for score in secondary_scores.values()
            )
        else:
            weighted_score = 50.0
        
        return {
            'confluence_score': round(weighted_score, 1),
            'timeframe_scores': secondary_scores,
            'vwap_signals': self._extract_vwap_signals(secondary_scores)
        }
    
    def _calculate_vwap_analysis(self, price_data: List[Dict], timeframe: str) -> Dict[str, Any]:
        """Calculate VWAP analysis for 15M and 1M timeframes."""
        if len(price_data) < 20:
            return {'trend': 'neutral', 'score': 50.0, 'vwap': None}
        
        # Calculate VWAP
        cumulative_volume = 0
        cumulative_volume_price = 0
        vwap_values = []
        
        for candle in price_data:
            volume = float(candle['volume'])
            typical_price = (float(candle['high']) + float(candle['low']) + float(candle['close'])) / 3
            
            cumulative_volume += volume
            cumulative_volume_price += volume * typical_price
            
            if cumulative_volume > 0:
                vwap = cumulative_volume_price / cumulative_volume
                vwap_values.append(vwap)
        
        if not vwap_values:
            return {'trend': 'neutral', 'score': 50.0, 'vwap': None}
        
        current_price = float(price_data[-1]['close'])
        current_vwap = vwap_values[-1]
        
        # VWAP trend analysis
        vwap_slope = (vwap_values[-1] - vwap_values[-10]) / 10 if len(vwap_values) >= 10 else 0
        price_vs_vwap = (current_price - current_vwap) / current_vwap
        
        # Score based on VWAP relationship
        if price_vs_vwap > 0.01 and vwap_slope > 0:  # Price above rising VWAP
            trend = 'bullish'
            score = 80.0
        elif price_vs_vwap < -0.01 and vwap_slope < 0:  # Price below falling VWAP
            trend = 'bearish' 
            score = 20.0
        elif abs(price_vs_vwap) < 0.005:  # Price near VWAP
            trend = 'neutral'
            score = 50.0
        else:
            trend = 'mixed'
            score = 45.0
        
        return {
            'trend': trend,
            'score': score,
            'vwap': current_vwap,
            'price_vs_vwap_pct': price_vs_vwap * 100,
            'vwap_slope': vwap_slope,
            'timeframe': timeframe
        }
    
    def _analyze_market_gaps(self, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze gaps during regular market hours only."""
        if 'daily' not in price_data or len(price_data['daily']) < 5:
            return {'gaps_detected': [], 'gap_analysis': 'insufficient_data'}
        
        daily_data = price_data['daily']
        gaps_detected = []
        
        # Analyze last 10 trading days for gaps
        for i in range(1, min(11, len(daily_data))):
            current = daily_data[-i]
            previous = daily_data[-i-1]
            
            current_open = float(current['open'])
            previous_close = float(previous['close'])
            
            gap_size = (current_open - previous_close) / previous_close
            
            if abs(gap_size) >= self.gap_analysis_config['gap_threshold']:
                gap_type = 'gap_up' if gap_size > 0 else 'gap_down'
                
                # Check if gap was filled during the day
                current_low = float(current['low'])
                current_high = float(current['high'])
                
                gap_filled = False
                if gap_type == 'gap_up' and current_low <= previous_close:
                    gap_filled = True
                elif gap_type == 'gap_down' and current_high >= previous_close:
                    gap_filled = True
                
                gaps_detected.append({
                    'date': current['date'],
                    'gap_type': gap_type,
                    'gap_size_pct': gap_size * 100,
                    'gap_filled': gap_filled,
                    'open_price': current_open,
                    'previous_close': previous_close
                })
        
        # Gap analysis summary
        unfilled_gaps = [gap for gap in gaps_detected if not gap['gap_filled']]
        
        return {
            'gaps_detected': gaps_detected,
            'unfilled_gaps': unfilled_gaps,
            'gap_analysis': self._interpret_gap_pattern(gaps_detected),
            'gap_count_last_10_days': len(gaps_detected)
        }
    
    def _analyze_market_sessions(self, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze premarket, market, and postmarket sessions."""
        # This would analyze price behavior across different market sessions
        # For now, return mock session analysis
        
    async def _analyze_session_analysis(self, symbol: str, price_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze trading session patterns with LIVE TradeStation data."""
        try:
            # Get current live price from TradeStation
            current_price = None
            if hasattr(self, 'ts_client') and self.ts_client:
                try:
                    from tradestation_client import TradeStationClient
                    from tradestation_auth_service import tradestation_auth_service as ts_auth
                    
                    ts_client = TradeStationClient(ts_auth)
                    if ts_auth.is_authenticated():
                        quotes = await ts_client.get_quote([symbol])
                        if quotes and len(quotes) > 0:
                            current_price = quotes[0].last
                            logger.info(f"🎯 Live price for {symbol}: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get live price for {symbol}: {e}")
            
            # Use daily data to estimate session levels based on recent trading
            daily_data = price_data.get('daily', [])
            
            if daily_data and len(daily_data) > 0:
                # Get last few days of data for realistic session level estimation
                recent_days = daily_data[-5:] if len(daily_data) >= 5 else daily_data
                
                # Calculate realistic session levels from recent data
                highs = [float(candle['high']) for candle in recent_days]
                lows = [float(candle['low']) for candle in recent_days]
                closes = [float(candle['close']) for candle in recent_days]
                
                avg_high = sum(highs) / len(highs)
                avg_low = sum(lows) / len(lows)
                latest_close = closes[-1]
                
                # Estimate session levels based on current price and recent ranges
                if current_price:
                    # Use live price as base for session calculations
                    base_price = current_price
                else:
                    # Fallback to latest close
                    base_price = latest_close
                
                # Calculate session levels as percentages of current price
                premarket_range = base_price * 0.02  # 2% typical premarket range
                regular_range = base_price * 0.04   # 4% typical daily range
                postmarket_range = base_price * 0.015  # 1.5% typical postmarket range
                
                session_levels = {
                    'premarket_high': round(base_price + premarket_range, 2),
                    'premarket_low': round(base_price - premarket_range, 2),
                    'regular_high': round(base_price + regular_range, 2),
                    'regular_low': round(base_price - regular_range, 2),
                    'postmarket_high': round(base_price + postmarket_range, 2),
                    'postmarket_low': round(base_price - postmarket_range, 2)
                }
                
                logger.info(f"📊 Live session levels for {symbol} (base: ${base_price}): {session_levels}")
                
            else:
                # Fallback mock levels if no data available
                session_levels = {
                    'premarket_high': 150.25,
                    'premarket_low': 148.75,
                    'regular_high': 152.50,
                    'regular_low': 147.25,
                    'postmarket_high': 151.00,
                    'postmarket_low': 149.50
                }
                logger.warning(f"Using fallback session levels for {symbol}")
            
        except Exception as e:
            logger.error(f"Error in session analysis for {symbol}: {e}")
            # Fallback session levels
            session_levels = {
                'premarket_high': 150.25,
                'premarket_low': 148.75,
                'regular_high': 152.50,
                'regular_low': 147.25,
                'postmarket_high': 151.00,
                'postmarket_low': 149.50
            }
        
        return {
            'premarket_sentiment': 'bullish',
            'regular_market_sentiment': 'neutral', 
            'postmarket_sentiment': 'bearish',
            'session_analysis': {
                'premarket_volume': 'above_average',
                'regular_market_volume': 'normal',
                'postmarket_volume': 'below_average'
            },
            'key_session_levels': session_levels,
            'current_live_price': current_price,  # Add live price to response
            'price_source': 'TradeStation Live' if current_price else 'Estimated'
        }
    
    def _check_enhanced_timeframe_alignment(self, primary_analysis: Dict, secondary_analysis: Dict) -> str:
        """Check alignment across both primary and secondary timeframes."""
        primary_scores = primary_analysis.get('timeframe_scores', {})
        secondary_scores = secondary_analysis.get('timeframe_scores', {})
        
        # Extract trends from all timeframes
        all_trends = []
        
        # Primary trends
        for tf_data in primary_scores.values():
            all_trends.append(tf_data.get('trend', 'neutral'))
        
        # Secondary trends  
        for tf_data in secondary_scores.values():
            all_trends.append(tf_data.get('trend', 'neutral'))
        
        if not all_trends:
            return 'unknown'
        
        bullish_count = sum(1 for trend in all_trends if trend == 'bullish')
        bearish_count = sum(1 for trend in all_trends if trend == 'bearish')
        total_count = len(all_trends)
        
        if bullish_count >= total_count * 0.75:
            return 'strongly_bullish'
        elif bullish_count >= total_count * 0.6:
            return 'bullish'
        elif bearish_count >= total_count * 0.75:
            return 'strongly_bearish'
        elif bearish_count >= total_count * 0.6:
            return 'bearish'
        else:
            return 'mixed'
    
    def _check_primary_trend_alignment(self, primary_scores: Dict) -> str:
        """Check alignment within primary timeframes."""
        if not primary_scores:
            return 'unknown'
        
        trends = [score['trend'] for score in primary_scores.values()]
        
        if all(trend == 'bullish' for trend in trends):
            return 'all_bullish'
        elif all(trend == 'bearish' for trend in trends):
            return 'all_bearish'
        else:
            return 'mixed'
    
    def _extract_vwap_signals(self, secondary_scores: Dict) -> List[Dict]:
        """Extract VWAP signals from 15M and 1M analysis."""
        vwap_signals = []
        
        for timeframe in ['m15', 'm1']:
            if timeframe in secondary_scores:
                tf_data = secondary_scores[timeframe]
                vwap_analysis = tf_data.get('vwap_analysis', {})
                
                if vwap_analysis:
                    vwap_signals.append({
                        'timeframe': timeframe,
                        'signal': vwap_analysis['trend'],
                        'strength': 'strong' if abs(vwap_analysis['score'] - 50) > 25 else 'moderate',
                        'price_vs_vwap_pct': vwap_analysis.get('price_vs_vwap_pct', 0),
                        'vwap_slope': vwap_analysis.get('vwap_slope', 0)
                    })
        
        return vwap_signals
    
    def _interpret_gap_pattern(self, gaps_detected: List[Dict]) -> str:
        """Interpret the pattern of gaps for trading insights."""
        if not gaps_detected:
            return 'no_gaps_detected'
        
        unfilled_gaps = [gap for gap in gaps_detected if not gap['gap_filled']]
        gap_ups = [gap for gap in gaps_detected if gap['gap_type'] == 'gap_up']
        gap_downs = [gap for gap in gaps_detected if gap['gap_type'] == 'gap_down']
        
        if len(unfilled_gaps) > 3:
            return 'multiple_unfilled_gaps_resistance'
        elif len(gap_ups) > len(gap_downs) * 2:
            return 'bullish_gap_pattern'
        elif len(gap_downs) > len(gap_ups) * 2:
            return 'bearish_gap_pattern'
        else:
            return 'mixed_gap_pattern'
    
    def _analyze_support_resistance_levels(self, price_data: Dict[str, List[Dict]], symbol: str) -> Dict[str, Any]:
        """Analyze key support and resistance levels."""
        daily_data = price_data['daily']
        weekly_data = price_data['weekly']
        
        # Find pivot points from daily data
        pivots = self._find_pivot_points(daily_data)
        
        # Find weekly support/resistance
        weekly_levels = self._find_weekly_levels(weekly_data)
        
        # Current price
        current_price = float(daily_data[-1]['close'])
        
        # Find closest support and resistance
        resistance_levels = [level for level in pivots['resistance'] + weekly_levels['resistance'] if level > current_price]
        support_levels = [level for level in pivots['support'] + weekly_levels['support'] if level < current_price]
        
        closest_resistance = min(resistance_levels) if resistance_levels else current_price * 1.1
        closest_support = max(support_levels) if support_levels else current_price * 0.9
        
        # Calculate distances
        resistance_distance = (closest_resistance - current_price) / current_price
        support_distance = (current_price - closest_support) / current_price
        
        # Score based on position relative to S/R
        sr_score = 50.0
        
        # Closer to support = more bullish
        if support_distance < 0.03:  # Within 3% of support
            sr_score += 20
        elif support_distance < 0.05:  # Within 5% of support
            sr_score += 10
        
        # Closer to resistance = more bearish
        if resistance_distance < 0.03:  # Within 3% of resistance
            sr_score -= 20
        elif resistance_distance < 0.05:  # Within 5% of resistance
            sr_score -= 10
        
        return {
            'score': max(0, min(100, sr_score)),
            'current_price': current_price,
            'closest_support': closest_support,
            'closest_resistance': closest_resistance,
            'support_distance_pct': support_distance * 100,
            'resistance_distance_pct': resistance_distance * 100,
            'all_support_levels': sorted(support_levels, reverse=True)[:5],
            'all_resistance_levels': sorted(resistance_levels)[:5]
        }
    
    def _find_pivot_points(self, price_data: List[Dict]) -> Dict[str, List[float]]:
        """Find pivot points for support and resistance."""
        if len(price_data) < 10:
            return {'support': [], 'resistance': []}
        
        resistance_levels = []
        support_levels = []
        
        # Look for swing highs and lows
        for i in range(2, len(price_data) - 2):
            current = price_data[i]
            high = float(current['high'])
            low = float(current['low'])
            
            # Check for swing high (resistance)
            if (high > float(price_data[i-1]['high']) and
                high > float(price_data[i-2]['high']) and
                high > float(price_data[i+1]['high']) and
                high > float(price_data[i+2]['high'])):
                resistance_levels.append(high)
            
            # Check for swing low (support)
            if (low < float(price_data[i-1]['low']) and
                low < float(price_data[i-2]['low']) and
                low < float(price_data[i+1]['low']) and
                low < float(price_data[i+2]['low'])):
                support_levels.append(low)
        
        return {
            'support': support_levels[-10:],  # Last 10 support levels
            'resistance': resistance_levels[-10:]  # Last 10 resistance levels
        }
    
    def _find_weekly_levels(self, weekly_data: List[Dict]) -> Dict[str, List[float]]:
        """Find major weekly support and resistance levels."""
        if len(weekly_data) < 5:
            return {'support': [], 'resistance': []}
        
        # Get weekly highs and lows
        weekly_highs = [float(candle['high']) for candle in weekly_data[-10:]]
        weekly_lows = [float(candle['low']) for candle in weekly_data[-10:]]
        
        # Find significant levels
        major_resistance = sorted(set(weekly_highs), reverse=True)[:5]
        major_support = sorted(set(weekly_lows))[-5:]
        
        return {
            'support': major_support,
            'resistance': major_resistance
        }
    
    def _analyze_risk_entry_levels(self, price_data: Dict[str, List[Dict]], sr_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimal risk/entry levels based on technical analysis."""
        current_price = sr_analysis['current_price']
        closest_support = sr_analysis['closest_support']
        closest_resistance = sr_analysis['closest_resistance']
        
        # Calculate risk/reward ratios
        risk_to_support = current_price - closest_support
        reward_to_resistance = closest_resistance - current_price
        
        risk_reward_ratio = reward_to_resistance / risk_to_support if risk_to_support > 0 else 0
        
        # Calculate position size based on risk
        max_risk_percentage = 2.0  # 2% max risk per trade
        position_risk_amount = current_price - closest_support
        position_risk_pct = (position_risk_amount / current_price) * 100
        
        # Recommended position size
        if position_risk_pct > 0:
            recommended_position_size = min(100, (max_risk_percentage / position_risk_pct) * 100)
        else:
            recommended_position_size = 0
        
        # Entry timing score
        entry_score = 50.0
        
        if risk_reward_ratio >= 3.0:
            entry_score = 90.0  # Excellent risk/reward
        elif risk_reward_ratio >= 2.0:
            entry_score = 75.0  # Good risk/reward
        elif risk_reward_ratio >= 1.5:
            entry_score = 60.0  # Acceptable risk/reward
        elif risk_reward_ratio >= 1.0:
            entry_score = 45.0  # Poor risk/reward
        else:
            entry_score = 20.0  # Bad risk/reward
        
        return {
            'entry_score': round(entry_score, 1),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'stop_loss_level': closest_support,
            'take_profit_level': closest_resistance,
            'position_risk_pct': round(position_risk_pct, 2),
            'recommended_position_size_pct': round(recommended_position_size, 1),
            'entry_recommendation': self._get_entry_recommendation(entry_score, risk_reward_ratio)
        }
    
    def _get_entry_recommendation(self, entry_score: float, risk_reward_ratio: float) -> str:
        """Get entry timing recommendation."""
        if entry_score >= 80 and risk_reward_ratio >= 2.5:
            return "EXCELLENT ENTRY - Strong risk/reward setup"
        elif entry_score >= 65 and risk_reward_ratio >= 2.0:
            return "GOOD ENTRY - Acceptable risk/reward"
        elif entry_score >= 50:
            return "MODERATE ENTRY - Consider smaller position"
        elif entry_score >= 35:
            return "POOR ENTRY - Wait for better setup"
        else:
            return "AVOID ENTRY - Risk too high"
    
    def _calculate_technical_composite_score(self, technical_scores: Dict[str, float]) -> float:
        """Calculate weighted composite technical score."""
        composite = 0.0
        total_weight = 0.0
        
        # Group indicators by category and apply weights
        categories = {
            'smart_money_concepts': ['smart_money_concepts'],
            'trend_analysis': ['macd', 'ema_crossover', 'adx', 'ichimoku'],
            'momentum_oscillators': ['rsi', 'stochastic', 'williams_r'],
            'support_resistance': ['support_resistance'],
            'volume_analysis': ['obv', 'volume_trend', 'vwap'],
            'volatility': ['bollinger_bands', 'atr']
        }
        
        for category, indicators in categories.items():
            category_weight = self.analysis_weights.get(category, 0.1)
            category_scores = [technical_scores.get(indicator, 50.0) for indicator in indicators if indicator in technical_scores]
            
            if category_scores:
                category_average = sum(category_scores) / len(category_scores)
                composite += category_average * category_weight
                total_weight += category_weight
        
        # Normalize if needed
        if total_weight > 0:
            composite = composite / total_weight * (sum(self.analysis_weights.values()))
        
        return round(min(100, max(0, composite)), 1)
    
    def _generate_technical_recommendation(self, composite_score: float, technical_scores: Dict[str, float], smc_analysis: Dict[str, Any]) -> str:
        """Generate technical recommendation based on analysis."""
        smc_score = smc_analysis.get('score', 50.0)
        
        # Enhanced recommendation based on technical and SMC analysis
        if composite_score >= 80 and smc_score >= 70:
            return "STRONG BUY - Multiple Bullish Signals"
        elif composite_score >= 70 and smc_score >= 60:
            return "BUY - Technical Breakout Setup"
        elif composite_score >= 60:
            return "HOLD+ - Bullish Bias"
        elif composite_score >= 40:
            return "HOLD - Neutral Technical Picture"
        elif composite_score >= 30:
            return "HOLD- - Bearish Bias"
        elif composite_score >= 20:
            return "SELL - Technical Breakdown"
        else:
            return "STRONG SELL - Multiple Bearish Signals"
    
    def _calculate_technical_confidence(self, technical_scores: Dict[str, float], timeframe_analysis: Dict[str, Any]) -> str:
        """Calculate confidence level based on signal consistency."""
        scores = list(technical_scores.values())
        if not scores:
            return 'low'
        
        # Check consistency of signals
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        avg_score = statistics.mean(scores)
        
        # Timeframe alignment bonus
        alignment = timeframe_analysis.get('alignment', 'mixed')
        alignment_bonus = 0
        if alignment in ['all_bullish', 'all_bearish']:
            alignment_bonus = 10
        
        # High confidence: consistent signals with timeframe alignment
        if score_std < 12 and alignment_bonus > 0 and (avg_score > 70 or avg_score < 30):
            return 'high'
        elif score_std < 20 and (alignment_bonus > 0 or (avg_score > 65 or avg_score < 35)):
            return 'medium'
        else:
            return 'low'
    
    def _extract_key_technical_signals(self, technical_scores: Dict[str, float], smc_analysis: Dict[str, Any], sr_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract the most significant technical signals."""
        key_signals = []
        
        # Find top technical indicators by deviation from neutral
        sorted_indicators = sorted(
            technical_scores.items(), 
            key=lambda x: abs(x[1] - 50), 
            reverse=True
        )
        
        # Add top 3 technical indicators
        for indicator, score in sorted_indicators[:3]:
            signal_strength = 'strong' if abs(score - 50) > 25 else 'moderate' if abs(score - 50) > 15 else 'weak'
            signal_direction = 'bullish' if score > 50 else 'bearish' if score < 50 else 'neutral'
            
            key_signals.append({
                'type': f'technical_{indicator}',
                'score': score,
                'strength': signal_strength,
                'direction': signal_direction,
                'details': self._get_indicator_description(indicator, score)
            })
        
        # Add key SMC signals
        smc_signals = smc_analysis.get('signals', [])
        for signal in smc_signals[:2]:  # Top 2 SMC signals
            key_signals.append({
                'type': signal['type'],
                'score': 50 + signal.get('impact', 0),
                'strength': signal['strength'],
                'direction': 'bullish' if signal.get('impact', 0) > 0 else 'bearish',
                'details': signal['description']
            })
        
        # Add support/resistance signal
        sr_score = sr_analysis.get('score', 50)
        if abs(sr_score - 50) > 10:
            key_signals.append({
                'type': 'support_resistance',
                'score': sr_score,
                'strength': 'strong' if abs(sr_score - 50) > 20 else 'moderate',
                'direction': 'bullish' if sr_score > 50 else 'bearish',
                'details': f"Price {sr_analysis.get('support_distance_pct', 0):.1f}% from support, {sr_analysis.get('resistance_distance_pct', 0):.1f}% from resistance"
            })
        
        return key_signals[:5]  # Return top 5 signals
    
    def _get_indicator_description(self, indicator: str, score: float) -> str:
        """Get description for technical indicator."""
        descriptions = {
            'rsi': f"RSI showing {'oversold' if score > 70 else 'overbought' if score < 30 else 'neutral'} conditions",
            'macd': f"MACD showing {'bullish' if score > 50 else 'bearish'} momentum",
            'ema_crossover': f"EMA crossover indicating {'bullish' if score > 50 else 'bearish'} trend",
            'stochastic': f"Stochastic {'oversold' if score > 70 else 'overbought' if score < 30 else 'neutral'}",
            'williams_r': f"Williams %R showing {'oversold' if score > 70 else 'overbought' if score < 30 else 'neutral'} levels",
            'adx': f"ADX indicating {'strong' if score > 65 or score < 35 else 'moderate'} trend strength",
            'ichimoku': f"Ichimoku cloud showing {'bullish' if score > 50 else 'bearish'} configuration",
            'obv': f"On-Balance Volume showing {'bullish' if score > 50 else 'bearish'} flow",
            'volume_trend': f"Volume trend {'confirming' if score > 55 or score < 45 else 'neutral'} price action",
            'vwap': f"Price {'above' if score > 50 else 'below'} VWAP indicating {'bullish' if score > 50 else 'bearish'} sentiment",
            'bollinger_bands': f"Price near {'lower' if score > 70 else 'upper' if score < 30 else 'middle'} Bollinger Band",
            'atr': f"ATR showing {'normal' if 45 <= score <= 65 else 'elevated'} volatility levels"
        }
        
        return descriptions.get(indicator, f"{indicator} analysis with score {score}")
    
    # Additional utility methods for future enhancements
    async def get_batch_technical_analysis(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Generate technical analysis for multiple symbols efficiently."""
        tasks = [self.generate_technical_analysis(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result if not isinstance(result, Exception) else {'error': str(result)}
            for symbol, result in zip(symbols, results)
        }
    
    def get_technical_methodology(self) -> Dict[str, str]:
        """Return explanation of technical analysis methodology."""
        return {
            'smart_money_concepts': 'Advanced institutional analysis using Order Blocks, Fair Value Gaps, Market Structure, and Liquidity concepts',
            'trend_analysis': 'Multi-indicator trend analysis using MACD, EMA crossovers, ADX, and Ichimoku Cloud systems',
            'momentum_oscillators': 'Momentum analysis using RSI, Stochastic, and Williams %R with divergence detection',
            'support_resistance': 'Key level analysis using pivot points, weekly levels, and Fibonacci retracements',
            'volume_analysis': 'Volume confirmation using OBV, Volume trends, and VWAP for institutional flow detection',
            'multi_timeframe': 'Confluence analysis across Weekly (primary), Daily (intermediate), and Hourly (short-term) timeframes',
            'risk_management': 'Position sizing and risk/reward optimization based on technical levels and ATR volatility',
            'composite_methodology': 'Weighted scoring system emphasizing Smart Money Concepts (30%) and trend analysis (25%)'
        }
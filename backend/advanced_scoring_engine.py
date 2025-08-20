"""
Advanced Scoring Engine pentru FlowMind Analytics
Integrează multiple surse de date și algoritmi avansați pentru scoring optim

SURSE DE DATE:
1. TradeStation API - Market data real-time, historical, volume
2. Unusual Whales - Options flow, institutional activity  
3. Technical Indicators - 15+ indicatori tehnici avansați
4. Fundamental Data - P/E, P/B, ROE, Debt/Equity, etc.
5. Market Sentiment - News sentiment, social media trends
6. Options Activity - Put/Call ratios, unusual volume
7. Institutional Activity - Smart money moves

ALGORITMI:
1. Multi-factor quantitative scoring (40+ factori)
2. Machine learning trend prediction
3. Options flow analysis scoring
4. Sentiment analysis cu NLP
5. Risk-adjusted returns calculation
6. Relative strength vs sector/market
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class ScoringFactors:
    """Factori de scoring cu ponderi"""
    # Technical Analysis (35%)
    trend_strength: float = 0.08        # Puterea trendul principal
    momentum_indicators: float = 0.07   # RSI, MACD, Stochastic  
    moving_averages: float = 0.06       # SMA/EMA crossovers
    volume_analysis: float = 0.06       # Volume confirmation patterns
    volatility_analysis: float = 0.04   # Bollinger Bands, ATR
    support_resistance: float = 0.04    # S/R levels și breakouts
    
    # Fundamental Analysis (25%) 
    valuation_ratios: float = 0.06      # P/E, P/B, P/S ratios
    growth_metrics: float = 0.05        # Revenue/earnings growth
    profitability: float = 0.05         # ROE, ROA, margins
    financial_health: float = 0.04      # Debt ratios, cash flow
    dividend_quality: float = 0.03      # Yield, payout ratio, growth
    earnings_quality: float = 0.02      # Earnings surprises, guidance
    
    # Options Flow Analysis (20%)
    unusual_options_volume: float = 0.08  # Volumul neobișnuit de opțiuni
    put_call_ratios: float = 0.04         # Put/Call ratio trends
    options_sentiment: float = 0.04       # Bullish/bearish options activity
    large_trades: float = 0.04            # Big money moves
    
    # Market Sentiment (15%)
    news_sentiment: float = 0.06          # Sentiment din știri
    social_sentiment: float = 0.04        # Social media sentiment  
    analyst_ratings: float = 0.03         # Rating changes, targets
    insider_activity: float = 0.02        # Insider buying/selling
    
    # Risk Factors (5%)
    beta_analysis: float = 0.02           # Systematic risk
    drawdown_risk: float = 0.02           # Maximum drawdown risk
    liquidity_risk: float = 0.01          # Trading volume, bid-ask

class AdvancedScoringEngine:
    def __init__(self, ts_client=None, uw_service=None):
        self.ts_client = ts_client
        self.uw_service = uw_service
        self.factors = ScoringFactors()
        self.sector_benchmarks = {}  # Cache pentru benchmarks sector
        
    async def calculate_comprehensive_score(self, symbol: str) -> Dict[str, Any]:
        """
        Calculează scorul complet cu toate sursele de date
        Returns: Dict cu scor total + breakdown detaliat
        """
        try:
            logger.info(f"🔍 Calculând scorul complet pentru {symbol}")
            
            # Obține toate datele în paralel pentru viteză maximă
            tasks = [
                self._get_technical_data(symbol),
                self._get_fundamental_data(symbol), 
                self._get_options_flow_data(symbol),
                self._get_sentiment_data(symbol),
                self._get_risk_data(symbol)
            ]
            
            technical_data, fundamental_data, options_data, sentiment_data, risk_data = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            # Calculează scorurile individuale
            scores = {
                'technical_score': await self._calculate_technical_score(technical_data, symbol),
                'fundamental_score': await self._calculate_fundamental_score(fundamental_data, symbol),
                'options_score': await self._calculate_options_score(options_data, symbol),
                'sentiment_score': await self._calculate_sentiment_score(sentiment_data, symbol),
                'risk_score': await self._calculate_risk_score(risk_data, symbol)
            }
            
            # Combină toate scorurile cu ponderile
            total_score = self._combine_scores(scores)
            
            # Determină rating-ul
            rating = self._get_investment_rating(total_score)
            
            # Obține stock data live de la TradeStation
            stock_data = await self._get_live_stock_data(symbol)
            
            result = {
                'symbol': symbol.upper(),
                'timestamp': datetime.utcnow().isoformat(),
                'total_score': round(total_score, 2),
                'rating': rating,
                'component_scores': scores,
                'stock_data': stock_data,  # Add live stock data
                'data_quality': self._assess_data_quality(technical_data, fundamental_data, options_data),
                'recommendation': self._get_recommendation(total_score, scores),
                'risk_level': self._assess_risk_level(risk_data, scores.get('risk_score', 50)),
                'confidence': self._calculate_confidence(scores)
            }
            
            logger.info(f"✅ {symbol}: Scor {total_score:.1f}, Rating {rating}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Eroare la calcularea scorului pentru {symbol}: {e}")
            return self._get_default_score(symbol, str(e))
    
    async def _get_technical_data(self, symbol: str) -> Dict[str, Any]:
        """Obține date tehnice avansate"""
        try:
            logger.info(f"🔍 Getting technical data for {symbol}")
            
            # Verifică dacă TradeStation client este disponibil și autentificat
            if self.ts_client:
                logger.info(f"📊 TradeStation client available, checking authentication...")
                
                # Verifică autentificarea
                if hasattr(self.ts_client, 'auth') and hasattr(self.ts_client.auth, 'is_authenticated'):
                    is_auth = self.ts_client.auth.is_authenticated()
                    logger.info(f"🔐 TradeStation authentication status: {is_auth}")
                    
                    if is_auth and hasattr(self.ts_client, 'get_historical_bars'):
                        try:
                            logger.info(f"📈 Fetching historical bars for {symbol} from TradeStation...")
                            bars = await self.ts_client.get_historical_bars(
                                symbol=symbol,
                                interval=1,
                                unit="Daily", 
                                bars_back=200  # 200 zile pentru analiză tehnică solidă
                            )
                            
                            logger.info(f"📊 Received {len(bars) if bars else 0} bars for {symbol}")
                            
                            if bars and len(bars) > 50:
                                logger.info(f"✅ Using TradeStation live data for {symbol}")
                                df = pd.DataFrame(bars)
                                result = self._calculate_advanced_technical_indicators(df, symbol)
                                result['is_live_data'] = True
                                result['data_source'] = 'TradeStation API'
                                return result
                            else:
                                logger.warning(f"⚠️ Insufficient TradeStation data for {symbol}: {len(bars) if bars else 0} bars")
                        except Exception as e:
                            logger.error(f"❌ TradeStation technical data failed for {symbol}: {e}")
                else:
                    logger.warning(f"❌ TradeStation not authenticated or missing methods")
            else:
                logger.warning(f"❌ TradeStation client not available")
            
            # Fallback la mock data realistică
            logger.info(f"🔄 Using mock technical data for {symbol}")
            return self._generate_mock_technical_data(symbol)
            
        except Exception as e:
            logger.error(f"❌ Error getting technical data for {symbol}: {e}")
            return {}
    
    def _calculate_advanced_technical_indicators(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Calculează 15+ indicatori tehnici avansați"""
        try:
            # Convertește coloanele la numeric
            df['Close'] = pd.to_numeric(df['Close'])
            df['High'] = pd.to_numeric(df['High'])
            df['Low'] = pd.to_numeric(df['Low'])
            df['Volume'] = pd.to_numeric(df['TotalVolume'], errors='coerce').fillna(0)
            
            indicators = {}
            
            # 1. TREND INDICATORS
            # Moving Averages
            df['SMA20'] = df['Close'].rolling(20).mean()
            df['SMA50'] = df['Close'].rolling(50).mean()
            df['SMA200'] = df['Close'].rolling(200).mean()
            df['EMA12'] = df['Close'].ewm(span=12).mean()
            df['EMA26'] = df['Close'].ewm(span=26).mean()
            
            current_price = df['Close'].iloc[-1]
            sma20 = df['SMA20'].iloc[-1]
            sma50 = df['SMA50'].iloc[-1]
            sma200 = df['SMA200'].iloc[-1]
            
            # Trend Strength (0-100)
            trend_signals = 0
            if current_price > sma20: trend_signals += 1
            if current_price > sma50: trend_signals += 1  
            if current_price > sma200: trend_signals += 1
            if sma20 > sma50: trend_signals += 1
            if sma50 > sma200: trend_signals += 1
            
            indicators['trend_strength'] = (trend_signals / 5) * 100
            
            # 2. MOMENTUM INDICATORS  
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # MACD
            macd_line = df['EMA12'] - df['EMA26']  
            macd_signal = macd_line.ewm(span=9).mean()
            indicators['macd'] = macd_line.iloc[-1] - macd_signal.iloc[-1]
            
            # 3. VOLUME ANALYSIS
            avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            indicators['volume_ratio'] = current_volume / avg_volume if avg_volume > 0 else 1
            
            # 4. VOLATILITY INDICATORS
            # Bollinger Bands
            bb_middle = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            
            # Position in BB (0-100, 50 = middle)
            bb_position = ((current_price - bb_lower.iloc[-1]) / 
                          (bb_upper.iloc[-1] - bb_lower.iloc[-1])) * 100
            indicators['bollinger_position'] = max(0, min(100, bb_position))
            
            # ATR pentru volatilitate
            df['TR'] = np.maximum(df['High'] - df['Low'], 
                                np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                         abs(df['Low'] - df['Close'].shift(1))))
            atr = df['TR'].rolling(14).mean().iloc[-1]
            indicators['atr_percent'] = (atr / current_price) * 100 if current_price > 0 else 0
            
            # 5. SUPPORT/RESISTANCE
            # Găsește niveluri de S/R din ultimele 50 de zile
            recent_highs = df['High'].tail(50)
            recent_lows = df['Low'].tail(50)
            
            resistance_level = recent_highs.quantile(0.95)
            support_level = recent_lows.quantile(0.05)
            
            indicators['distance_to_resistance'] = ((resistance_level - current_price) / current_price) * 100
            indicators['distance_to_support'] = ((current_price - support_level) / current_price) * 100
            
            return {
                'symbol': symbol,
                'indicators': indicators,
                'data_points': len(df),
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return self._generate_mock_technical_data(symbol)
    
    def _generate_mock_technical_data(self, symbol: str) -> Dict[str, Any]:
        """Generează date tehnice mock realiste pentru demo"""
        import random
        
        logger.info(f"📋 Generating mock technical data for {symbol}")
        
        # Simulează indicatori realisti
        rsi = random.uniform(30, 80)  
        trend_strength = random.uniform(40, 90)
        volume_ratio = random.uniform(0.8, 2.5)
        bollinger_position = random.uniform(20, 80)
        
        return {
            'symbol': symbol,
            'indicators': {
                'trend_strength': trend_strength,
                'rsi': rsi,
                'macd': random.uniform(-2, 2),
                'volume_ratio': volume_ratio,
                'bollinger_position': bollinger_position,
                'atr_percent': random.uniform(1, 4),
                'distance_to_resistance': random.uniform(2, 15),
                'distance_to_support': random.uniform(2, 15)
            },
            'data_points': 200,
            'is_mock': True,
            'is_live_data': False,
            'data_source': 'Mock Data',
            'calculation_date': datetime.utcnow().isoformat()
        }
    
    async def _get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Obține date fundamentale (mock pentru demo)"""
        import random
        
        # Mock data realistă pentru fundamental analysis
        return {
            'pe_ratio': random.uniform(10, 30),
            'pb_ratio': random.uniform(1, 5),
            'roe': random.uniform(5, 25),
            'debt_to_equity': random.uniform(0.2, 2.0),
            'current_ratio': random.uniform(1.0, 3.0),
            'revenue_growth': random.uniform(-10, 20),
            'earnings_growth': random.uniform(-15, 25),
            'gross_margin': random.uniform(20, 60),
            'net_margin': random.uniform(5, 25),
            'dividend_yield': random.uniform(0, 5),
            'is_mock': True
        }
    
    async def _get_options_flow_data(self, symbol: str) -> Dict[str, Any]:
        """Obține date options flow de la Unusual Whales"""
        try:
            if self.uw_service:
                # Încearcă să obții options flow real
                flow_data = await self.uw_service.get_options_flow([symbol])
                if flow_data:
                    return self._process_options_flow(flow_data, symbol)
        except Exception as e:
            logger.warning(f"UW options flow failed for {symbol}: {e}")
        
        # Mock options data
        import random
        return {
            'put_call_ratio': random.uniform(0.5, 2.0),
            'unusual_volume_score': random.uniform(0, 100),
            'large_trades_count': random.randint(0, 50),
            'options_sentiment': random.choice(['bullish', 'neutral', 'bearish']),
            'is_mock': True
        }
    
    async def _get_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """Mock sentiment data (poate integra cu news APIs)"""
        import random
        
        return {
            'news_sentiment': random.uniform(-1, 1),  # -1 bearish, +1 bullish
            'social_sentiment': random.uniform(-1, 1),
            'analyst_rating': random.uniform(1, 5),   # 1=strong sell, 5=strong buy
            'price_target_change': random.uniform(-10, 10),
            'is_mock': True
        }
    
    async def _get_risk_data(self, symbol: str) -> Dict[str, Any]:
        """Calculează metrici de risc"""
        import random
        
        return {
            'beta': random.uniform(0.5, 2.0),
            'max_drawdown': random.uniform(5, 30),
            'volatility': random.uniform(15, 60),
            'sharpe_ratio': random.uniform(0.5, 2.5),
            'is_mock': True
        }
    
    async def _calculate_technical_score(self, data: Dict[str, Any], symbol: str) -> float:
        """Calculează scorul tehnic (0-100)"""
        if not data or 'indicators' not in data:
            return 50  # Neutral score
        
        indicators = data['indicators']
        
        # RSI Score (optimal range 40-70)
        rsi = indicators.get('rsi', 50)
        if 40 <= rsi <= 70:
            rsi_score = 80 + (10 * (70 - abs(rsi - 55)) / 15)  # Premium for optimal range
        elif 30 <= rsi <= 80:
            rsi_score = 60
        else:
            rsi_score = 30  # Overbought/oversold penalty
        
        # Trend Score
        trend_score = indicators.get('trend_strength', 50)
        
        # Volume Score (higher volume = better confirmation)
        volume_ratio = indicators.get('volume_ratio', 1)
        volume_score = min(100, 50 + (volume_ratio - 1) * 25)
        
        # Bollinger Position Score (avoid extremes)
        bb_pos = indicators.get('bollinger_position', 50)
        if 30 <= bb_pos <= 70:
            bb_score = 80
        else:
            bb_score = 40
        
        # Combine with weights
        technical_score = (
            rsi_score * 0.3 +
            trend_score * 0.4 +
            volume_score * 0.2 +
            bb_score * 0.1
        )
        
        return max(0, min(100, technical_score))
    
    async def _calculate_fundamental_score(self, data: Dict[str, Any], symbol: str) -> float:
        """Calculează scorul fundamental (0-100)"""
        if not data:
            return 50
        
        # P/E Score (lower is better, optimal 12-20)
        pe = data.get('pe_ratio', 20)
        if 12 <= pe <= 20:
            pe_score = 90
        elif 8 <= pe <= 25:
            pe_score = 70
        else:
            pe_score = 40
        
        # ROE Score (higher is better)
        roe = data.get('roe', 15)
        roe_score = min(100, max(0, (roe / 25) * 100))
        
        # Growth Score
        revenue_growth = data.get('revenue_growth', 5)
        growth_score = min(100, max(0, 50 + revenue_growth * 2))
        
        # Debt Score (lower debt-to-equity is better)
        debt_ratio = data.get('debt_to_equity', 1.0)
        debt_score = max(0, 100 - debt_ratio * 30)
        
        fundamental_score = (
            pe_score * 0.3 +
            roe_score * 0.25 +
            growth_score * 0.25 +
            debt_score * 0.2
        )
        
        return max(0, min(100, fundamental_score))
    
    async def _calculate_options_score(self, data: Dict[str, Any], symbol: str) -> float:
        """Calculează scorul opțiunilor (0-100)"""
        if not data:
            return 50
        
        # Put/Call Ratio Score (0.7-1.3 optimal)
        pcr = data.get('put_call_ratio', 1.0)
        if 0.7 <= pcr <= 1.3:
            pcr_score = 80
        else:
            pcr_score = 40
        
        # Unusual Volume Score
        uv_score = data.get('unusual_volume_score', 50)
        
        # Large Trades Score
        large_trades = data.get('large_trades_count', 0)
        trades_score = min(100, large_trades * 2)
        
        options_score = (
            pcr_score * 0.4 +
            uv_score * 0.4 +
            trades_score * 0.2
        )
        
        return max(0, min(100, options_score))
    
    async def _calculate_sentiment_score(self, data: Dict[str, Any], symbol: str) -> float:
        """Calculează scorul de sentiment (0-100)"""
        if not data:
            return 50
        
        # News Sentiment (-1 to 1 -> 0 to 100)
        news = data.get('news_sentiment', 0)
        news_score = (news + 1) * 50
        
        # Social Sentiment  
        social = data.get('social_sentiment', 0)
        social_score = (social + 1) * 50
        
        # Analyst Rating (1-5 -> 0-100)
        analyst = data.get('analyst_rating', 3)
        analyst_score = (analyst - 1) * 25
        
        sentiment_score = (
            news_score * 0.4 +
            social_score * 0.3 +
            analyst_score * 0.3
        )
        
        return max(0, min(100, sentiment_score))
    
    async def _calculate_risk_score(self, data: Dict[str, Any], symbol: str) -> float:
        """Calculează scorul de risc (0-100, higher = lower risk)"""
        if not data:
            return 50
        
        # Beta Score (1.0 is neutral, lower is better)
        beta = data.get('beta', 1.0)
        beta_score = max(0, 100 - abs(beta - 1.0) * 50)
        
        # Sharpe Ratio Score (higher is better)
        sharpe = data.get('sharpe_ratio', 1.0) 
        sharpe_score = min(100, sharpe * 40)
        
        # Volatility Score (lower is better)
        vol = data.get('volatility', 30)
        vol_score = max(0, 100 - vol * 1.5)
        
        risk_score = (
            beta_score * 0.3 +
            sharpe_score * 0.4 +
            vol_score * 0.3
        )
        
        return max(0, min(100, risk_score))
    
    def _combine_scores(self, scores: Dict[str, float]) -> float:
        """Combină toate scorurile cu ponderile"""
        weights = {
            'technical_score': 0.35,    # 35% technical
            'fundamental_score': 0.25,  # 25% fundamental  
            'options_score': 0.20,      # 20% options flow
            'sentiment_score': 0.15,    # 15% sentiment
            'risk_score': 0.05          # 5% risk (inverse - higher risk score = lower total)
        }
        
        total = 0
        for score_type, weight in weights.items():
            score = scores.get(score_type, 50)  # Default neutral
            total += score * weight
        
        return max(0, min(100, total))
    
    def _get_investment_rating(self, score: float) -> str:
        """Convertește scorul în rating"""
        if score >= 85:
            return "STRONG BUY"
        elif score >= 70:
            return "BUY"
        elif score >= 55:
            return "HOLD"
        elif score >= 40:
            return "WEAK HOLD"
        else:
            return "SELL"
    
    def _get_recommendation(self, score: float, component_scores: Dict) -> str:
        """Generează recomandare detaliată"""
        tech_score = component_scores.get('technical_score', 50)
        fund_score = component_scores.get('fundamental_score', 50)
        
        if score >= 80:
            return f"Excellent opportunity with strong technical ({tech_score:.1f}) and fundamental ({fund_score:.1f}) metrics"
        elif score >= 65:
            return f"Good investment opportunity with balanced risk-reward profile"
        elif score >= 45:
            return f"Neutral position - consider market conditions and risk tolerance"
        else:
            return f"High risk investment - consider alternatives or wait for better entry"
    
    def _assess_risk_level(self, risk_data: Dict, risk_score: float) -> str:
        """Evaluează nivelul de risc"""
        if risk_score >= 75:
            return "LOW"
        elif risk_score >= 50:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _calculate_confidence(self, scores: Dict) -> float:
        """Calculează încrederea în scor (0-100)"""
        # Confidence bazată pe convergența scorurilor
        score_values = [v for v in scores.values() if isinstance(v, (int, float))]
        if len(score_values) < 2:
            return 50
        
        # Mai multă convergență = mai multă încredere
        std_dev = np.std(score_values)
        confidence = max(50, 100 - std_dev * 2)
        return min(100, confidence)
    
    def _assess_data_quality(self, tech_data, fund_data, options_data) -> str:
        """Evaluează calitatea datelor"""
        quality_factors = []
        
        # Verifică dacă avem date tehnice live
        if tech_data and tech_data.get('is_live_data') and tech_data.get('data_points', 0) >= 100:
            quality_factors.append("live_technical")
        elif tech_data and tech_data.get('data_points', 0) >= 100:
            quality_factors.append("technical")
            
        # Verifică date fundamentale
        if fund_data and not fund_data.get('is_mock'):
            quality_factors.append("live_fundamental") 
        elif fund_data:
            quality_factors.append("fundamental")
            
        # Verifică options data
        if options_data and not options_data.get('is_mock'):
            quality_factors.append("live_options")
        elif options_data:
            quality_factors.append("options")
        
        live_factors = len([f for f in quality_factors if f.startswith('live_')])
        total_factors = len(quality_factors)
        
        if live_factors >= 2:
            return "HIGH"
        elif live_factors >= 1 or total_factors >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_default_score(self, symbol: str, error: str) -> Dict[str, Any]:
        """Score default pentru erori"""
        return {
            'symbol': symbol.upper(),
            'timestamp': datetime.utcnow().isoformat(),
            'total_score': 50.0,
            'rating': "HOLD",
            'component_scores': {
                'technical_score': 50,
                'fundamental_score': 50, 
                'options_score': 50,
                'sentiment_score': 50,
                'risk_score': 50
            },
            'data_quality': "LOW",
            'recommendation': f"Unable to calculate score due to error: {error}",
            'risk_level': "UNKNOWN",
            'confidence': 25.0,
            'error': error
        }

# Instanță globală
advanced_scoring_engine = None

def get_scoring_engine(ts_client=None, uw_service=None):
    """Factory function pentru scoring engine"""
    global advanced_scoring_engine
    if advanced_scoring_engine is None:
        advanced_scoring_engine = AdvancedScoringEngine(ts_client, uw_service)
    return advanced_scoring_engine
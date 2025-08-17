"""
Investment Scoring System - Algoritm pentru cele mai bune oportunități de investiții
Enhanced with Technical Analysis: Overall Trend, Indicators, Price Action
SCANNER ENGINE pentru toate tickerele din TradeStation
"""
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from enhanced_ticker_data import enhanced_ticker_manager
from technical_analysis_enhanced import technical_analyzer
from market_sentiment_analyzer import market_sentiment_analyzer, sentiment_to_investment_score

logger = logging.getLogger(__name__)

# MongoDB Connection pentru stocare rezultate scanner
mongo_client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
db = mongo_client['flowmind_db']
scanned_stocks_collection = db['scanned_stocks']

class StockScanner:
    """Scanner Engine pentru toate tickerele din TradeStation"""
    
    def __init__(self, investment_scorer):
        self.scorer = investment_scorer
        self.ts_client = None  # TradeStation client pentru tickere
        self.max_stocks = 1000  # Păstrăm top 1000 acțiuni
        
    async def get_all_tickers_from_ts(self) -> List[str]:
        """Obține toate tickerele din TradeStation"""
        try:
            # Lista de tickere majore pentru început (S&P 500 + NASDAQ 100 + alte majore)
            major_tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B', 'V', 'JNJ',
                'WMT', 'JPM', 'PG', 'UNH', 'DIS', 'HD', 'MA', 'PFE', 'BAC', 'ABBV',
                'ADBE', 'CRM', 'KO', 'PEP', 'TMO', 'COST', 'AVGO', 'DHR', 'NEE', 'ABT',
                'CMCSA', 'XOM', 'LLY', 'VZ', 'ORCL', 'INTC', 'AMD', 'COP', 'PM', 'HON',
                'LIN', 'CVX', 'NOW', 'IBM', 'QCOM', 'UBER', 'TXN', 'SPGI', 'LOW', 'CAT',
                'GS', 'NFLX', 'INTU', 'AMGN', 'RTX', 'ISRG', 'MDT', 'BA', 'SBUX', 'DE',
                'AMAT', 'GILD', 'AXP', 'BKNG', 'LRCX', 'TJX', 'SYK', 'BLK', 'MU', 'TMUS',
                'REGN', 'PYPL', 'SCHW', 'PANW', 'C', 'PGR', 'VRTX', 'MMC', 'CB', 'MDLZ',
                'SO', 'FI', 'BSX', 'EOG', 'KLAC', 'WM', 'EL', 'SNPS', 'ITW', 'ADI',
                'MSI', 'CSX', 'CME', 'ZTS', 'HCA', 'SHW', 'APD', 'CDNS', 'MO', 'USB'
            ]
            
            # TODO: Integrare TradeStation API pentru lista completă de tickere
            # Pentru acum folosim lista majoră + putem extinde cu mai multe
            
            logger.info(f"Scanăm {len(major_tickers)} tickere majore")
            return major_tickers
            
        except Exception as e:
            logger.error(f"Eroare la obținerea tickerelor: {e}")
            return []
    
    async def scan_all_stocks(self) -> Dict[str, Any]:
        """Scanner principal - analizează toate tickerele și păstrează top 1000"""
        logger.info("🔄 Începe scanarea completă a tuturor tickerelor...")
        
        # Obține lista de tickere
        tickers = await self.get_all_tickers_from_ts()
        if not tickers:
            return {"error": "Nu s-au putut obține tickerele"}
        
        scanned_results = []
        processed = 0
        errors = 0
        
        # Scanează fiecare ticker
        for ticker in tickers:
            try:
                logger.info(f"Scanez {ticker} ({processed + 1}/{len(tickers)})")
                
                # Obține scoring pentru ticker folosind metoda corectă
                # First get stock data
                stock_data = await enhanced_ticker_manager.get_real_time_quote(ticker)
                if not stock_data:
                    logger.warning(f"⚠️ {ticker}: Nu s-au putut obține datele stock")
                    continue
                
                result = await self.scorer.calculate_investment_score(stock_data)
                
                if result and 'total_score' in result:
                    # Adaugă informații suplimentare
                    result['ticker'] = ticker
                    result['scanned_at'] = datetime.utcnow()
                    result['scan_id'] = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                    
                    scanned_results.append(result)
                    logger.info(f"✅ {ticker}: Score {result['total_score']:.1f}")
                else:
                    logger.warning(f"⚠️ {ticker}: Nu s-a putut calcula scorul")
                    
                processed += 1
                
                # Pauză scurtă pentru a nu supraîncărca API-urile
                await asyncio.sleep(0.5)
                
            except Exception as e:
                errors += 1
                logger.error(f"❌ Eroare la scanarea {ticker}: {e}")
                continue
        
        # Sortează după scor (descrescător) și păstrează top 1000
        scanned_results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        top_stocks = scanned_results[:self.max_stocks]
        
        # Salvează în MongoDB
        await self.save_scan_results(top_stocks)
        
        summary = {
            'scan_completed_at': datetime.utcnow(),
            'total_tickers_processed': processed,
            'successful_scans': len(scanned_results),
            'errors': errors,
            'top_stocks_count': len(top_stocks),
            'top_10_stocks': [
                {
                    'ticker': stock['ticker'],
                    'score': stock['total_score'],
                    'rating': stock.get('rating', 'N/A')
                }
                for stock in top_stocks[:10]
            ]
        }
        
        logger.info(f"🏆 Scanare completă: {len(top_stocks)} acțiuni top din {processed} procesate")
        return summary
    
    async def save_scan_results(self, results: List[Dict[str, Any]]):
        """Salvează rezultatele scanării în MongoDB"""
        try:
            # Șterge rezultatele vechi
            await scanned_stocks_collection.delete_many({})
            
            # Inserează rezultatele noi
            if results:
                await scanned_stocks_collection.insert_many(results)
                logger.info(f"💾 Salvate {len(results)} rezultate în MongoDB")
            
        except Exception as e:
            logger.error(f"Eroare la salvarea rezultatelor: {e}")
    
    async def get_top_stocks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obține top acțiuni din ultimul scan"""
        try:
            cursor = scanned_stocks_collection.find({}).sort('total_score', -1).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Eroare la obținerea top acțiuni: {e}")
            return []

# Instanță globală scanner
stock_scanner = None


class InvestmentScorer:
    def __init__(self):
        # Enhanced weights to include sentiment analysis (40/40/20 split)
        self.weights = {
            # Fundamental Analysis (40%)
            'pe_score': 0.07,           # P/E ratio 
            'pb_score': 0.05,           # Price-to-book
            'value_score': 0.07,        # Overall valuation
            'growth_score': 0.07,       # Revenue/earnings growth
            'profitability_score': 0.06, # ROE, margins
            'dividend_score': 0.04,     # Dividend yield & stability
            'financial_health': 0.04,   # Debt ratios, cash
            
            # Technical Analysis (40%)
            'trend_score': 0.12,        # Overall trend direction & strength
            'momentum_score': 0.10,     # RSI, MACD, Stochastic
            'volume_score': 0.06,       # Volume confirmation
            'price_action_score': 0.08, # Price patterns, volatility
            'support_resistance_score': 0.04, # S/R levels
            
            # Sentiment Analysis (20%) - NEW!
            'sentiment_score': 0.20,    # Market sentiment from multiple sources
            
            # Market Metrics (Combined)
            'volatility_score': 0.05,   # Risk (Beta, volatility)
        }
    
    async def calculate_investment_score(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive investment score with technical analysis and sentiment"""
        try:
            symbol = stock_data.get('symbol', 'N/A')
            
            # Get technical analysis and sentiment data concurrently
            technical_task = technical_analyzer.analyze_stock_technical(symbol)
            sentiment_task = market_sentiment_analyzer.analyze_market_sentiment(symbol)
            
            technical_data, sentiment_data = await asyncio.gather(technical_task, sentiment_task)
            
            # Calculate individual scores
            scores = {}
            
            # Fundamental scores
            scores['pe_score'] = self._calculate_pe_score(stock_data)
            scores['pb_score'] = self._calculate_pb_score(stock_data)
            scores['value_score'] = self._calculate_value_score(stock_data)
            scores['growth_score'] = self._calculate_growth_score(stock_data)
            scores['profitability_score'] = self._calculate_profitability_score(stock_data)
            scores['dividend_score'] = self._calculate_dividend_score(stock_data)
            scores['financial_health'] = self._calculate_financial_health_score(stock_data)
            scores['volatility_score'] = self._calculate_volatility_score(stock_data)
            
            # Technical scores
            technical_scores = technical_data.get('technical_score', {})
            scores['trend_score'] = technical_scores.get('trend_score', 50)
            scores['momentum_score'] = technical_scores.get('momentum_score', 50)
            scores['volume_score'] = technical_scores.get('volume_score', 50)
            scores['price_action_score'] = technical_scores.get('price_action_score', 50)
            scores['support_resistance_score'] = technical_scores.get('support_resistance_score', 50)
            
            # Sentiment score (NEW!)
            scores['sentiment_score'] = sentiment_to_investment_score(sentiment_data)
            
            # Calculate weighted total score
            total_score = sum(scores[metric] * self.weights[metric] for metric in scores)
            total_score = max(0, min(100, total_score))
            
            # Determine investment rating with technical and sentiment consideration
            rating = self._get_enhanced_investment_rating(total_score, technical_data, sentiment_data)
            
            # Create enhanced recommendation explanation
            explanation = self._generate_enhanced_explanation(stock_data, scores, total_score, technical_data, sentiment_data)
            
            # Generate technical signals
            technical_signals = technical_data.get('signals', [])
            
            # Calculate separate component scores
            fundamental_keys = ['pe_score', 'pb_score', 'value_score', 'growth_score', 'profitability_score', 'dividend_score', 'financial_health']
            technical_keys = ['trend_score', 'momentum_score', 'volume_score', 'price_action_score', 'support_resistance_score']
            sentiment_keys = ['sentiment_score']
            
            try:
                # Calculate fundamental score
                fundamental_weighted_sum = sum(scores[k] * self.weights[k] for k in fundamental_keys if k in scores)
                fundamental_weights_sum = sum(self.weights[k] for k in fundamental_keys if k in self.weights)
                fundamental_score = fundamental_weighted_sum / fundamental_weights_sum if fundamental_weights_sum > 0 else 50
                
                # Calculate technical score  
                technical_weighted_sum = sum(scores[k] * self.weights[k] for k in technical_keys if k in scores)
                technical_weights_sum = sum(self.weights[k] for k in technical_keys if k in self.weights)
                technical_score = technical_weighted_sum / technical_weights_sum if technical_weights_sum > 0 else 50
                
                # Calculate sentiment score
                sentiment_weighted_sum = sum(scores[k] * self.weights[k] for k in sentiment_keys if k in scores)
                sentiment_weights_sum = sum(self.weights[k] for k in sentiment_keys if k in self.weights)
                sentiment_score = sentiment_weighted_sum / sentiment_weights_sum if sentiment_weights_sum > 0 else 50
                
            except Exception as e:
                logger.error(f"Error calculating component scores: {str(e)}")
                fundamental_score = 50
                technical_score = 50
                sentiment_score = 50
            
            return {
                'symbol': symbol,
                'total_score': round(total_score, 2),
                'rating': rating,
                'individual_scores': {k: round(v, 2) for k, v in scores.items()},
                'fundamental_score': round(fundamental_score, 2),
                'technical_score': round(technical_score, 2),
                'sentiment_score': round(sentiment_score, 2),  # NEW!
                'explanation': explanation,
                'risk_level': self._assess_enhanced_risk_level(stock_data, scores, technical_data, sentiment_data),
                'investment_horizon': self._recommend_enhanced_investment_horizon(scores, technical_data, sentiment_data),
                'key_strengths': self._identify_enhanced_key_strengths(scores, technical_data, sentiment_data),
                'key_risks': self._identify_enhanced_key_risks(scores, technical_data, sentiment_data),
                'technical_analysis': {
                    'trend_direction': technical_data.get('trend_analysis', {}).get('direction', 'NEUTRAL'),
                    'trend_strength': technical_data.get('trend_analysis', {}).get('strength', 50),
                    'key_indicators': self._get_key_technical_indicators(technical_data),
                    'signals': technical_signals,
                    'support_resistance': technical_data.get('support_resistance', {})
                },
                'sentiment_analysis': {
                    'direction': sentiment_data.get('insights', {}).get('direction', 'UNKNOWN'),
                    'strength': sentiment_data.get('insights', {}).get('strength', 'Unknown'),
                    'market_mood': sentiment_data.get('market_mood', 'UNCERTAIN'),
                    'confidence': sentiment_data.get('confidence_level', 0.0),
                    'dominant_source': sentiment_data.get('insights', {}).get('dominant_source', 'None'),
                    'key_themes': sentiment_data.get('insights', {}).get('key_themes', []),
                    'total_mentions': sentiment_data.get('total_mentions', 0),
                    'summary': sentiment_data.get('insights', {}).get('summary', 'No sentiment data available')
                },
                'last_updated': datetime.utcnow().isoformat(),
                'analysis_type': 'ENHANCED_WITH_TECHNICAL_AND_SENTIMENT'
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced investment score for {stock_data.get('symbol', 'unknown')}: {str(e)}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._get_default_score(stock_data.get('symbol', 'N/A'))
    
    def _calculate_pe_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on P/E ratio (lower is better, but not too low)"""
        pe_ratio = stock_data.get('pe_ratio')
        if not pe_ratio or pe_ratio <= 0:
            return 50  # Neutral score for missing/invalid P/E
        
        # Optimal P/E range: 15-25
        if 15 <= pe_ratio <= 25:
            return 90
        elif 10 <= pe_ratio < 15:
            return 80
        elif 25 < pe_ratio <= 35:
            return 70
        elif 5 <= pe_ratio < 10:
            return 60
        elif 35 < pe_ratio <= 50:
            return 50
        else:
            return 30  # Very high or very low P/E
    
    def _calculate_pb_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on estimated Price-to-Book ratio"""
        # Since we don't have direct P/B, estimate based on market cap and other factors
        market_cap = stock_data.get('market_cap', 0)
        price = stock_data.get('price', 0)
        
        if market_cap == 0 or price == 0:
            return 50
        
        # Estimate P/B score based on market cap size and sector
        sector = stock_data.get('sector', 'Unknown')
        
        # Tech stocks typically have higher P/B ratios
        if sector == 'Technology':
            return 70  # Generally acceptable for tech
        elif sector in ['Healthcare', 'Financial Services']:
            return 75  # Moderate P/B expectations
        else:
            return 80  # Conservative sectors
    
    def _calculate_value_score(self, stock_data: Dict[str, Any]) -> float:
        """Overall valuation score based on multiple factors"""
        price = stock_data.get('price', 0)
        week_52_low = stock_data.get('week_52_low', 0)
        week_52_high = stock_data.get('week_52_high', 0)
        
        if not all([price, week_52_low, week_52_high]):
            return 50
        
        # Calculate position within 52-week range
        range_position = (price - week_52_low) / (week_52_high - week_52_low)
        
        # Lower position = better value (inverted score)
        if range_position <= 0.3:
            return 90  # Near 52-week low = good value
        elif range_position <= 0.5:
            return 75  # Below middle = decent value
        elif range_position <= 0.7:
            return 60  # Above middle = fair value
        else:
            return 40   # Near 52-week high = expensive
    
    def _calculate_momentum_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on price momentum"""
        change_percent = stock_data.get('change_percent', 0)
        
        # Recent positive momentum is good, but not excessive
        if 0.5 <= change_percent <= 3.0:
            return 85  # Good positive momentum
        elif -0.5 <= change_percent < 0.5:
            return 70  # Stable
        elif 3.0 < change_percent <= 5.0:
            return 75  # Strong but not excessive
        elif -2.0 <= change_percent < -0.5:
            return 60  # Minor decline
        elif change_percent > 5.0:
            return 50  # Potentially overheated
        else:
            return 40   # Significant decline
    
    def _calculate_growth_score(self, stock_data: Dict[str, Any]) -> float:
        """Estimate growth score based on available data"""
        sector = stock_data.get('sector', 'Unknown')
        market_cap = stock_data.get('market_cap', 0)
        
        # Sector-based growth expectations
        growth_sectors = ['Technology', 'Healthcare', 'Communication Services']
        if sector in growth_sectors:
            return 80
        elif sector in ['Consumer Cyclical', 'Industrials']:
            return 70
        else:
            return 60
    
    def _calculate_profitability_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on profitability metrics"""
        pe_ratio = stock_data.get('pe_ratio')
        sector = stock_data.get('sector', 'Unknown')
        
        if not pe_ratio or pe_ratio <= 0:
            return 30  # No earnings = poor profitability
        
        # Having a positive P/E means profitable
        base_score = 70
        
        # Adjust by sector profitability expectations
        high_margin_sectors = ['Technology', 'Healthcare', 'Financial Services']
        if sector in high_margin_sectors:
            return min(90, base_score + 15)
        else:
            return base_score
    
    def _calculate_dividend_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on dividend yield"""
        dividend_yield = stock_data.get('dividend_yield')
        
        if not dividend_yield:
            return 50  # No dividend = neutral
        
        dividend_percent = dividend_yield * 100
        
        if 2.0 <= dividend_percent <= 4.0:
            return 90  # Attractive dividend
        elif 1.0 <= dividend_percent < 2.0:
            return 75  # Moderate dividend
        elif 4.0 < dividend_percent <= 6.0:
            return 80  # High dividend
        elif dividend_percent > 6.0:
            return 60   # Potentially unsustainable
        else:
            return 50   # Very low dividend
    
    def _calculate_financial_health_score(self, stock_data: Dict[str, Any]) -> float:
        """Assess financial health"""
        market_cap = stock_data.get('market_cap', 0)
        
        # Larger market cap generally indicates more financial stability
        if market_cap >= 100e9:  # $100B+
            return 90  # Large cap = stable
        elif market_cap >= 10e9:  # $10B+
            return 80  # Mid-large cap = good
        elif market_cap >= 2e9:   # $2B+
            return 70  # Mid cap = decent
        else:
            return 55  # Small cap = higher risk
    
    def _calculate_volume_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on trading volume (liquidity)"""
        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume', 0)
        
        if not avg_volume or avg_volume == 0:
            return 50
        
        volume_ratio = volume / avg_volume
        
        if 0.8 <= volume_ratio <= 1.5:
            return 85  # Normal volume
        elif 0.5 <= volume_ratio < 0.8:
            return 70  # Below average volume
        elif 1.5 < volume_ratio <= 2.0:
            return 80  # Above average volume
        else:
            return 60   # Extreme volume (high or low)
    
    def _calculate_volatility_score(self, stock_data: Dict[str, Any]) -> float:
        """Score based on volatility (lower volatility = higher score)"""
        beta = stock_data.get('beta')
        
        if not beta:
            return 60  # Unknown risk
        
        if 0.7 <= beta <= 1.2:
            return 85  # Market-level risk
        elif 0.4 <= beta < 0.7:
            return 90  # Lower risk
        elif 1.2 < beta <= 1.5:
            return 70  # Higher risk
        else:
            return 50   # High volatility
    
    def _get_enhanced_investment_rating(self, score: float, technical_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> str:
        """Enhanced investment rating considering technical analysis and sentiment"""
        base_rating = self._get_investment_rating(score)
        
        # Adjust rating based on technical signals
        trend_direction = technical_data.get('trend_analysis', {}).get('direction', 'NEUTRAL')
        signals = technical_data.get('signals', [])
        
        # Count bullish vs bearish signals
        buy_signals = len([s for s in signals if s.get('signal') == 'BUY'])
        sell_signals = len([s for s in signals if s.get('signal') == 'SELL'])
        
        # Get sentiment data
        sentiment_direction = sentiment_data.get('insights', {}).get('direction', 'UNKNOWN')
        sentiment_confidence = sentiment_data.get('confidence_level', 0.0)
        
        # Triple confluence: Fundamental + Technical + Sentiment
        bullish_confluence = (
            trend_direction == 'BULLISH' and 
            buy_signals > sell_signals and 
            sentiment_direction == 'BULLISH' and 
            sentiment_confidence > 0.5
        )
        
        bearish_confluence = (
            trend_direction == 'BEARISH' and 
            sell_signals > buy_signals and 
            sentiment_direction == 'BEARISH' and 
            sentiment_confidence > 0.5
        )
        
        # Adjust rating based on confluence
        if bullish_confluence:
            if base_rating == 'HOLD +':
                return 'BUY STRONG'
            elif base_rating == 'HOLD':
                return 'BUY'
            elif base_rating == 'BUY':
                return 'BUY STRONG'
        elif bearish_confluence:
            if base_rating == 'BUY STRONG':
                return 'BUY'
            elif base_rating == 'BUY':
                return 'HOLD +'
            elif base_rating == 'HOLD +':
                return 'HOLD'
        
        # Partial adjustments for 2-way confluence
        tech_sentiment_bullish = (
            trend_direction == 'BULLISH' and 
            sentiment_direction == 'BULLISH' and 
            sentiment_confidence > 0.4
        )
        
        tech_sentiment_bearish = (
            trend_direction == 'BEARISH' and 
            sentiment_direction == 'BEARISH' and 
            sentiment_confidence > 0.4
        )
        
        if tech_sentiment_bullish and base_rating == 'HOLD':
            return 'HOLD +'
        elif tech_sentiment_bearish and base_rating == 'BUY':
            return 'HOLD +'
        
        return base_rating
    
    def _generate_enhanced_explanation(self, stock_data: Dict[str, Any], scores: Dict[str, float], total_score: float, technical_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> str:
        """Generate enhanced explanation including technical analysis and sentiment"""
        symbol = stock_data.get('symbol', 'N/A')
        sector = stock_data.get('sector', 'Unknown')
        price = stock_data.get('price', 0)
        
        # Get technical information
        trend_direction = technical_data.get('trend_analysis', {}).get('direction', 'NEUTRAL')
        trend_strength = technical_data.get('trend_analysis', {}).get('strength', 50)
        
        # Get sentiment information
        sentiment_direction = sentiment_data.get('insights', {}).get('direction', 'UNKNOWN')
        sentiment_strength = sentiment_data.get('insights', {}).get('strength', 'Unknown')
        market_mood = sentiment_data.get('market_mood', 'UNCERTAIN')
        
        explanation = f"{symbol} ({sector}) at ${price:.2f} "
        
        if total_score >= 75:
            explanation += "shows strong investment potential with "
        elif total_score >= 65:
            explanation += "presents a solid investment opportunity with "
        elif total_score >= 55:
            explanation += "offers moderate investment appeal with "
        else:
            explanation += "faces investment challenges with "
        
        # Build context combining all three analyses
        context_parts = []
        
        # Technical context
        if trend_direction == 'BULLISH':
            context_parts.append(f"bullish technical trend (strength: {trend_strength:.0f}%)")
        elif trend_direction == 'BEARISH':
            context_parts.append(f"bearish technical trend (strength: {trend_strength:.0f}%)")
        else:
            context_parts.append("neutral technical conditions")
        
        # Sentiment context
        if sentiment_direction == 'BULLISH':
            context_parts.append(f"{sentiment_strength.lower()} positive market sentiment ({market_mood.lower()})")
        elif sentiment_direction == 'BEARISH':
            context_parts.append(f"{sentiment_strength.lower()} negative market sentiment ({market_mood.lower()})")
        else:
            context_parts.append(f"mixed market sentiment ({market_mood.lower()})")
        
        # Calculate component strength
        fundamental_score = sum(scores[k] * self.weights[k] for k in ['pe_score', 'pb_score', 'value_score', 'growth_score', 'profitability_score', 'dividend_score', 'financial_health'] if k in scores)
        technical_score = sum(scores[k] * self.weights[k] for k in ['trend_score', 'momentum_score', 'volume_score', 'price_action_score', 'support_resistance_score'] if k in scores)
        sentiment_score = scores.get('sentiment_score', 50) * self.weights.get('sentiment_score', 0.2)
        
        # Find strongest component
        components = [
            ('fundamentals', fundamental_score),
            ('technicals', technical_score), 
            ('sentiment', sentiment_score)
        ]
        strongest = max(components, key=lambda x: x[1])
        
        if strongest[0] == 'fundamentals':
            explanation += f"strong fundamentals, {context_parts[0]}, and {context_parts[1]}."
        elif strongest[0] == 'technicals':
            explanation += f"{context_parts[0]}, decent fundamentals, and {context_parts[1]}."
        else:
            explanation += f"{context_parts[1]}, {context_parts[0]}, and balanced fundamentals."
        
        return explanation
    
    def _assess_enhanced_risk_level(self, stock_data: Dict[str, Any], scores: Dict[str, float], technical_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> str:
        """Enhanced risk assessment including technical volatility and sentiment"""
        # Base risk from fundamental analysis
        volatility_score = scores.get('volatility_score', 50)
        financial_health = scores.get('financial_health', 50)
        
        # Technical risk factors
        trend_strength = technical_data.get('trend_analysis', {}).get('strength', 50)
        price_action = technical_data.get('price_action', {})
        volatility = price_action.get('volatility', 0.3)
        
        # Sentiment risk factors
        sentiment_confidence = sentiment_data.get('confidence_level', 0.0)
        market_mood = sentiment_data.get('market_mood', 'UNCERTAIN')
        
        # Combine risk factors
        base_risk_score = (volatility_score + financial_health) / 2
        
        # Adjust for technical volatility
        if volatility > 0.5:  # High volatility
            base_risk_score -= 10
        elif volatility < 0.2:  # Low volatility
            base_risk_score += 10
        
        # Adjust for sentiment uncertainty
        if sentiment_confidence < 0.3 or market_mood == 'UNCERTAIN':
            base_risk_score -= 8  # Higher risk due to sentiment uncertainty
        elif market_mood in ['PESSIMISTIC', 'CAUTIOUSLY_NEGATIVE']:
            base_risk_score -= 5
        elif market_mood in ['OPTIMISTIC', 'CAUTIOUSLY_POSITIVE']:
            base_risk_score += 5
        
        # Adjust for trend reliability
        trend_reliability = technical_data.get('trend_analysis', {}).get('short_term', {}).get('reliability', 'LOW')
        if trend_reliability == 'LOW':
            base_risk_score -= 5
        
        if base_risk_score >= 75:
            return "LOW"
        elif base_risk_score >= 60:
            return "MODERATE"
        else:
            return "HIGH"
    
    def _recommend_enhanced_investment_horizon(self, scores: Dict[str, float], technical_data: Dict[str, Any], sentiment_data: Dict[str, Any] = None) -> str:
        """Enhanced investment horizon recommendation including sentiment analysis"""
        trend_direction = technical_data.get('trend_analysis', {}).get('direction', 'NEUTRAL')
        momentum_score = scores.get('momentum_score', 50)
        value_score = scores.get('value_score', 50)
        
        # Include sentiment in decision making
        sentiment_direction = 'NEUTRAL'
        if sentiment_data:
            sentiment_direction = sentiment_data.get('insights', {}).get('direction', 'NEUTRAL')
        
        # Strong technical momentum + positive sentiment suggests shorter-term opportunities
        if momentum_score >= 80 and trend_direction in ['BULLISH', 'BEARISH']:
            if sentiment_direction == 'POSITIVE':
                return "SHORT-TERM"
            else:
                return "MEDIUM-TERM"
        # Good value with neutral/positive technical and sentiment suggests long-term
        elif value_score >= 75 and trend_direction != 'BEARISH' and sentiment_direction != 'NEGATIVE':
            return "LONG-TERM"
        else:
            return "MEDIUM-TERM"
    
    def _identify_enhanced_key_strengths(self, scores: Dict[str, float], technical_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> List[str]:
        """Enhanced key strengths identification including sentiment"""
        strengths = []
        
        # Fundamental strengths
        if scores.get('pe_score', 0) >= 80:
            strengths.append("Attractive Valuation")
        if scores.get('dividend_score', 0) >= 80:
            strengths.append("Strong Dividend")
        if scores.get('financial_health', 0) >= 80:
            strengths.append("Financial Stability")
        if scores.get('profitability_score', 0) >= 80:
            strengths.append("High Profitability")
        
        # Technical strengths
        if scores.get('trend_score', 0) >= 80:
            strengths.append("Strong Technical Trend")
        if scores.get('momentum_score', 0) >= 80:
            strengths.append("Positive Momentum")
        if scores.get('volume_score', 0) >= 80:
            strengths.append("Volume Confirmation")
        
        # Sentiment strengths
        sentiment_score = scores.get('sentiment_score', 50)
        if sentiment_score >= 80:
            strengths.append("Very Positive Sentiment")
        elif sentiment_score >= 70:
            strengths.append("Positive Market Sentiment")
        
        # Specific sentiment factors
        sentiment_direction = sentiment_data.get('insights', {}).get('direction', 'UNKNOWN')
        sentiment_confidence = sentiment_data.get('confidence_level', 0.0)
        
        if sentiment_direction == 'BULLISH' and sentiment_confidence > 0.7:
            strengths.append("High-Confidence Bullish Sentiment")
        
        market_mood = sentiment_data.get('market_mood', 'UNCERTAIN')
        if market_mood == 'OPTIMISTIC':
            strengths.append("Optimistic Market Mood")
        
        # Specific technical patterns
        trend_direction = technical_data.get('trend_analysis', {}).get('direction', 'NEUTRAL')
        if trend_direction == 'BULLISH':
            strengths.append("Bullish Trend")
        
        signals = technical_data.get('signals', [])
        buy_signals = len([s for s in signals if s.get('signal') == 'BUY'])
        if buy_signals >= 2:
            strengths.append("Multiple Buy Signals")
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_enhanced_key_risks(self, scores: Dict[str, float], technical_data: Dict[str, Any], sentiment_data: Dict[str, Any] = None) -> List[str]:
        """Enhanced key risks identification including sentiment analysis"""
        risks = []
        
        # Fundamental risks
        if scores.get('pe_score', 100) <= 40:
            risks.append("Valuation Concerns")
        if scores.get('financial_health', 100) <= 40:
            risks.append("Financial Risk")
        if scores.get('volatility_score', 100) <= 40:
            risks.append("High Volatility")
        
        # Technical risks
        if scores.get('trend_score', 100) <= 40:
            risks.append("Weak Technical Trend")
        if scores.get('momentum_score', 100) <= 40:
            risks.append("Negative Momentum")
        
        # Include sentiment risks
        if sentiment_data:
            sentiment_direction = sentiment_data.get('insights', {}).get('direction', 'NEUTRAL')
            if sentiment_direction == 'NEGATIVE':
                risks.append("Negative Market Sentiment")
            elif sentiment_data.get('insights', {}).get('strength', 'Medium') == 'Weak':
                risks.append("Weak Sentiment Conviction")
        
        # Specific technical risks
        trend_direction = technical_data.get('trend_analysis', {}).get('direction', 'NEUTRAL')
        if trend_direction == 'BEARISH':
            risks.append("Bearish Trend")
        
        # Support/Resistance risks
        sr_data = technical_data.get('support_resistance', {})
        distance_to_resistance = sr_data.get('distance_to_resistance', 10)
        if distance_to_resistance < 3:
            risks.append("Near Resistance Level")
        
        signals = technical_data.get('signals', [])
        sell_signals = len([s for s in signals if s.get('signal') == 'SELL'])
        if sell_signals >= 2:
            risks.append("Multiple Sell Signals")
        
        return risks[:4]  # Top 4 risks
    
    def _get_key_technical_indicators(self, technical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key technical indicators for display"""
        indicators = technical_data.get('indicators', {})
        
        key_indicators = {}
        
        # RSI
        rsi_data = indicators.get('rsi', {})
        if rsi_data:
            key_indicators['RSI'] = {
                'value': rsi_data.get('current', 50),
                'signal': rsi_data.get('signal', 'NEUTRAL')
            }
        
        # MACD
        macd_data = indicators.get('macd', {})
        if macd_data:
            key_indicators['MACD'] = {
                'crossover': macd_data.get('crossover', 'NEUTRAL'),
                'momentum': macd_data.get('momentum', 'NEUTRAL')
            }
        
        # Bollinger Bands
        bb_data = indicators.get('bollinger_bands', {})
        if bb_data:
            key_indicators['Bollinger_Bands'] = {
                'position': bb_data.get('position', 0.5),
                'signal': bb_data.get('signal', 'NEUTRAL')
            }
        
        return key_indicators
    
    def _get_investment_rating(self, score: float) -> str:
        """Convert score to investment rating (original method for compatibility)"""
        if score >= 85:
            return "BUY STRONG"
        elif score >= 75:
            return "BUY"
        elif score >= 65:
            return "HOLD +"
        elif score >= 55:
            return "HOLD"
        elif score >= 45:
            return "HOLD -"
        else:
            return "AVOID"
    
    def _generate_explanation(self, stock_data: Dict[str, Any], scores: Dict[str, float], total_score: float) -> str:
        """Generate human-readable explanation"""
        symbol = stock_data.get('symbol', 'N/A')
        sector = stock_data.get('sector', 'Unknown')
        price = stock_data.get('price', 0)
        
        explanation = f"{symbol} ({sector}) at ${price:.2f} "
        
        if total_score >= 75:
            explanation += "shows strong investment potential with "
        elif total_score >= 65:
            explanation += "presents a solid investment opportunity with "
        elif total_score >= 55:
            explanation += "offers moderate investment appeal with "
        else:
            explanation += "faces investment challenges with "
        
        # Highlight top factors
        top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        factors = []
        
        for factor, score in top_scores:
            if score >= 80:
                factor_name = factor.replace('_score', '').replace('_', ' ')
                factors.append(f"strong {factor_name}")
        
        if factors:
            explanation += ", ".join(factors) + "."
        else:
            explanation += "mixed fundamentals."
        
        return explanation
    
    def _assess_risk_level(self, stock_data: Dict[str, Any], scores: Dict[str, float]) -> str:
        """Assess overall risk level"""
        volatility_score = scores.get('volatility_score', 50)
        financial_health = scores.get('financial_health', 50)
        
        avg_risk_score = (volatility_score + financial_health) / 2
        
        if avg_risk_score >= 80:
            return "LOW"
        elif avg_risk_score >= 65:
            return "MODERATE"
        else:
            return "HIGH"
    
    def _recommend_investment_horizon(self, scores: Dict[str, float]) -> str:
        """Recommend investment time horizon"""
        momentum_score = scores.get('momentum_score', 50)
        value_score = scores.get('value_score', 50)
        
        if value_score >= 75 and momentum_score >= 70:
            return "LONG-TERM"  # Good value + momentum
        elif momentum_score >= 80:
            return "SHORT-TERM"  # Strong momentum
        else:
            return "MEDIUM-TERM"
    
    def _identify_key_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify top strengths"""
        strengths = []
        
        if scores.get('pe_score', 0) >= 80:
            strengths.append("Attractive Valuation")
        if scores.get('dividend_score', 0) >= 80:
            strengths.append("Strong Dividend")
        if scores.get('momentum_score', 0) >= 80:
            strengths.append("Positive Momentum")
        if scores.get('financial_health', 0) >= 80:
            strengths.append("Financial Stability")
        if scores.get('volatility_score', 0) >= 80:
            strengths.append("Low Risk")
        
        return strengths[:3]  # Top 3 strengths
    
    def _identify_key_risks(self, scores: Dict[str, float]) -> List[str]:
        """Identify main risks"""
        risks = []
        
        if scores.get('pe_score', 100) <= 40:
            risks.append("Valuation Concerns")
        if scores.get('volatility_score', 100) <= 40:
            risks.append("High Volatility")
        if scores.get('volume_score', 100) <= 40:
            risks.append("Low Liquidity")
        if scores.get('momentum_score', 100) <= 40:
            risks.append("Negative Momentum")
        if scores.get('financial_health', 100) <= 40:
            risks.append("Financial Risk")
        
        return risks[:3]  # Top 3 risks
    
    def _get_default_score(self, symbol: str) -> Dict[str, Any]:
        """Return default score for error cases"""
        return {
            'symbol': symbol,
            'total_score': 50.0,
            'rating': "HOLD",
            'individual_scores': {k.replace('_score', ''): 50.0 for k in self.weights.keys()},
            'explanation': f"Unable to calculate comprehensive score for {symbol}",
            'risk_level': "UNKNOWN",
            'investment_horizon': "UNKNOWN",
            'key_strengths': [],
            'key_risks': ["Insufficient Data"],
            'last_updated': datetime.utcnow().isoformat()
        }

# Global instance
investment_scorer = InvestmentScorer()
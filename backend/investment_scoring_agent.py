"""
Investment Scoring Agent - AI-Powered Investment Analysis
Uses Unusual Whales data to generate comprehensive investment scores with ML-enhanced insights.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
from unusual_whales_service import UnusualWhalesService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvestmentScoringAgent:
    """
    AI-powered investment scoring agent that combines multiple data sources
    from Unusual Whales to generate comprehensive investment recommendations.
    """
    
    def __init__(self):
        self.uw_service = UnusualWhalesService()
        
        # Scoring weights for different signal types
        self.signal_weights = {
            'options_flow': 0.25,        # Options sentiment from flow data
            'dark_pool': 0.20,           # Institutional activity
            'congressional': 0.15,       # Political insider information  
            'ai_strategies': 0.20,       # UW AI trading strategies
            'market_momentum': 0.10,     # General market indicators
            'risk_assessment': 0.10      # Risk-adjusted scoring
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.75,
            'medium': 0.50,
            'low': 0.25
        }
    
    async def generate_investment_score(self, symbol: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive investment score for a given symbol using UW data sources.
        
        Args:
            symbol: Stock ticker symbol
            user_context: Optional user portfolio/preferences for personalization
            
        Returns:
            Dict containing investment score, signals, and recommendations
        """
        try:
            logger.info(f"Generating investment score for {symbol}")
            
            # 1. Fetch all UW data sources concurrently
            uw_data = await self._fetch_uw_data(symbol)
            
            # 2. Analyze each signal component  
            signal_scores = await self._analyze_signal_components(uw_data, symbol)
            
            # 3. Calculate composite investment score
            composite_score = self._calculate_composite_score(signal_scores)
            
            # 4. Generate recommendation and confidence
            recommendation = self._generate_recommendation(composite_score, signal_scores)
            confidence = self._calculate_confidence_level(signal_scores)
            
            # 5. Extract key insights
            key_signals = self._extract_key_signals(uw_data, signal_scores)
            
            # 6. Risk assessment
            risk_analysis = self._assess_risk_factors(uw_data, signal_scores)
            
            return {
                'symbol': symbol,
                'investment_score': round(composite_score, 1),
                'recommendation': recommendation,
                'confidence_level': confidence,
                'key_signals': key_signals,
                'risk_analysis': risk_analysis,
                'signal_breakdown': signal_scores,
                'timestamp': datetime.now().isoformat(),
                'agent_version': '1.0',
                'data_sources': ['unusual_whales_options_flow', 'dark_pool', 'congressional_trades', 'ai_strategies']
            }
            
        except Exception as e:
            logger.error(f"Error generating investment score for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': f"Failed to generate investment score: {str(e)}",
                'investment_score': 50.0,  # Neutral score on error
                'recommendation': 'HOLD',
                'confidence_level': 'low',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fetch_uw_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch all relevant data from Unusual Whales API concurrently."""
        try:
            # Fetch all UW data sources in parallel for efficiency
            tasks = [
                self.uw_service.get_options_flow_alerts(
                    minimum_premium=200000,  # Focus on significant flows
                    limit=100
                ),
                self.uw_service.get_dark_pool_recent(
                    minimum_volume=100000,
                    minimum_dark_percentage=0.01,
                    limit=50
                ),
                self.uw_service.get_congressional_trades(
                    days_back=90,  # Longer lookback for congressional activity
                    minimum_amount=50000,
                    limit=100
                )
            ]
            
            options_flow, dark_pool, congressional = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter data for the specific symbol
            filtered_data = {
                'options_flow': self._filter_options_for_symbol(options_flow, symbol),
                'dark_pool': self._filter_dark_pool_for_symbol(dark_pool, symbol), 
                'congressional': self._filter_congressional_for_symbol(congressional, symbol),
                'strategies': []
            }
            
            logger.info(f"Fetched UW data for {symbol}: Options={len(filtered_data['options_flow'])}, "
                       f"DarkPool={len(filtered_data['dark_pool'])}, "
                       f"Congressional={len(filtered_data['congressional'])}, "
                       f"Strategies={len(filtered_data['strategies'])}")
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error fetching UW data for {symbol}: {str(e)}")
            return {'options_flow': [], 'dark_pool': [], 'congressional': [], 'strategies': []}
    
    def _filter_options_for_symbol(self, options_data: List[Dict], symbol: str) -> List[Dict]:
        """Filter options flow data for specific symbol."""
        if isinstance(options_data, Exception) or not options_data:
            return []
        
        return [opt for opt in options_data if opt.get('symbol', '').upper() == symbol.upper()]
    
    def _filter_dark_pool_for_symbol(self, dark_pool_data: List[Dict], symbol: str) -> List[Dict]:
        """Filter dark pool data for specific symbol."""
        if isinstance(dark_pool_data, Exception) or not dark_pool_data:
            return []
            
        return [dp for dp in dark_pool_data if dp.get('ticker', '').upper() == symbol.upper()]
    
    def _filter_congressional_for_symbol(self, congressional_data: List[Dict], symbol: str) -> List[Dict]:
        """Filter congressional trades for specific symbol."""
        if isinstance(congressional_data, Exception) or not congressional_data:
            return []
            
        return [cong for cong in congressional_data if cong.get('ticker', '').upper() == symbol.upper()]
    
    def _filter_strategies_for_symbol(self, strategies_data: List[Dict], symbol: str) -> List[Dict]:
        """Filter trading strategies for specific symbol.""" 
        if isinstance(strategies_data, Exception) or not strategies_data:
            return []
            
        return [strat for strat in strategies_data if symbol.upper() in strat.get('ticker', '').upper()]
    
    async def _analyze_signal_components(self, uw_data: Dict[str, Any], symbol: str) -> Dict[str, float]:
        """Analyze each signal component and return normalized scores (0-100)."""
        
        signal_scores = {}
        
        # 1. Options Flow Analysis
        signal_scores['options_flow'] = self._analyze_options_sentiment(uw_data['options_flow'])
        
        # 2. Dark Pool Analysis  
        signal_scores['dark_pool'] = self._analyze_dark_pool_sentiment(uw_data['dark_pool'])
        
        # 3. Congressional Activity Analysis
        signal_scores['congressional'] = self._analyze_congressional_sentiment(uw_data['congressional'])
        
        # 4. AI Strategies Analysis
        signal_scores['ai_strategies'] = self._analyze_ai_strategies_confidence(uw_data['strategies'])
        
        # 5. Market Momentum (derived from options flow patterns)
        signal_scores['market_momentum'] = self._analyze_market_momentum(uw_data['options_flow'])
        
        # 6. Risk Assessment
        signal_scores['risk_assessment'] = self._calculate_risk_score(uw_data)
        
        return signal_scores
    
    def _analyze_options_sentiment(self, options_data: List[Dict]) -> float:
        """Analyze options flow to determine bullish/bearish sentiment."""
        if not options_data:
            return 50.0  # Neutral score
        
        bullish_count = sum(1 for opt in options_data if opt.get('sentiment', '').lower() == 'bullish')
        bearish_count = sum(1 for opt in options_data if opt.get('sentiment', '').lower() == 'bearish')
        total_premium = sum(opt.get('premium', 0) for opt in options_data)
        
        if bullish_count + bearish_count == 0:
            return 50.0
        
        # Weight by premium volume - larger premiums have more significance
        bullish_premium = sum(opt.get('premium', 0) for opt in options_data 
                            if opt.get('sentiment', '').lower() == 'bullish')
        
        # Sentiment ratio weighted by premium
        sentiment_ratio = bullish_count / (bullish_count + bearish_count)
        premium_ratio = bullish_premium / max(total_premium, 1) if total_premium > 0 else 0.5
        
        # Combine count and premium weighting
        combined_sentiment = (sentiment_ratio * 0.4 + premium_ratio * 0.6)
        
        # Scale to 0-100 with premium volume boost
        base_score = combined_sentiment * 100
        
        # Boost for high premium volume (institutional interest)
        if total_premium > 5000000:  # $5M+ total premium
            base_score = min(100, base_score * 1.1)
        
        return round(base_score, 1)
    
    def _analyze_dark_pool_sentiment(self, dark_pool_data: List[Dict]) -> float:
        """Analyze dark pool activity for institutional sentiment."""
        if not dark_pool_data:
            return 50.0  # Neutral
        
        # High dark pool percentage suggests institutional accumulation
        avg_dark_percentage = statistics.mean([dp.get('dark_percentage', 0) for dp in dark_pool_data])
        total_dark_volume = sum(dp.get('dark_volume', 0) for dp in dark_pool_data)
        
        # Score based on dark pool percentage (higher = more bullish institutional activity)
        percentage_score = min(100, avg_dark_percentage * 1.5)  # Scale up since 60%+ is high
        
        # Volume significance boost
        volume_multiplier = 1.0
        if total_dark_volume > 1000000:  # 1M+ shares
            volume_multiplier = 1.2
        elif total_dark_volume > 5000000:  # 5M+ shares  
            volume_multiplier = 1.4
        
        return round(min(100, percentage_score * volume_multiplier), 1)
    
    def _analyze_congressional_sentiment(self, congressional_data: List[Dict]) -> float:
        """Analyze congressional trading activity for insider sentiment.""" 
        if not congressional_data:
            return 50.0  # Neutral
        
        purchases = [trade for trade in congressional_data if 'purchase' in trade.get('transaction_type', '').lower()]
        sales = [trade for trade in congressional_data if 'sale' in trade.get('transaction_type', '').lower()]
        
        if not purchases and not sales:
            return 50.0
        
        # Weight by transaction amounts
        purchase_amount = sum(trade.get('transaction_amount', 0) for trade in purchases)
        sale_amount = sum(trade.get('transaction_amount', 0) for trade in sales)
        total_amount = purchase_amount + sale_amount
        
        if total_amount == 0:
            return 50.0
        
        # Calculate purchase ratio
        purchase_ratio = purchase_amount / total_amount
        
        # Recent activity boost (last 30 days gets higher weight)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_trades = [
            trade for trade in congressional_data 
            if self._parse_date(trade.get('transaction_date', '')) > recent_cutoff
        ]
        
        recency_boost = 1.0
        if len(recent_trades) > 0:
            recency_boost = 1.3
        
        # Scale to 0-100
        base_score = purchase_ratio * 100 * recency_boost
        
        return round(min(100, base_score), 1)
    
    def _analyze_ai_strategies_confidence(self, strategies_data: List[Dict]) -> float:
        """Analyze AI-generated trading strategies confidence."""
        if not strategies_data:
            return 50.0  # Neutral when no strategies
        
        # Extract confidence levels from strategies
        confidences = []
        bullish_strategies = 0
        
        for strategy in strategies_data:
            confidence = strategy.get('confidence', 0.5)
            confidences.append(confidence)
            
            # Check if strategy is bullish (calls, long positions, etc.)
            strategy_type = strategy.get('strategy_name', '').lower()
            if any(bullish_term in strategy_type for bullish_term in ['long', 'call', 'bull']):
                bullish_strategies += 1
        
        if not confidences:
            return 50.0
        
        # Average confidence scaled to 0-100
        avg_confidence = statistics.mean(confidences)
        confidence_score = avg_confidence * 100
        
        # Boost for predominantly bullish strategies
        if len(strategies_data) > 0:
            bullish_ratio = bullish_strategies / len(strategies_data)
            if bullish_ratio > 0.6:  # 60%+ bullish strategies
                confidence_score *= 1.2
        
        return round(min(100, confidence_score), 1)
    
    def _analyze_market_momentum(self, options_data: List[Dict]) -> float:
        """Analyze market momentum from options flow patterns.""" 
        if not options_data:
            return 50.0
        
        # Look for momentum indicators in options data
        short_term_dte = [opt for opt in options_data if opt.get('dte', 365) <= 7]  # Weekly options
        high_volume = [opt for opt in options_data if opt.get('volume', 0) > 1000]
        
        momentum_score = 50.0  # Base neutral
        
        # Short-term options activity suggests momentum
        if len(short_term_dte) > len(options_data) * 0.3:  # 30%+ short-term
            momentum_score += 15
        
        # High volume suggests strong momentum
        if len(high_volume) > len(options_data) * 0.4:  # 40%+ high volume
            momentum_score += 15
        
        # Opening vs closing positions (opening suggests new momentum)
        opening_positions = sum(1 for opt in options_data if opt.get('is_opener', False))
        if opening_positions > len(options_data) * 0.5:  # 50%+ opening
            momentum_score += 10
        
        return round(min(100, momentum_score), 1)
    
    def _calculate_risk_score(self, uw_data: Dict[str, Any]) -> float:
        """Calculate risk-adjusted score (higher = lower risk)."""
        risk_factors = 0
        total_checks = 0
        
        # Check options data for risk indicators
        options_data = uw_data['options_flow']
        if options_data:
            total_checks += 3
            
            # High volume/OI ratio suggests higher risk
            high_vol_oi = sum(1 for opt in options_data if opt.get('volume_oi_ratio', 0) > 3)
            if high_vol_oi < len(options_data) * 0.3:  # Less than 30% high vol/OI is good
                risk_factors += 1
            
            # Diverse expiration dates reduce risk
            unique_dtes = len(set(opt.get('dte', 0) for opt in options_data))
            if unique_dtes > 3:  # Good diversification
                risk_factors += 1
            
            # Mix of call/put activity reduces directional risk
            calls = sum(1 for opt in options_data if 'call' in opt.get('option_type', '').lower())
            puts = sum(1 for opt in options_data if 'put' in opt.get('option_type', '').lower())
            if calls > 0 and puts > 0:  # Both directions represented
                risk_factors += 1
        
        # Dark pool consistency reduces risk
        dark_pool_data = uw_data['dark_pool']
        if dark_pool_data:
            total_checks += 1
            consistent_percentages = [dp.get('dark_percentage', 0) for dp in dark_pool_data]
            if consistent_percentages and max(consistent_percentages) - min(consistent_percentages) < 20:
                risk_factors += 1  # Consistent dark pool activity
        
        if total_checks == 0:
            return 50.0  # Neutral risk score
        
        risk_score = (risk_factors / total_checks) * 100
        return round(risk_score, 1)
    
    def _calculate_composite_score(self, signal_scores: Dict[str, float]) -> float:
        """Calculate weighted composite investment score."""
        composite = 0.0
        
        for signal_type, score in signal_scores.items():
            weight = self.signal_weights.get(signal_type, 0.0)
            composite += score * weight
        
        return round(min(100, max(0, composite)), 1)
    
    def _generate_recommendation(self, composite_score: float, signal_scores: Dict[str, float]) -> str:
        """Generate investment recommendation based on composite score."""
        if composite_score >= 75:
            return "STRONG BUY"
        elif composite_score >= 65:
            return "BUY"
        elif composite_score >= 55:
            return "HOLD+"
        elif composite_score >= 45:
            return "HOLD"
        elif composite_score >= 35:
            return "HOLD-"
        elif composite_score >= 25:
            return "SELL"
        else:
            return "STRONG SELL"
    
    def _calculate_confidence_level(self, signal_scores: Dict[str, float]) -> str:
        """Calculate confidence level based on signal consistency."""
        scores = list(signal_scores.values())
        if not scores:
            return 'low'
        
        # Check consistency of signals
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        avg_score = statistics.mean(scores)
        
        # High confidence: consistent signals with good average
        if score_std < 15 and (avg_score > 65 or avg_score < 35):
            return 'high'
        elif score_std < 25:
            return 'medium'
        else:
            return 'low'
    
    def _extract_key_signals(self, uw_data: Dict[str, Any], signal_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Extract the most significant signals for display."""
        key_signals = []
        
        # Find top 3 signals by score
        sorted_signals = sorted(signal_scores.items(), key=lambda x: abs(x[1] - 50), reverse=True)
        
        for signal_type, score in sorted_signals[:3]:
            signal_info = {
                'type': signal_type,
                'score': score,
                'strength': 'strong' if abs(score - 50) > 20 else 'moderate' if abs(score - 50) > 10 else 'weak',
                'direction': 'bullish' if score > 50 else 'bearish' if score < 50 else 'neutral'
            }
            
            # Add specific details based on signal type
            if signal_type == 'options_flow':
                options_count = len(uw_data['options_flow'])
                signal_info['details'] = f"{options_count} options flow alerts analyzed"
            elif signal_type == 'dark_pool':
                dp_count = len(uw_data['dark_pool'])
                signal_info['details'] = f"{dp_count} dark pool trades analyzed"
            elif signal_type == 'congressional':
                cong_count = len(uw_data['congressional'])
                signal_info['details'] = f"{cong_count} congressional trades analyzed"
            elif signal_type == 'ai_strategies':
                strat_count = len(uw_data['strategies'])
                signal_info['details'] = f"{strat_count} AI strategies analyzed"
            
            key_signals.append(signal_info)
        
        return key_signals
    
    def _assess_risk_factors(self, uw_data: Dict[str, Any], signal_scores: Dict[str, float]) -> Dict[str, Any]:
        """Assess various risk factors."""
        risk_factors = []
        overall_risk = 'medium'  # Default
        
        # High volatility indicators from options
        options_data = uw_data['options_flow']
        if options_data:
            short_dte_count = sum(1 for opt in options_data if opt.get('dte', 365) <= 3)
            if short_dte_count > len(options_data) * 0.4:
                risk_factors.append("High short-term options activity suggests volatility")
        
        # Signal inconsistency
        scores = list(signal_scores.values())
        if len(scores) > 1:
            score_range = max(scores) - min(scores)
            if score_range > 40:
                risk_factors.append("Mixed signals across data sources")
        
        # Determine overall risk level
        risk_score = signal_scores.get('risk_assessment', 50)
        if risk_score < 30:
            overall_risk = 'high'
        elif risk_score > 70:
            overall_risk = 'low'
        
        return {
            'overall_risk': overall_risk,
            'risk_factors': risk_factors,
            'risk_score': risk_score
        }
    
    def _parse_date(self, date_string: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_string, '%Y-%m-%d')
        except:
            return datetime.now() - timedelta(days=365)  # Default to old date
    
    # Additional utility methods for future enhancements
    async def get_batch_scores(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Generate investment scores for multiple symbols efficiently."""
        tasks = [self.generate_investment_score(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result if not isinstance(result, Exception) else {'error': str(result)}
            for symbol, result in zip(symbols, results)
        }
    
    def get_scoring_explanation(self) -> Dict[str, str]:
        """Return explanation of scoring methodology for transparency."""
        return {
            'options_flow': 'Analyzes options trading sentiment and premium volume to gauge market sentiment',
            'dark_pool': 'Evaluates institutional activity through dark pool trading percentages and volumes', 
            'congressional': 'Tracks congressional insider trading activity and timing',
            'ai_strategies': 'Incorporates AI-generated trading strategy confidence and directional bias',
            'market_momentum': 'Assesses short-term momentum indicators from options flow patterns',
            'risk_assessment': 'Evaluates various risk factors including volatility and signal consistency',
            'composite_methodology': 'Weighted average of all signals with risk adjustment and confidence scoring'
        }
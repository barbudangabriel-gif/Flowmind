# FLOWMIND CORE ENGINE - AI AGENTS & ML ARCHITECTURE

**Design Date:** November 1, 2025  
**Target:** Professional Trading Desk with Live Monitoring & AI Decision Support

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FLOWMIND CORE ENGINE                            │
│                    (Professional Trading Desk System)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
            │  DATA LAYER  │ │ AI AGENTS │ │ LIVE MONITOR│
            │   (Redis +   │ │  (Brain)  │ │  (WebSocket)│
            │   TimeSeries)│ └─────┬─────┘ └──────┬──────┘
            └──────┬───────┘       │              │
                   │               │              │
        ┌──────────┴───────────────┴──────────────┴──────────┐
        │                                                     │
    ┌───▼────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────▼───┐
    │Market  │  │Signal  │  │Risk    │  │Execution│  │Frontend  │
    │Data    │  │Engine  │  │Manager │  │Engine   │  │Dashboard │
    │Ingestion│  │(ML)    │  │(Rules) │  │(Broker) │  │(React)   │
    └────────┘  └────────┘  └────────┘  └────────┘  └──────────┘
```

---

## 📊 1. DATA LAYER (Foundation)

### Architecture: Redis + TimeSeries + Message Queue

```python
# backend/core/data_layer.py

class DataLayer:
    """
    Centralized data management for CORE ENGINE
    - Real-time market data (Redis Streams)
    - Historical data (Redis TimeSeries)
    - Agent state (Redis Hash)
    - Message queue (Redis Pub/Sub)
    """
    
    # Redis Keys Structure:
    # market:ticker:TSLA:price     → Current price (TimeSeries)
    # market:ticker:TSLA:greeks    → Current Greeks (Hash)
    # market:ticker:TSLA:flow      → Options flow (Stream)
    # 
    # agent:scanner:state          → Agent state (Hash)
    # agent:scanner:signals        → Signal queue (List)
    # 
    # live:positions               → Real-time positions (Sorted Set)
    # live:pnl:realtime            → Tick-by-tick P&L (TimeSeries)
    # live:alerts                  → Alert feed (Stream)
```

**Key Technologies:**
- **Redis Streams:** Real-time event streaming (market data, signals)
- **Redis TimeSeries:** OHLCV, Greeks, P&L tracking (retention: 90 days)
- **Redis Pub/Sub:** Agent communication, WebSocket broadcast
- **Redis Hash:** Agent state, portfolio snapshot
- **Redis Sorted Set:** Priority queues, ranked signals

---

## 🤖 2. AI AGENTS (Brain) - Multi-Agent System

### Agent Types & Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI AGENT HIERARCHY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MASTER ORCHESTRATOR (GPT-4o / Claude 3.5 Sonnet)      │  │
│  │  • Coordinates all agents                               │  │
│  │  • Makes final trade decisions                          │  │
│  │  • Risk override authority                              │  │
│  └──────────────────┬──────────────────────────────────────┘  │
│                     │                                          │
│     ┌───────────────┼───────────────┐                         │
│     │               │               │                         │
│  ┌──▼────┐     ┌───▼────┐     ┌───▼────┐                    │
│  │SCANNER│     │ANALYST │     │EXECUTOR│                     │
│  │AGENTS │     │AGENTS  │     │AGENTS  │                     │
│  └───────┘     └────────┘     └────────┘                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 2.1 SCANNER AGENTS (Data Collection & Pattern Detection)

**Purpose:** Monitor markets, detect opportunities, generate signals

```python
# backend/agents/scanners/

class OptionsFlowScanner:
    """
    Monitors unusual options activity
    - Dark pool sweeps (>$1M premium)
    - Unusual volume (>10x avg)
    - Smart money indicators (bid/ask ratio)
    """
    interval: 30s  # Scan every 30 seconds
    priority: HIGH
    
    def scan():
        signals = uw_api.flow_summary(minPremium=1_000_000)
        for trade in signals:
            if is_unusual(trade):
                emit_signal("options_flow", trade)

class GEXScanner:
    """
    Gamma Exposure levels scanner
    - Identify pin zones (max GEX)
    - Detect squeeze potential (negative GEX)
    - Call wall / Put wall identification
    """
    interval: 5m
    priority: MEDIUM
    
    def scan():
        for ticker in watchlist:
            gex = calculate_gex_levels(ticker)
            if abs(gex.call_wall - current_price) < 2%:
                emit_signal("gex_pin", ticker, gex)

class EarningsScanner:
    """
    Pre/post earnings opportunities
    - IV crush plays (sell premium before earnings)
    - Strangle setups (high IV rank)
    - Historical earnings move analysis
    """
    interval: 1h
    priority: LOW
    
    def scan():
        earnings_today = uw_api.earnings_today()
        for company in earnings_today:
            if company.iv_rank > 70:
                emit_signal("earnings_play", company)

class TechnicalScanner:
    """
    TA pattern recognition
    - Support/Resistance breaks
    - Moving average crossovers
    - RSI divergence
    - Volume anomalies
    """
    interval: 1m
    priority: HIGH
    
    def scan():
        for ticker in universe:
            signals = detect_patterns(ticker)
            if signals.strength > 0.8:
                emit_signal("technical", ticker, signals)

class SentimentScanner:
    """
    News & social sentiment
    - Unusual Whales insider trades
    - Dark pool activity
    - Congress trades
    - Twitter sentiment (if available)
    """
    interval: 5m
    priority: MEDIUM
```

### 2.2 ANALYST AGENTS (Signal Processing & Decision Making)

**Purpose:** Analyze signals, validate trades, generate recommendations

```python
# backend/agents/analysts/

class StrategyAnalyst:
    """
    Matches signals to optimal strategies
    - Input: Raw signal from scanner
    - Output: Concrete strategy recommendation
    - Uses: Options risk engine, historical backtest
    """
    
    async def analyze(signal: Signal):
        # 1. Fetch market data
        current_price = await get_spot_price(signal.ticker)
        iv_rank = await get_iv_rank(signal.ticker)
        
        # 2. Strategy selection based on signal type
        if signal.type == "options_flow" and signal.direction == "bullish":
            # Suggest call spread or long call
            strategy = self.build_call_spread(signal)
        elif signal.type == "gex_pin":
            # Suggest iron condor around pin zone
            strategy = self.build_iron_condor(signal)
        
        # 3. Validate with options risk engine
        validation = await risk_engine.validate(strategy)
        
        # 4. Backtest similar setups (5-year)
        backtest = await backtest_engine.run(strategy)
        
        return StrategyRecommendation(
            strategy=strategy,
            validation=validation,
            backtest=backtest,
            confidence=0.75,
            expected_return=0.15,
            max_loss=-500,
        )

class RiskAnalyst:
    """
    Portfolio-level risk assessment
    - Greeks exposure (Delta, Gamma, Vega)
    - Correlation analysis
    - Concentration risk
    - VaR (Value at Risk) calculation
    """
    
    async def assess_portfolio():
        positions = await get_all_positions()
        
        # Calculate portfolio Greeks
        total_delta = sum(pos.delta for pos in positions)
        total_vega = sum(pos.vega for pos in positions)
        
        # Concentration risk
        ticker_exposure = defaultdict(float)
        for pos in positions:
            ticker_exposure[pos.ticker] += pos.value
        
        max_concentration = max(ticker_exposure.values()) / portfolio_value
        
        # VaR calculation (Monte Carlo)
        var_95 = self.calculate_var(positions, confidence=0.95)
        
        return RiskReport(
            total_delta=total_delta,
            total_vega=total_vega,
            concentration=max_concentration,
            var_95=var_95,
            alerts=self.generate_alerts(),
        )

class ProfitOptimizer:
    """
    Exit strategy optimization
    - When to take profits (50%, 75%, 100% profit targets)
    - When to cut losses (stop loss levels)
    - Rolling strategies (extend duration)
    """
    
    async def optimize_exit(position: Position):
        # Analyze current P&L
        current_pnl_pct = position.unrealized_pnl / position.cost_basis
        
        # Check historical success rates
        if current_pnl_pct > 0.50:
            # 50% profit target hit
            if self.should_take_profit_50(position):
                return ExitRecommendation("CLOSE", reason="50% target")
        
        # Greeks decay analysis
        if position.theta < -50 and position.dte < 7:
            return ExitRecommendation("ROLL", reason="Theta decay high")
        
        return ExitRecommendation("HOLD", reason="Let it run")

class HedgeAnalyst:
    """
    Portfolio hedging recommendations
    - When to hedge (high delta, low VIX)
    - What to hedge with (SPY puts, VIX calls)
    - How much to allocate (10% hedge budget)
    """
    
    async def recommend_hedge():
        portfolio = await get_portfolio_snapshot()
        
        # Check if hedging needed
        if portfolio.delta > 200 and vix < 15:
            # Bullish portfolio, low volatility → hedge tail risk
            hedge = HedgeRecommendation(
                type="SPY_PUT_SPREAD",
                strikes=(440, 435),
                expiry=30_days,
                cost=200,
                protection="Protects against 5% drop",
            )
            return hedge
        
        return None
```

### 2.3 EXECUTOR AGENTS (Trade Execution & Management)

**Purpose:** Execute approved trades, manage orders, handle fills

```python
# backend/agents/executors/

class OrderExecutor:
    """
    Smart order execution
    - Limit orders with patience (don't chase)
    - Split orders for better fills
    - Monitor slippage
    """
    
    async def execute_strategy(strategy: Strategy, urgency: str):
        if urgency == "HIGH":
            # Market order for immediate fill
            await broker.market_order(strategy.legs)
        else:
            # Limit order with mid-price + small offset
            mid_price = (bid + ask) / 2
            limit_price = mid_price + 0.05
            
            order = await broker.limit_order(strategy.legs, limit_price)
            
            # Monitor for 5 minutes, then adjust
            await asyncio.sleep(300)
            if not order.filled:
                await self.adjust_limit(order, new_limit=mid_price + 0.10)

class PositionManager:
    """
    Active position management
    - Monitor stop losses
    - Adjust profit targets
    - Roll positions near expiration
    """
    
    async def monitor_positions():
        while True:
            positions = await get_open_positions()
            
            for pos in positions:
                # Check stop loss
                if pos.unrealized_pnl_pct < -0.50:  # -50% loss
                    await self.close_position(pos, reason="STOP_LOSS")
                
                # Check profit target
                if pos.unrealized_pnl_pct > 0.50:  # 50% profit
                    await self.take_profit(pos, percent=0.50)
                
                # Check expiration
                if pos.dte < 7:
                    await self.roll_position(pos)
            
            await asyncio.sleep(60)  # Check every minute
```

### 2.4 MASTER ORCHESTRATOR (Decision Maker)

**Purpose:** Coordinate agents, make final decisions, override when needed

```python
# backend/agents/orchestrator.py

class MasterOrchestrator:
    """
    Central intelligence coordinating all agents
    - LLM: GPT-4o or Claude 3.5 Sonnet
    - Context: Full portfolio state, recent signals, market conditions
    - Authority: Final approval on all trades
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.scanners = [OptionsFlowScanner(), GEXScanner(), ...]
        self.analysts = [StrategyAnalyst(), RiskAnalyst(), ...]
        self.executors = [OrderExecutor(), PositionManager()]
    
    async def orchestrate_cycle(self):
        """
        Main decision cycle (runs every 30 seconds)
        """
        # 1. Gather signals from all scanners
        signals = []
        for scanner in self.scanners:
            new_signals = await scanner.scan()
            signals.extend(new_signals)
        
        # 2. Prioritize signals (by confidence, urgency, potential)
        ranked_signals = self.rank_signals(signals)
        
        # 3. For top signals, get analyst recommendations
        recommendations = []
        for signal in ranked_signals[:5]:  # Top 5 only
            rec = await self.strategy_analyst.analyze(signal)
            if rec.validation.passed:
                recommendations.append(rec)
        
        # 4. Portfolio risk check
        risk_report = await self.risk_analyst.assess_portfolio()
        
        # 5. LLM decision (with full context)
        context = {
            "signals": ranked_signals,
            "recommendations": recommendations,
            "risk_report": risk_report,
            "portfolio": await get_portfolio_snapshot(),
            "market_conditions": await get_market_conditions(),
        }
        
        decision = await self.llm_decide(context)
        
        # 6. Execute approved trades
        if decision.action == "EXECUTE":
            await self.executor.execute_strategy(
                decision.strategy,
                urgency=decision.urgency,
            )
        
        # 7. Log everything
        await self.log_cycle(context, decision)
    
    async def llm_decide(self, context):
        """
        LLM makes final decision with full reasoning
        """
        prompt = f"""
You are the Master Orchestrator for FlowMind Trading System.

PORTFOLIO STATE:
- Cash: ${context['portfolio'].cash}
- Positions: {len(context['portfolio'].positions)} open
- Total Delta: {context['risk_report'].total_delta}
- Total Vega: {context['risk_report'].total_vega}
- Day P&L: ${context['portfolio'].day_pnl}

TOP SIGNALS ({len(context['signals'])}):
{self.format_signals(context['signals'][:3])}

ANALYST RECOMMENDATIONS ({len(context['recommendations'])}):
{self.format_recommendations(context['recommendations'])}

RISK ASSESSMENT:
- Portfolio VaR (95%): ${context['risk_report'].var_95}
- Max concentration: {context['risk_report'].concentration:.1%}
- Risk alerts: {context['risk_report'].alerts}

MARKET CONDITIONS:
- VIX: {context['market_conditions'].vix}
- SPY trend: {context['market_conditions'].spy_trend}
- Market regime: {context['market_conditions'].regime}

TASK:
1. Analyze the signals and recommendations
2. Consider portfolio risk and exposure
3. Decide: EXECUTE top recommendation, WAIT for better setup, or HEDGE portfolio
4. Provide clear reasoning

Respond in JSON:
{{
  "action": "EXECUTE" | "WAIT" | "HEDGE",
  "strategy": {{ ... }},
  "reasoning": "...",
  "confidence": 0.0-1.0,
  "urgency": "LOW" | "MEDIUM" | "HIGH"
}}
"""
        
        response = await self.llm.ainvoke(prompt)
        return self.parse_llm_response(response)
```

---

## 📡 3. LIVE MONITORING SYSTEM (WebSocket Dashboard)

### Real-Time Trade Desk Interface

```javascript
// frontend/src/pages/TradeDeskLive.jsx

const TradeDeskLive = () => {
  // WebSocket connections
  const { signals } = useWebSocket('/ws/signals');
  const { portfolio } = useWebSocket('/ws/portfolio');
  const { agents } = useWebSocket('/ws/agents');
  
  return (
    <div className="grid grid-cols-12 gap-4 h-screen bg-slate-900 p-4">
      
      {/* Left Column: Agent Status */}
      <div className="col-span-3 space-y-4">
        <AgentMonitor agents={agents} />
        <SignalFeed signals={signals} />
      </div>
      
      {/* Middle Column: Portfolio & Positions */}
      <div className="col-span-6 space-y-4">
        <PortfolioSummary portfolio={portfolio} />
        <LivePositionsGrid positions={portfolio.positions} />
        <RecentTradesLog />
      </div>
      
      {/* Right Column: Risk & Analytics */}
      <div className="col-span-3 space-y-4">
        <GreeksMonitor greeks={portfolio.greeks} />
        <RiskMeter risk={portfolio.risk} />
        <PerformanceChart data={portfolio.pnl_history} />
      </div>
      
    </div>
  );
};
```

### Live Components Breakdown:

**1. Agent Monitor:**
```jsx
<AgentMonitor>
  ┌─────────────────────────────┐
  │ 🤖 AGENTS STATUS            │
  ├─────────────────────────────┤
  │ 🟢 Orchestrator    ACTIVE   │
  │ 🟢 Flow Scanner    ACTIVE   │
  │ 🟡 GEX Scanner     IDLE     │
  │ 🟢 Strategy Analyst ACTIVE  │
  │ 🔴 Executor        PAUSED   │
  │                             │
  │ Last Cycle: 23:45:12        │
  │ Next Cycle: 23:45:42 (30s)  │
  └─────────────────────────────┘
```

**2. Signal Feed (Live Stream):**
```jsx
<SignalFeed>
  ┌─────────────────────────────┐
  │ 📊 LIVE SIGNALS             │
  ├─────────────────────────────┤
  │ 🔥 23:45:10                 │
  │ TSLA - Options Flow         │
  │ $1.2M call sweep at $250    │
  │ Confidence: 85%             │
  ├─────────────────────────────┤
  │ ⚡ 23:44:55                 │
  │ SPY - GEX Pin Zone          │
  │ Call wall at $470           │
  │ Confidence: 72%             │
  └─────────────────────────────┘
```

**3. Portfolio Summary (Real-time):**
```jsx
<PortfolioSummary>
  ┌───────────────────────────────────────┐
  │ 💼 PORTFOLIO                          │
  ├───────────────────────────────────────┤
  │ Cash: $8,450.23    Day P&L: +$234.50 │
  │ Equity: $12,340    Week: +$1,240.00  │
  │ Total: $20,790     YTD: +$4,567.89   │
  │                                       │
  │ Positions: 7 open  Greeks:           │
  │ • 3 Bullish        Δ: +156.4         │
  │ • 2 Neutral        Γ: +12.3          │
  │ • 2 Hedges         θ: -$45.2/day     │
  └───────────────────────────────────────┘
```

**4. Live Positions Grid:**
```jsx
<LivePositionsGrid>
  Symbol | Strategy      | DTE | P&L    | Delta | Actions
  ───────┼───────────────┼─────┼────────┼───────┼─────────
  TSLA   | Call Spread   | 14  | +$125  | +0.45 | [Close]
  SPY    | Iron Condor   | 30  | +$80   |  0.00 | [Roll]
  AAPL   | Long Call     | 45  | -$50   | +0.62 | [Hold]
  VIX    | Call (Hedge)  | 21  | -$20   | +0.28 | [Hold]
```

---

## 🧠 4. MACHINE LEARNING MODELS

### ML Pipeline Architecture

```python
# backend/ml/

# 4.1 Signal Confidence Scoring
class SignalConfidenceModel:
    """
    RandomForest classifier
    - Input: Signal features (volume, IV, price action, etc.)
    - Output: Confidence score (0-1) + feature importance
    - Trained on: Historical signals + outcomes (win/loss)
    """
    features = [
        'unusual_volume_ratio',
        'iv_rank',
        'price_vs_moving_avg',
        'options_flow_direction',
        'dark_pool_sentiment',
        'rsi',
        'macd_cross',
    ]

# 4.2 Win Rate Prediction
class WinRatePredictorModel:
    """
    Gradient Boosting (XGBoost)
    - Input: Strategy + market conditions
    - Output: Expected win rate (%)
    - Trained on: 5 years of options trades
    """

# 4.3 Profit Target Optimizer
class ProfitTargetModel:
    """
    Neural Network (PyTorch)
    - Input: Position Greeks, DTE, current P&L
    - Output: Optimal exit time (hold vs take profit)
    - Trained on: Historical position outcomes
    """

# 4.4 Volatility Regime Detection
class VolatilityRegimeModel:
    """
    Hidden Markov Model
    - Input: VIX history, market returns
    - Output: Current regime (LOW/MEDIUM/HIGH vol)
    - Used for: Strategy selection (credit vs debit)
    """
```

---

## 🔄 5. SYSTEM WORKFLOW (Complete Cycle)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLOWMIND CORE ENGINE CYCLE                   │
│                        (Every 30 seconds)                       │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: DATA INGESTION (0-5s)
├─ Fetch market data (TradeStation, Unusual Whales)
├─ Update Redis TimeSeries (prices, Greeks, flow)
└─ Broadcast to WebSocket clients

PHASE 2: SIGNAL GENERATION (5-15s)
├─ Scanner agents run in parallel
├─ Detect patterns, anomalies, opportunities
├─ Emit signals to queue (Redis Stream)
└─ ML model scores confidence

PHASE 3: ANALYSIS & VALIDATION (15-25s)
├─ Strategy Analyst processes top signals
├─ Risk Analyst checks portfolio exposure
├─ Options Risk Engine validates trades
├─ Backtest engine runs historical simulation
└─ Generate recommendations

PHASE 4: DECISION MAKING (25-28s)
├─ Master Orchestrator (LLM) evaluates
│  • All signals + recommendations
│  • Portfolio risk report
│  • Market conditions
├─ LLM decides: EXECUTE, WAIT, or HEDGE
└─ Log decision + reasoning

PHASE 5: EXECUTION (28-30s)
├─ If EXECUTE: OrderExecutor sends to broker
├─ If WAIT: Add to watchlist
├─ If HEDGE: HedgeAnalyst builds protection
└─ Update portfolio state

PHASE 6: MONITORING (Continuous)
├─ PositionManager monitors open trades
├─ Stop loss / Profit target checks
├─ Auto-roll near expiration
└─ WebSocket updates to frontend

CYCLE COMPLETE → Repeat
```

---

## 📁 FILE STRUCTURE

```
backend/
├── core/
│   ├── data_layer.py          # Redis management, TimeSeries
│   ├── message_queue.py       # Pub/Sub, Streams
│   └── websocket_manager.py   # WebSocket broadcast
│
├── agents/
│   ├── orchestrator.py        # Master AI (LLM)
│   ├── scanners/
│   │   ├── options_flow_scanner.py
│   │   ├── gex_scanner.py
│   │   ├── earnings_scanner.py
│   │   ├── technical_scanner.py
│   │   └── sentiment_scanner.py
│   ├── analysts/
│   │   ├── strategy_analyst.py
│   │   ├── risk_analyst.py
│   │   ├── profit_optimizer.py
│   │   └── hedge_analyst.py
│   └── executors/
│       ├── order_executor.py
│       └── position_manager.py
│
├── ml/
│   ├── signal_confidence_model.py
│   ├── win_rate_predictor.py
│   ├── profit_target_model.py
│   ├── volatility_regime_model.py
│   └── training/
│       ├── train_signal_confidence.py
│       └── backtest_validation.py
│
├── options_risk_engine.py     # ✅ Already built
├── hedge_module.py
├── super_scoring_engine.py
└── algo_attachment.py

frontend/
├── pages/
│   ├── TradeDeskLive.jsx      # Main dashboard
│   ├── AgentMonitor.jsx
│   └── SignalFeed.jsx
└── components/
    ├── PortfolioSummary.jsx
    ├── LivePositionsGrid.jsx
    ├── GreeksMonitor.jsx
    └── RiskMeter.jsx
```

---

## 🚀 IMPLEMENTATION PRIORITY

**PHASE 1: Foundation (Week 1-2)**
1. ✅ Options Risk Engine (DONE)
2. Data Layer (Redis Streams, TimeSeries)
3. WebSocket infrastructure
4. Basic agent scaffolding

**PHASE 2: Scanner Agents (Week 3)**
1. Options Flow Scanner (Unusual Whales integration)
2. GEX Scanner
3. Technical Scanner (TA patterns)
4. Signal queue + prioritization

**PHASE 3: Analyst Agents (Week 4)**
1. Strategy Analyst (signal → strategy)
2. Risk Analyst (portfolio Greeks, VaR)
3. Integration with Options Risk Engine

**PHASE 4: Orchestrator + ML (Week 5-6)**
1. Master Orchestrator (LLM decision maker)
2. ML models training (signal confidence)
3. Backtest validation

**PHASE 5: Execution + Monitoring (Week 7)**
1. Order Executor (broker integration)
2. Position Manager (auto-management)
3. Live monitoring dashboard

---

## 🎯 SUCCESS METRICS

- **Signal Quality:** >70% win rate on executed trades
- **Response Time:** <30s from signal to execution
- **Risk Management:** Max drawdown <10%
- **Uptime:** >99% agent availability
- **Latency:** <100ms WebSocket updates

---

**Next Question:** Care vrei să construim primul - Data Layer sau Scanner Agents? Sau preferi să vezi UI mockup-ul pentru Trade Desk Live?

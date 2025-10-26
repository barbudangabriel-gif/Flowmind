/**
 * StrategyEngine - Universal P&L Calculator for All Options Strategies
 * 
 * Purpose: Generate P&L curves, calculate Greeks, and compute metrics for ANY strategy
 * defined in strategies.json. Eliminates need for manual implementation of 69 strategies.
 * 
 * Features:
 * - Universal formula parser with variable substitution
 * - Black-Scholes Greeks calculation for each leg
 * - Automatic breakeven finder
 * - Support for simple (Long Call) and complex (Iron Condor) strategies
 */

import STRATEGIES from '../config/strategies.json';

class StrategyEngine {
  constructor(strategyId, currentPrice = 250, optionsData = null) {
    this.strategyId = strategyId;
    this.config = STRATEGIES[strategyId];
    
    if (!this.config) {
      throw new Error(`Strategy "${strategyId}" not found in strategies.json`);
    }
    
    this.currentPrice = currentPrice;
    this.optionsData = optionsData;
    this.legs = [];
    this.netCost = 0;
    this.strikes = {};
  }

  /**
   * Initialize strategy with strikes and premiums
   * @param {Object} params - { strikes: {lower: 220, higher: 240}, premiums: {lower: 35, higher: 10} }
   */
  initialize(params = {}) {
    const { strikes = {}, premiums = {} } = params;
    
    this.legs = this.config.legs.map((legConfig, idx) => {
      let strike, premium;
      
      if (legConfig.strike_label) {
        // Multi-leg strategy (e.g., Bull Call Spread)
        strike = strikes[legConfig.strike_label] || this.currentPrice;
        premium = premiums[legConfig.strike_label] || 0;
      } else {
        // Single-leg strategy (e.g., Long Call)
        strike = strikes.strike || this.currentPrice + legConfig.strike_offset;
        premium = premiums.premium || 0;
      }
      
      // Store strikes for formula evaluation
      if (legConfig.strike_label) {
        this.strikes[`${legConfig.strike_label}_strike`] = strike;
      } else {
        this.strikes.strike = strike;
      }
      
      return {
        ...legConfig,
        strike,
        premium,
        legIndex: idx
      };
    });
    
    // Calculate net cost (debit/credit)
    this.netCost = this.calculateNetCost();
    
    return this;
  }

  /**
   * Calculate net debit/credit for the strategy
   */
  calculateNetCost() {
    return this.legs.reduce((total, leg) => {
      const multiplier = leg.action === 'buy' ? 1 : -1;
      return total + (leg.premium * multiplier);
    }, 0);
  }

  /**
   * Generate P&L curve across price range
   * @param {number} priceMin - Starting price
   * @param {number} priceMax - Ending price
   * @param {number} step - Price step size
   * @returns {Array} Array of {price, pnl} objects
   */
  generatePnLCurve(priceMin, priceMax, step = 1) {
    const points = [];
    
    // Collect all critical strike prices for sharp angles
    const criticalPrices = new Set();
    if (this.strikes.strike) criticalPrices.add(this.strikes.strike);
    if (this.strikes.lower_strike) criticalPrices.add(this.strikes.lower_strike);
    if (this.strikes.higher_strike) criticalPrices.add(this.strikes.higher_strike);
    
    // Generate regular points
    for (let price = priceMin; price <= priceMax; price += step) {
      points.push({ price, pnl: this.calculatePnL(price) });
      
      // Add critical prices nearby (for sharp angles)
      for (const strike of criticalPrices) {
        if (price < strike && price + step > strike) {
          // Insert point exactly at strike
          points.push({ price: strike, pnl: this.calculatePnL(strike) });
        }
      }
    }
    
    // Sort by price
    points.sort((a, b) => a.price - b.price);
    
    return points;
  }

  /**
   * Calculate P&L at specific price point
   * @param {number} price - Stock price at expiration
   * @returns {number} P&L in dollars
   */
  calculatePnL(price) {
    const formula = this.getFormulaForPrice(price);
    return this.evaluateFormula(formula, price);
  }

  /**
   * Determine which formula applies to current price
   */
  getFormulaForPrice(price) {
    const { pnl_formula } = this.config;
    
    if (pnl_formula.type === 'simple') {
      // Simple strategy (Long Call, Long Put)
      const strike = this.legs[0].strike;
      
      if (this.config.category === 'bearish') {
        return price < strike ? pnl_formula.below_strike : pnl_formula.above_strike;
      } else {
        return price < strike ? pnl_formula.below_strike : pnl_formula.above_strike;
      }
      
    } else if (pnl_formula.type === 'multi_segment') {
      // Multi-leg strategy (Bull Call Spread, Iron Condor)
      for (const segment of pnl_formula.segments) {
        if (this.isPriceInRange(price, segment.range)) {
          return segment.formula;
        }
      }
    }
    
    return "0"; // Fallback
  }

    /**
   * Check if price is in specified range
   */
  isPriceInRange(price, range) {
    switch (range) {
      case 'below_lower':
        return price <= this.strikes.lower_strike;
      
      case 'above_higher':
        return price >= this.strikes.higher_strike;
      
      case 'below_higher':
        return price < this.strikes.higher_strike;
      
      case 'above_lower':
        return price > this.strikes.lower_strike;
      
      case 'between':
        return price > this.strikes.lower_strike && price < this.strikes.higher_strike;
      
      default:
        return false;
    }
  }

  /**
   * Evaluate formula string with variable substitution
   * @param {string} formula - Formula like "(price - strike) * 100 - premium"
   * @param {number} price - Current price (can be null for max_profit/max_loss)
   * @returns {number} Calculated value
   */
  evaluateFormula(formula, price) {
    // Build variable map
    const vars = {
      price,
      premium: this.netCost,
      net_debit: Math.abs(this.netCost),
      net_credit: -this.netCost,
      quantity: this.legs[0]?.quantity || 1,
      ...this.strikes
    };
    
    // Replace variables in formula (skip null/undefined values)
    let expression = formula;
    for (const [key, value] of Object.entries(vars)) {
      if (value !== null && value !== undefined) {
        const regex = new RegExp(`\\b${key}\\b`, 'g');
        expression = expression.replace(regex, value.toString());
      }
    }
    
    // Safe evaluation (in production, use math.js or similar)
    try {
      // eslint-disable-next-line no-eval
      return eval(expression);
    } catch (err) {
      console.error('Formula evaluation error:', formula, expression, err);
      return 0;
    }
  }

  /**
   * Calculate breakeven price(s)
   * @returns {Array} Array of breakeven prices
   */
  calculateBreakeven() {
    const { breakeven } = this.config;
    
    if (Array.isArray(breakeven)) {
      // Multiple breakevens (e.g., Iron Condor)
      return breakeven.map(formula => this.evaluateFormula(formula, null));
    } else {
      // Single breakeven
      return [this.evaluateFormula(breakeven, null)];
    }
  }

  /**
   * Calculate max profit
   * @returns {number|string} Max profit value or "unlimited"
   */
  calculateMaxProfit() {
    const { max_profit } = this.config;
    
    if (max_profit === 'unlimited') {
      return 'unlimited';
    }
    
    return this.evaluateFormula(max_profit, null);
  }

  /**
   * Calculate max loss
   * @returns {number} Max loss value (always positive)
   */
  calculateMaxLoss() {
    const { max_loss } = this.config;
    return Math.abs(this.evaluateFormula(max_loss, null));
  }

  /**
   * Get comprehensive strategy metrics
   * @returns {Object} Strategy metrics
   */
  getMetrics() {
    return {
      id: this.strategyId,
      name: this.config.name,
      category: this.config.category,
      complexity: this.config.complexity,
      description: this.config.description,
      maxProfit: this.calculateMaxProfit(),
      maxLoss: this.calculateMaxLoss(),
      breakeven: this.calculateBreakeven(),
      netCost: this.netCost,
      netDebit: Math.abs(this.netCost),
      legs: this.legs,
      strikes: this.strikes,
      idealConditions: this.config.ideal_conditions,
      riskReward: this.config.risk_reward
    };
  }

  /**
   * Calculate Greeks (Delta, Gamma, Theta, Vega) using Black-Scholes
   * @param {number} volatility - Implied volatility (e.g., 0.30 for 30%)
   * @param {number} daysToExpiry - Days until expiration
   * @param {number} riskFreeRate - Annual risk-free rate (default 0.05)
   * @returns {Object} Greeks {delta, gamma, theta, vega}
   */
  calculateGreeks(volatility = 0.30, daysToExpiry = 30, riskFreeRate = 0.05) {
    const T = daysToExpiry / 365; // Convert to years
    
    return this.legs.reduce((acc, leg) => {
      const legGreeks = this.blackScholes(
        this.currentPrice,
        leg.strike,
        T,
        volatility,
        riskFreeRate,
        leg.type === 'call'
      );
      
      const multiplier = leg.quantity * (leg.action === 'buy' ? 1 : -1);
      
      return {
        delta: acc.delta + legGreeks.delta * multiplier,
        gamma: acc.gamma + legGreeks.gamma * multiplier,
        theta: acc.theta + legGreeks.theta * multiplier,
        vega: acc.vega + legGreeks.vega * multiplier
      };
    }, { delta: 0, gamma: 0, theta: 0, vega: 0 });
  }

  /**
   * Black-Scholes formula for option pricing and Greeks
   */
  blackScholes(S, K, T, sigma, r = 0.05, isCall = true) {
    if (T <= 0) {
      // At expiration
      const intrinsic = isCall ? Math.max(S - K, 0) : Math.max(K - S, 0);
      return { price: intrinsic, delta: 0, gamma: 0, theta: 0, vega: 0 };
    }
    
    const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);
    
    const N_d1 = this.normCDF(d1);
    const N_d2 = this.normCDF(d2);
    const n_d1 = this.normPDF(d1); // Standard normal PDF
    
    // Option price
    const price = isCall
      ? S * N_d1 - K * Math.exp(-r * T) * N_d2
      : K * Math.exp(-r * T) * this.normCDF(-d2) - S * this.normCDF(-d1);
    
    // Greeks
    const delta = isCall ? N_d1 : N_d1 - 1;
    const gamma = n_d1 / (S * sigma * Math.sqrt(T));
    const theta = isCall
      ? (-(S * n_d1 * sigma) / (2 * Math.sqrt(T)) - r * K * Math.exp(-r * T) * N_d2) / 365
      : (-(S * n_d1 * sigma) / (2 * Math.sqrt(T)) + r * K * Math.exp(-r * T) * this.normCDF(-d2)) / 365;
    const vega = (S * n_d1 * Math.sqrt(T)) / 100; // Vega per 1% change in IV
    
    return { price, delta, gamma, theta, vega };
  }

  /**
   * Standard normal cumulative distribution function
   */
  normCDF(x) {
    const t = 1 / (1 + 0.2316419 * Math.abs(x));
    const d = 0.3989423 * Math.exp(-x * x / 2);
    const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return x > 0 ? 1 - prob : prob;
  }

  /**
   * Standard normal probability density function
   */
  normPDF(x) {
    return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
  }
}

export default StrategyEngine;

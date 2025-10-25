/**
 * StrategyEngine Test - Verify P&L calculations match expected values
 * 
 * Run: node frontend/src/services/__tests__/StrategyEngine.test.js
 */

import StrategyEngine from '../StrategyEngine.js';

console.log('\n🧪 StrategyEngine Test Suite\n');

// Test 1: Long Call Strategy
console.log('📊 Test 1: Long Call Strategy');
console.log('───────────────────────────────');

const longCallEngine = new StrategyEngine('long_call', 224.21);
longCallEngine.initialize({
  strikes: { strike: 220 },
  premiums: { premium: 3933 } // $39.33 per share × 100
});

const longCallMetrics = longCallEngine.getMetrics();
console.log('Strategy:', longCallMetrics.name);
console.log('Net Cost:', `$${longCallMetrics.netCost.toFixed(2)}`);
console.log('Max Loss:', `$${longCallMetrics.maxLoss.toFixed(2)}`);
console.log('Max Profit:', longCallMetrics.maxProfit);
console.log('Breakeven:', `$${longCallMetrics.breakeven[0].toFixed(2)}`);

// Generate P&L curve
const longCallCurve = longCallEngine.generatePnLCurve(100, 330, 10);
console.log('\nP&L Curve (sample points):');
longCallCurve.forEach(point => {
  const sign = point.pnl >= 0 ? '+' : '';
  console.log(`  Price $${point.price.toFixed(2)} → P&L ${sign}$${point.pnl.toFixed(2)}`);
});

// Calculate Greeks
const longCallGreeks = longCallEngine.calculateGreeks(0.344, 438); // IV=34.4%, DTE=438
console.log('\nGreeks:');
console.log(`  Delta: ${longCallGreeks.delta.toFixed(4)}`);
console.log(`  Gamma: ${longCallGreeks.gamma.toFixed(4)}`);
console.log(`  Theta: ${longCallGreeks.theta.toFixed(4)}`);
console.log(`  Vega: ${longCallGreeks.vega.toFixed(4)}`);

// Verify expected values (from BuilderV2Page implementation)
console.log('\n✅ Expected vs Actual:');
console.log(`  Breakeven: Expected ~$259.33, Got $${longCallMetrics.breakeven[0].toFixed(2)}`);
console.log(`  Max Loss: Expected $3,933, Got $${longCallMetrics.maxLoss.toFixed(0)}`);

// Test 2: Bull Call Spread Strategy
console.log('\n\n📊 Test 2: Bull Call Spread Strategy');
console.log('───────────────────────────────────');

const bullSpreadEngine = new StrategyEngine('bull_call_spread', 250);
bullSpreadEngine.initialize({
  strikes: { lower: 240, higher: 260 },
  premiums: { lower: 1500, higher: 800 } // Buy 240C @ $15, Sell 260C @ $8
});

const bullSpreadMetrics = bullSpreadEngine.getMetrics();
console.log('Strategy:', bullSpreadMetrics.name);
console.log('Net Debit:', `$${bullSpreadMetrics.netDebit.toFixed(2)}`);
console.log('Max Loss:', `$${bullSpreadMetrics.maxLoss.toFixed(2)}`);
console.log('Max Profit:', `$${bullSpreadMetrics.maxProfit.toFixed(2)}`);
console.log('Breakeven:', `$${bullSpreadMetrics.breakeven[0].toFixed(2)}`);

// Generate P&L curve
const bullSpreadCurve = bullSpreadEngine.generatePnLCurve(200, 300, 20);
console.log('\nP&L Curve (sample points):');
bullSpreadCurve.forEach(point => {
  const sign = point.pnl >= 0 ? '+' : '';
  console.log(`  Price $${point.price.toFixed(2)} → P&L ${sign}$${point.pnl.toFixed(2)}`);
});

// Calculate Greeks
const bullSpreadGreeks = bullSpreadEngine.calculateGreeks(0.30, 30);
console.log('\nGreeks:');
console.log(`  Delta: ${bullSpreadGreeks.delta.toFixed(4)}`);
console.log(`  Gamma: ${bullSpreadGreeks.gamma.toFixed(4)}`);
console.log(`  Theta: ${bullSpreadGreeks.theta.toFixed(4)}`);
console.log(`  Vega: ${bullSpreadGreeks.vega.toFixed(4)}`);

// Verify spread width
const spreadWidth = (260 - 240) * 100;
console.log('\n✅ Expected vs Actual:');
console.log(`  Spread Width: Expected $2,000, Got $${spreadWidth}`);
console.log(`  Max Profit: Expected ~$1,300, Got $${bullSpreadMetrics.maxProfit.toFixed(0)}`);
console.log(`  Max Loss: Expected $700, Got $${bullSpreadMetrics.maxLoss.toFixed(0)}`);

// Test 3: Long Put Strategy
console.log('\n\n📊 Test 3: Long Put Strategy');
console.log('──────────────────────────────');

const longPutEngine = new StrategyEngine('long_put', 250);
longPutEngine.initialize({
  strikes: { strike: 240 },
  premiums: { premium: 1200 } // $12 per share × 100
});

const longPutMetrics = longPutEngine.getMetrics();
console.log('Strategy:', longPutMetrics.name);
console.log('Net Cost:', `$${longPutMetrics.netCost.toFixed(2)}`);
console.log('Max Loss:', `$${longPutMetrics.maxLoss.toFixed(2)}`);
console.log('Max Profit:', `$${longPutMetrics.maxProfit.toFixed(2)}`);
console.log('Breakeven:', `$${longPutMetrics.breakeven[0].toFixed(2)}`);

// Generate P&L curve
const longPutCurve = longPutEngine.generatePnLCurve(180, 280, 20);
console.log('\nP&L Curve (sample points):');
longPutCurve.forEach(point => {
  const sign = point.pnl >= 0 ? '+' : '';
  console.log(`  Price $${point.price.toFixed(2)} → P&L ${sign}$${point.pnl.toFixed(2)}`);
});

console.log('\n✅ Expected vs Actual:');
console.log(`  Breakeven: Expected $228, Got $${longPutMetrics.breakeven[0].toFixed(2)}`);
console.log(`  Max Profit (at $0): Expected $22,800, Got $${longPutMetrics.maxProfit.toFixed(0)}`);

// Test 4: Bear Put Spread Strategy
console.log('\n\n📊 Test 4: Bear Put Spread Strategy');
console.log('───────────────────────────────────');

const bearSpreadEngine = new StrategyEngine('bear_put_spread', 250);
bearSpreadEngine.initialize({
  strikes: { higher: 260, lower: 240 },
  premiums: { higher: 1500, lower: 800 } // Buy 260P @ $15, Sell 240P @ $8
});

const bearSpreadMetrics = bearSpreadEngine.getMetrics();
console.log('Strategy:', bearSpreadMetrics.name);
console.log('Net Debit:', `$${bearSpreadMetrics.netDebit.toFixed(2)}`);
console.log('Max Loss:', `$${bearSpreadMetrics.maxLoss.toFixed(2)}`);
console.log('Max Profit:', `$${bearSpreadMetrics.maxProfit.toFixed(2)}`);
console.log('Breakeven:', `$${bearSpreadMetrics.breakeven[0].toFixed(2)}`);

// Generate P&L curve
const bearSpreadCurve = bearSpreadEngine.generatePnLCurve(200, 300, 20);
console.log('\nP&L Curve (sample points):');
bearSpreadCurve.forEach(point => {
  const sign = point.pnl >= 0 ? '+' : '';
  console.log(`  Price $${point.price.toFixed(2)} → P&L ${sign}$${point.pnl.toFixed(2)}`);
});

console.log('\n✅ Expected vs Actual:');
console.log(`  Spread Width: Expected $2,000, Got $${(260 - 240) * 100}`);
console.log(`  Max Profit: Expected ~$1,300, Got $${bearSpreadMetrics.maxProfit.toFixed(0)}`);
console.log(`  Max Loss: Expected $700, Got $${bearSpreadMetrics.maxLoss.toFixed(0)}`);

console.log('\n\n🎉 All tests completed!\n');

import { ALL_STRATEGIES } from "./strategies"; // catalogul existent cu ~60 strategii

// Organizare strategii pe niveluri și grupe ca în screenshot
export const strategiesByLevel = {
 novice: [
 { 
 title: "Basic", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'long-call') || { id: 'long_call', name: 'Long Call', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'long-put') || { id: 'long_put', name: 'Long Put', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'short_call') || { id: 'short_call', name: 'Short Call', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'short_put') || { id: 'short_put', name: 'Short Put', stance: 'bullish' },
 ].filter(Boolean)
 },
 { 
 title: "Income", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'covered-call') || { id: 'covered_call', name: 'Covered Call', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'cash-secured-put') || { id: 'cash_secured_put', name: 'Cash Secured Put', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'wheel_strategy') || { id: 'wheel_strategy', name: 'Wheel Strategy', stance: 'neutral' },
 ].filter(Boolean)
 },
 { 
 title: "Protection", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'protective-put') || { id: 'protective_put', name: 'Protective Put', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'covered_put') || { id: 'covered_put', name: 'Covered Put', stance: 'bearish' },
 ].filter(Boolean)
 },
 ],
 
 intermediate: [
 { 
 title: "Spreads", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'bull-call-spread') || { id: 'bull_call_spread', name: 'Bull Call Spread', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'bear-call-spread') || { id: 'bear_call_spread', name: 'Bear Call Spread', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'bull-put-spread') || { id: 'bull_put_spread', name: 'Bull Put Spread', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'bear-put-spread') || { id: 'bear_put_spread', name: 'Bear Put Spread', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'calendar_spread') || { id: 'calendar_spread', name: 'Calendar Spread', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'diagonal_spread') || { id: 'diagonal_spread', name: 'Diagonal Spread', stance: 'neutral' },
 ].filter(Boolean)
 },
 { 
 title: "Volatility", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'long-straddle') || { id: 'long_straddle', name: 'Long Straddle', stance: 'directional' },
 ALL_STRATEGIES.find(s => s.id === 'short_straddle') || { id: 'short_straddle', name: 'Short Straddle', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'long-strangle') || { id: 'long_strangle', name: 'Long Strangle', stance: 'directional' },
 ALL_STRATEGIES.find(s => s.id === 'short_strangle') || { id: 'short_strangle', name: 'Short Strangle', stance: 'neutral' },
 ].filter(Boolean)
 },
 { 
 title: "Collar", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'collar') || { id: 'collar', name: 'Collar', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'risk_reversal') || { id: 'risk_reversal', name: 'Risk Reversal', stance: 'directional' },
 ].filter(Boolean)
 },
 ],
 
 advanced: [
 { 
 title: "Multi-Leg", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'iron-condor') || { id: 'iron_condor', name: 'Iron Condor', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'iron-butterfly') || { id: 'iron_butterfly', name: 'Iron Butterfly', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'butterfly_spread') || { id: 'butterfly_spread', name: 'Butterfly Spread', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'condor_spread') || { id: 'condor_spread', name: 'Condor Spread', stance: 'neutral' },
 ].filter(Boolean)
 },
 { 
 title: "Ratio", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'ratio_call_spread') || { id: 'ratio_call_spread', name: 'Ratio Call Spread', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'ratio_put_spread') || { id: 'ratio_put_spread', name: 'Ratio Put Spread', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'call-ratio-backspread') || { id: 'ratio_backspread', name: 'Ratio Backspread', stance: 'directional' },
 ].filter(Boolean)
 },
 { 
 title: "Time Decay", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'jade-lizard') || { id: 'jade_lizard', name: 'Jade Lizard', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'big_lizard') || { id: 'big_lizard', name: 'Big Lizard', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'broken_wing_butterfly') || { id: 'broken_wing_butterfly', name: 'Broken Wing Butterfly', stance: 'directional' },
 ].filter(Boolean)
 },
 ],
 
 expert: [
 { 
 title: "Complex Spreads", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'double_diagonal') || { id: 'double_diagonal', name: 'Double Diagonal', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'christmas_tree') || { id: 'christmas_tree', name: 'Christmas Tree', stance: 'directional' },
 ALL_STRATEGIES.find(s => s.id === 'zebra_spread') || { id: 'zebra_spread', name: 'Zebra Spread', stance: 'directional' },
 ].filter(Boolean)
 },
 { 
 title: "Exotic", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'synthetic-long-future') || { id: 'synthetic_long', name: 'Synthetic Long', stance: 'bullish' },
 ALL_STRATEGIES.find(s => s.id === 'synthetic_short') || { id: 'synthetic_short', name: 'Synthetic Short', stance: 'bearish' },
 ALL_STRATEGIES.find(s => s.id === 'conversion') || { id: 'conversion', name: 'Conversion', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'reversal') || { id: 'reversal', name: 'Reversal', stance: 'neutral' },
 ].filter(Boolean)
 },
 { 
 title: "Arbitrage", 
 items: [
 ALL_STRATEGIES.find(s => s.id === 'box_spread') || { id: 'box_spread', name: 'Box Spread', stance: 'neutral' },
 ALL_STRATEGIES.find(s => s.id === 'jelly_roll') || { id: 'jelly_roll', name: 'Jelly Roll', stance: 'neutral' },
 ].filter(Boolean)
 },
 ],
};

// Deep-link către Builder cu payload preconfigurat
export function deepLinkFromStrategy(strategy, { symbol = "TSLA", qty = 1 } = {}) {
 if (!strategy) return '/build/manual';
 
 // Construiește payload-ul pentru Builder
 const payload = {
 symbol,
 strategyId: strategy.id,
 qty,
 legs: strategy.buildParams ? strategy.buildParams(symbol)?.legs || [] : [],
 params: { iv_mult: 1.0, range_pct: 0.15 },
 meta: { 
 from: "menu", 
 stance: strategy.stance || 'neutral',
 level: strategy.level || 'intermediate'
 }
 };
 
 try {
 const json = JSON.stringify(payload);
 const b64 = typeof window !== "undefined"
 ? btoa(unescape(encodeURIComponent(json)))
 .replace(/\+/g, "-")
 .replace(/\//g, "_")
 .replace(/=+$/, "")
 : "";
 return `/build/${strategy.id}?s=${b64}`;
 } catch (error) {
 console.warn('Deep link generation failed:', error);
 return `/build/${strategy.id}`;
 }
}

// Utility pentru a obține strategiile cu fallback
export function getStrategyById(id) {
 return ALL_STRATEGIES.find(s => s.id === id) || {
 id,
 name: id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
 stance: 'neutral',
 level: 'intermediate'
 };
}
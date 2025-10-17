// app/frontend/src/lib/strategies.js
import { strategiesByLevel, getStrategyById } from '../data/strategies-helpers';

// === LISTA CANONICĂ (STRICT după specificația ta) ===
// Lista cu strategiile care trebuie să apară în mega menu
export const STRATEGY_META = {
 // Income 
 wheel_strategy: { name: 'Wheel Strategy', category: 'Income', id: 'wheel_strategy' },
 covered_put: { name: 'Covered Put', category: 'Income', id: 'covered_put' },

 // Spreads (Time/Price)
 calendar_spread: { name: 'Calendar Spread', category: 'Spreads', id: 'calendar_spread' },
 diagonal_spread: { name: 'Diagonal Spread', category: 'Spreads', id: 'diagonal_spread' },
 butterfly_spread: { name: 'Butterfly Spread', category: 'Spreads', id: 'butterfly_spread' },
 condor_spread: { name: 'Condor Spread', category: 'Spreads', id: 'condor_spread' },
 broken_wing_butterfly: { name: 'Broken Wing Butterfly', category: 'Spreads', id: 'broken_wing_butterfly' },
 double_diagonal: { name: 'Double Diagonal', category: 'Spreads', id: 'double_diagonal' },
 ratio_call_spread: { name: 'Ratio Call Spread', category: 'Spreads', id: 'ratio_call_spread' },
 ratio_put_spread: { name: 'Ratio Put Spread', category: 'Spreads', id: 'ratio_put_spread' },
 christmas_tree: { name: 'Christmas Tree', category: 'Spreads', id: 'christmas_tree' },
 zebra_spread: { name: 'ZEBRA Spread', category: 'Spreads', id: 'zebra_spread' },
 box_spread: { name: 'Box Spread', category: 'Spreads', id: 'box_spread' },

 // Volatility / Collar
 short_straddle: { name: 'Short Straddle', category: 'Volatility/Collar', id: 'short_straddle' },
 short_strangle: { name: 'Short Strangle', category: 'Volatility/Collar', id: 'short_strangle' },
 collar: { name: 'Collar', category: 'Volatility/Collar', id: 'collar' },
 risk_reversal: { name: 'Risk Reversal', category: 'Volatility/Collar', id: 'risk_reversal' },

 // Multi-Leg / Synthetic / Arbitrage
 big_lizard: { name: 'Big Lizard', category: 'Multi-Leg / Synthetic', id: 'big_lizard' },
 synthetic_short: { name: 'Synthetic Short', category: 'Multi-Leg / Synthetic', id: 'synthetic_short' },
 conversion: { name: 'Conversion', category: 'Multi-Leg / Synthetic', id: 'conversion' },
 reversal: { name: 'Reversal', category: 'Multi-Leg / Synthetic', id: 'reversal' },
 jelly_roll: { name: 'Jelly Roll', category: 'Multi-Leg / Synthetic', id: 'jelly_roll' },
};

// Ordinea în meniu: grupează clar pe categorii
export const STRATEGY_ORDER = [
 // Income
 'wheel_strategy', 'covered_put',
 // Spreads
 'calendar_spread', 'diagonal_spread', 'butterfly_spread', 'condor_spread',
 'broken_wing_butterfly', 'double_diagonal', 'ratio_call_spread', 'ratio_put_spread',
 'christmas_tree', 'zebra_spread', 'box_spread',
 // Volatility/Collar
 'short_straddle', 'short_strangle', 'collar', 'risk_reversal',
 // Multi-Leg / Synthetic / Arbitrage
 'big_lizard', 'synthetic_short', 'conversion', 'reversal', 'jelly_roll',
];

// Construim registrul final - mapare între slug și strategia din helpers
export const STRATEGY_REGISTRY = STRATEGY_ORDER.reduce((acc, slug) => {
 const meta = STRATEGY_META[slug];
 if (!meta) {
 console.error(`[Strategies] Missing meta for: ${slug}`);
 return acc;
 }
 
 // Încearcă să găsească strategia în helpers
 const strategy = getStrategyById(meta.id);
 if (strategy) {
 acc[slug] = { 
 slug, 
 ...meta, 
 ...strategy,
 tags: strategy.tags || ['advanced'],
 stance: strategy.stance || 'neutral',
 level: strategy.level || 'Advanced'
 };
 } else {
 console.warn(`[Strategies] Strategy not found in helpers: ${meta.id}`);
 // Creez o strategie placeholder
 acc[slug] = {
 slug,
 ...meta,
 tags: ['advanced'],
 stance: 'neutral', 
 level: 'Advanced',
 buildParams: () => ({ strategyId: meta.id, legs: [] })
 };
 }
 return acc;
}, {});

// Grupare pe categorii pentru Build menu
export const STRATEGIES_BY_CATEGORY = Object.values(STRATEGY_REGISTRY)
 .reduce((groups, strategy) => {
 const category = strategy.category;
 if (!groups[category]) {
 groups[category] = [];
 }
 groups[category].push(strategy);
 return groups;
 }, {});

// Total count pentru display
export const TOTAL_STRATEGIES = STRATEGY_ORDER.length;

// Debug logging pentru verificare
console.log(`[Strategies] Loaded ${TOTAL_STRATEGIES} strategies:`, STRATEGY_ORDER);
console.log('[Strategies] By category:', Object.keys(STRATEGIES_BY_CATEGORY).map(cat => `${cat}: ${STRATEGIES_BY_CATEGORY[cat].length}`).join(', '));
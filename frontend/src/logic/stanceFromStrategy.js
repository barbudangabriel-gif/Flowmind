// logic/stanceFromStrategy.js
const STRATEGY_STANCE_MAP = {
 // Novice / Income
 'long-call': 'bullish',
 'long-put': 'bearish',
 'covered-call': 'neutral',
 'cash-secured-put': 'bullish',
 'protective-put': 'bearish',

 // Intermediate
 'bull-put-spread': 'bullish',
 'bear-call-spread': 'bearish',
 'bull-call-spread': 'bullish',
 'bear-put-spread': 'bearish',
 'iron-condor': 'neutral',
 'iron-butterfly': 'neutral',
 'long-call-butterfly': 'neutral',
 'long-put-butterfly': 'neutral',
 'calendar-call': 'directional',
 'calendar-put': 'directional',
 'diagonal-call': 'directional',
 'diagonal-put': 'directional',
 'collar': 'neutral',

 // Advanced
 'short-call': 'bearish',
 'short-put': 'bullish',
 'covered-short-straddle': 'neutral',
 'covered-short-strangle': 'neutral',
 'short-call-condor': 'directional',
 'short-put-condor': 'directional',
 'short-call-butterfly': 'directional',
 'short-put-butterfly': 'directional',
 'inverse-iron-butterfly': 'directional',
 'inverse-iron-condor': 'directional',
 'bull-call-ladder': 'directional',
 'bear-put-ladder': 'directional',
 'call-ratio-backspread': 'directional',
 'put-ratio-backspread': 'directional',
 'call-broken-wing-butterfly': 'directional',
 'put-broken-wing-butterfly': 'directional',
 'reverse-call-ratio': 'directional',
 'reverse-put-ratio': 'directional',

 // Expert
 'synthetic-long-future': 'bullish',
 'synthetic-short-future': 'bearish',
 'synthetic-put': 'directional',
 'synthetic-call': 'directional',
 'long-combo': 'directional',
 'short-combo': 'directional',
 'long-straddle': 'neutral',
 'long-strangle': 'neutral',
 'short-straddle': 'neutral',
 'short-strangle': 'neutral',
 'strip': 'bearish',
 'strap': 'bullish',
 'guts': 'neutral',
 'short-guts': 'neutral',
 'double-diagonal': 'directional',
};

export function stanceFromStrategy(strategyId, legs) {
 const netDelta = legs.reduce((s, l) => s + (l.greeks?.delta ?? 0) * (l.side === 'BUY' ? 1 : -1) * l.qty, 0);

 const hasCall = legs.some(l => l.type === 'CALL');
 const hasPut = legs.some(l => l.type === 'PUT');
 const strength = Math.abs(netDelta) >= 0.60 ? 'very' : 'normal';

 // Use strategy mapping first
 if (STRATEGY_STANCE_MAP[strategyId]) {
 return { stance: STRATEGY_STANCE_MAP[strategyId], strength };
 }

 // Fallback logic
 if (Math.abs(netDelta) < 0.10) {
 const directionalIds = ['calendar-call', 'calendar-put', 'diagonal-call', 'diagonal-put', 'ratio-call', 'ratio-put', 'broken-wing', 'jade-lizard', 'iron-fly'];
 if (hasCall && hasPut && directionalIds.some(id => strategyId.includes(id))) {
 return { stance: 'directional', strength };
 }
 return { stance: 'neutral', strength: 'normal' };
 }

 // Directional: mix CALL+PUT cu Δ semnificativ
 if (hasCall && hasPut && Math.abs(netDelta) >= 0.10) {
 return { stance: 'directional', strength };
 }

 // Classic: sign of Δ decides
 return netDelta > 0
 ? { stance: 'bullish', strength }
 : { stance: 'bearish', strength };
}

export function strengthFromNetDelta(netDelta) {
 return Math.abs(netDelta || 0) >= 0.60 ? 'very' : 'normal';
}
// src/lib/buildStrategies.js
export const BUILD_STRATEGIES = [
 {
 level: 'Novice',
 groups: [
 { title: 'BASIC', items: ['Long Call','Long Put'] },
 { title: 'INCOME', items: ['Covered Call','Cash-Secured Put'] },
 { title: 'OTHER', items: ['Protective Put'] },
 ],
 },
 {
 level: 'Intermediate',
 groups: [
 { title: 'CREDIT SPREADS', items: ['Bull Put Spread','Bear Call Spread'] },
 { title: 'DEBIT SPREADS', items: ['Bull Call Spread','Bear Put Spread'] },
 { title: 'NEUTRAL', items: ['Iron Butterfly','Iron Condor','Long Put Butterfly','Long Call Butterfly'] },
 { title: 'CALENDAR SPREADS', items: ['Calendar Call Spread','Calendar Put Spread','Diagonal Call Spread','Diagonal Put Spread'] },
 { title: 'DIRECTIONAL', items: ['Inverse Iron Butterfly','Inverse Iron Condor','Short Put Butterfly','Short Call Butterfly','Straddle','Strangle'] },
 { title: 'OTHER', items: ['Collar'] },
 ],
 },
 {
 level: 'Advanced',
 groups: [
 { title: 'NAKED', items: ['Short Put','Short Call'] },
 { title: 'NEUTRAL', items: ['Short Iron Condor','Short Iron Butterfly'] },
 { title: 'INCOME', items: ['Covered Short Straddle','Covered Short Strangle'] },
 { title: 'DIRECTIONAL', items: ['Short Call Condor','Short Put Condor'] },
 { title: 'LADDERS', items: ['Bull Call Ladder','Bear Call Ladder','Bull Put Ladder','Bear Put Ladder'] },
 { title: 'RATIO SPREADS', items: ['Call Ratio Backspread','Put Ratio Backspread','Call Broken Wing','Put Broken Wing'] },
 { title: 'OTHER', items: ['Jade Lizard','Reverse Jade Lizard'] },
 ],
 },
 {
 level: 'Expert',
 groups: [
 { title: 'RATIO SPREADS', items: ['Call Ratio Spread','Put Ratio Spread'] },
 { title: 'SYNTHETIC', items: ['Long Synthetic Future','Short Synthetic Future','Synthetic Put'] },
 { title: 'ARBITRAGE', items: ['Long Combo','Short Combo'] },
 { title: 'OTHER', items: ['Strip','Strap','Guts','Short Guts','Double Diagonal'] },
 ],
 },
];

// utilitare minimale
export const toSlug = (name) =>
 name.toLowerCase().replace(/\s+/g, '_').replace(/[^\w_]/g, '');

export const FLAT_BUILD_LIST = BUILD_STRATEGIES.flatMap(sec =>
 sec.groups.flatMap(g => g.items.map(n => ({
 name: n, slug: toSlug(n), level: sec.level, category: g.title,
 })))
);
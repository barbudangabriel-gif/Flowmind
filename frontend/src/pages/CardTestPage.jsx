import React from 'react';
import StrategyCard from '../components/StrategyCard';

/**
 * CardTestPage - Test page for developing StrategyCard component
 * Shows only Long Call card for easier iteration
 */
export default function CardTestPage() {
  // Long Call strategy data matching Screenshot_545
  const longCallStrategy = {
    name: 'Long Call',
    legs: [
      { side: 'BUY', kind: 'CALL', strike: '195', qty: 1 }
    ],
    returnPercent: 90,
    chancePercent: 45,
    profit: 2315.16,
    risk: 2580,
    collateral: 0,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-md mx-auto">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-white mb-2">Strategy Card Test</h1>
          <p className="text-slate-400 text-sm">Long Call - Screenshot_545 Reference</p>
        </div>

        <StrategyCard
          strategy={longCallStrategy}
          onClick={() => console.log('Card clicked')}
        />

        <div className="mt-6 p-4 bg-slate-800/50 border border-slate-700/50 rounded-lg text-sm text-slate-300">
          <h3 className="font-semibold text-white mb-2">Expected from Screenshot_545:</h3>
          <ul className="space-y-1 text-xs">
            <li>• Background: #282841</li>
            <li>• Border: #31314a</li>
            <li>• Chart BG: #1e1e35</li>
            <li>• Profit line (above 0): GREEN</li>
            <li>• Loss line (below 0): RED</li>
            <li>• Zero line: Dashed white</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

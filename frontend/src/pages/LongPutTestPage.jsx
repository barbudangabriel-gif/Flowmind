/**
 * Long Put Test Page
 * 
 * Test simplu pentru Long Put cu gradient corect (bearish)
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import StrategyCardTemplate from '../components/StrategyCardTemplate';

export default function LongPutTestPage() {
  const navigate = useNavigate();

  // Long Put strategy data
  const longPutStrategy = {
    name: 'Long Put',
    category: 'bearish', // CRITICAL: triggers inverted gradients
    legs: [
      { side: 'BUY', kind: 'PUT', strike: '200', qty: 1 }
    ],
    returnPercent: 120,
    chancePercent: 38,
    profit: 15000,
    risk: 2500,
    collateral: 0,
  };

  const handleOpenInBuilder = (strategyData) => {
    console.log('Opening Long Put in Builder...', strategyData);
    navigate('/builder', {
      state: {
        selectedStrategy: {
          strategyId: 'long_put',
          strategyName: strategyData.name,
          currentPrice: 221.09,
          strikes: [200],
          premiums: [2500],
          volatility: 0.348,
          daysToExpiry: 420,
        },
        openBuildTab: true,
        openGraphView: true,
      }
    });
  };

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Long Put - Bearish Strategy Test</h1>
          <p className="text-gray-400">
            Verificare gradient: verde jos-stânga (profit când prețul scade)
          </p>
        </div>

        {/* Strategy Card */}
        <div className="max-w-md mx-auto">
          <StrategyCardTemplate 
            strategy={longPutStrategy}
            onClick={() => handleOpenInBuilder(longPutStrategy)}
          />
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-slate-800 rounded-lg p-6 max-w-2xl mx-auto">
          <h2 className="text-xl font-bold text-white mb-4">Expected Behavior:</h2>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Strike:</strong> $200 (vertical line)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Premium:</strong> $2,500 (max risk)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Profit Zone:</strong> GREEN line on LEFT (low prices) with gradient DOWN-LEFT</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Loss Zone:</strong> RED line on RIGHT (high prices) flat at -$2,500</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Breakeven:</strong> $200 - ($2,500 / 100) = $175</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">→</span>
              <span><strong>Click "Open in Builder"</strong> to test navigation to BuilderV2Page</span>
            </li>
          </ul>
        </div>

        {/* P&L Calculation Reference */}
        <div className="mt-6 bg-slate-800 rounded-lg p-6 max-w-2xl mx-auto">
          <h2 className="text-xl font-bold text-white mb-4">P&L Calculation:</h2>
          <div className="space-y-2 text-gray-300 font-mono text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-gray-400 mb-1">Price $160 (well below strike):</div>
                <div className="text-green-400">P&L = ($200 - $160) × 100 - $2,500 = +$1,500</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Price $175 (breakeven):</div>
                <div className="text-white">P&L = ($200 - $175) × 100 - $2,500 = $0</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Price $200 (at strike):</div>
                <div className="text-red-400">P&L = ($200 - $200) × 100 - $2,500 = -$2,500</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Price $240 (well above strike):</div>
                <div className="text-red-400">P&L = max(0, $200 - $240) × 100 - $2,500 = -$2,500</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

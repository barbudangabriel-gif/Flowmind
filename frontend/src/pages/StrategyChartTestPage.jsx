/**
 * StrategyChartTestPage - Visual comparison of StrategyChart component
 * 
 * Shows both sizes (card + full) for Long Call strategy
 * Compare with BuilderV2Page Build tab to verify identical rendering
 */

import React from 'react';
import StrategyChart from '../components/StrategyChart';

export default function StrategyChartTestPage() {
  // AMZN Long Call parameters (matching BuilderV2Page)
  const params = {
    strategyId: 'long_call',
    currentPrice: 221.09,
    strikes: { strike: 220 },
    premiums: { premium: 3787.50 },
    volatility: 0.348,
    daysToExpiry: 420
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a] text-white p-8">
      <h1 className="text-3xl font-bold mb-8">StrategyChart Component Test</h1>

      {/* Full Size Chart */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Full Size (1000x400) - Build Tab</h2>
        <div className="w-[60%] mx-auto">
          <StrategyChart 
            {...params}
            size="full"
            showProbability={false}
          />
        </div>
        <div className="mt-4 text-center text-gray-400 text-sm">
          Compare with BuilderV2Page Build tab Long Call chart
        </div>
      </div>

      {/* Card Size Chart */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Card Size (360x180) - Optimize Tab</h2>
        <div className="flex justify-center gap-6">
          <div className="w-[360px]">
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-2">Long Call</h3>
              <StrategyChart 
                {...params}
                size="card"
                showProbability={false}
              />
              <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                <div>
                  <div className="text-gray-400">Max Profit</div>
                  <div className="text-white font-semibold">Unlimited</div>
                </div>
                <div>
                  <div className="text-gray-400">Max Loss</div>
                  <div className="text-white font-semibold">-$3,788</div>
                </div>
                <div>
                  <div className="text-gray-400">Net Cost</div>
                  <div className="text-white font-semibold">$3,788</div>
                </div>
                <div>
                  <div className="text-gray-400">Breakeven</div>
                  <div className="text-white font-semibold">$259.33</div>
                </div>
              </div>
              <button className="w-full mt-4 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-semibold transition-colors">
                Open in Builder
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bull Call Spread Test */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Bull Call Spread (Card Size)</h2>
        <div className="flex justify-center gap-6">
          <div className="w-[360px]">
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-2">Bull Call Spread</h3>
              <StrategyChart 
                strategyId="bull_call_spread"
                currentPrice={250}
                strikes={{ lower: 240, higher: 260 }}
                premiums={{ lower: 1500, higher: 800 }}
                volatility={0.30}
                daysToExpiry={30}
                size="card"
                showProbability={false}
              />
              <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                <div>
                  <div className="text-gray-400">Max Profit</div>
                  <div className="text-white font-semibold">$1,300</div>
                </div>
                <div>
                  <div className="text-gray-400">Max Loss</div>
                  <div className="text-white font-semibold">-$700</div>
                </div>
                <div>
                  <div className="text-gray-400">Net Debit</div>
                  <div className="text-white font-semibold">$700</div>
                </div>
                <div>
                  <div className="text-gray-400">Breakeven</div>
                  <div className="text-white font-semibold">$247.00</div>
                </div>
              </div>
              <div className="mt-3 space-y-1">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-green-400">BUY</span>
                  <span className="text-white">1x</span>
                  <span className="text-white">CALL</span>
                  <span className="text-cyan-400">$240</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-red-400">SELL</span>
                  <span className="text-white">1x</span>
                  <span className="text-white">CALL</span>
                  <span className="text-cyan-400">$260</span>
                </div>
              </div>
              <button className="w-full mt-4 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-semibold transition-colors">
                Open in Builder
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Side-by-side comparison */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Side-by-Side: 4 Strategies (Card Size)</h2>
        <div className="grid grid-cols-4 gap-4">
          {[
            { id: 'long_call', name: 'Long Call', strikes: { strike: 220 }, premiums: { premium: 3787 } },
            { id: 'bull_call_spread', name: 'Bull Spread', strikes: { lower: 240, higher: 260 }, premiums: { lower: 1500, higher: 800 } },
            { id: 'long_put', name: 'Long Put', strikes: { strike: 240 }, premiums: { premium: 1200 } },
            { id: 'bear_put_spread', name: 'Bear Spread', strikes: { higher: 260, lower: 240 }, premiums: { higher: 1500, lower: 800 } },
          ].map((strategy) => (
            <div key={strategy.id} className="bg-slate-800 rounded-lg p-3">
              <h3 className="text-sm font-semibold text-white mb-2">{strategy.name}</h3>
              <StrategyChart 
                strategyId={strategy.id}
                currentPrice={250}
                strikes={strategy.strikes}
                premiums={strategy.premiums}
                volatility={0.30}
                daysToExpiry={30}
                size="card"
                showProbability={false}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Metrics Verification */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Expected Metrics (AMZN Long Call)</h2>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-400 mb-1">Net Cost</div>
            <div className="text-white font-semibold">$3,787.50</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">Max Loss</div>
            <div className="text-white font-semibold">$3,787.50</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">Max Profit</div>
            <div className="text-white font-semibold">Unlimited</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">Breakeven</div>
            <div className="text-white font-semibold">$259.33</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">Chance of Profit</div>
            <div className="text-white font-semibold">~34%</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">Strike</div>
            <div className="text-white font-semibold">$220</div>
          </div>
        </div>
        <div className="mt-4 text-gray-400 text-xs">
          ✅ Verify chart matches these metrics<br/>
          ✅ Breakeven line at $259.33<br/>
          ✅ Profit (cyan) above breakeven, Loss (red) below<br/>
          ✅ Tooltip shows correct P&L at cursor position
        </div>
      </div>
    </div>
  );
}

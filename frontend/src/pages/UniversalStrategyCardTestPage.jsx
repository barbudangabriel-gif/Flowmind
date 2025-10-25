/**
 * UniversalStrategyCard Test Page
 * 
 * Testing StrategyCardTemplate cu "Open in Builder" button
 * Navigare la BuilderV2Page cu tab Build + graph activ
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import StrategyCardTemplate from '../components/StrategyCardTemplate';

export default function UniversalStrategyCardTestPage() {
  const navigate = useNavigate();

  // Long Call strategy data
  const longCallStrategy = {
    name: 'Long Call',
    category: 'bullish',
    legs: [
      { side: 'BUY', kind: 'CALL', strike: '220', qty: 1 }
    ],
    returnPercent: 90,
    chancePercent: 34,
    profit: 10000,
    risk: 3787.50,
    collateral: 0,
  };

  // Bull Call Spread strategy data
  const bullCallSpreadStrategy = {
    name: 'Bull Call Spread',
    category: 'bullish',
    legs: [
      { side: 'BUY', kind: 'CALL', strike: '220', qty: 1 },
      { side: 'SELL', kind: 'CALL', strike: '240', qty: 1 }
    ],
    returnPercent: 65,
    chancePercent: 52,
    profit: 1300,
    risk: 700,
    collateral: 0,
  };

  // Long Put strategy data
  const longPutStrategy = {
    name: 'Long Put',
    category: 'bearish',
    legs: [
      { side: 'BUY', kind: 'PUT', strike: '200', qty: 1 }
    ],
    returnPercent: 120,
    chancePercent: 38,
    profit: 15000,
    risk: 2500,
    collateral: 0,
  };

  // Bear Call Spread strategy data
  const bearCallSpreadStrategy = {
    name: 'Bear Call Spread',
    category: 'bearish',
    legs: [
      { side: 'SELL', kind: 'CALL', strike: '220', qty: 1 },
      { side: 'BUY', kind: 'CALL', strike: '240', qty: 1 }
    ],
    returnPercent: 85,
    chancePercent: 60,
    profit: 1300,
    risk: 700,
    collateral: 0,
  };

  const handleOpenInBuilder = (strategyData) => {
    console.log('Opening strategy in Builder...', strategyData);
    navigate('/builder', {
      state: {
        selectedStrategy: {
          strategyId: strategyData.strategyId,
          strategyName: strategyData.name,
          currentPrice: 221.09,
          strikes: strategyData.strikes,
          premiums: strategyData.premiums,
          volatility: 0.348,
          daysToExpiry: 420,
          symbol: 'AMZN'
        },
        openBuildTab: true,
        openGraphView: true
      }
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a] text-white p-8">
      <h1 className="text-3xl font-bold mb-2">Strategy Card Template Test</h1>
      <p className="text-gray-400 mb-8">StrategyCardTemplate - 4 strategies cu "Open in Builder"</p>

      {/* Grid of 4 strategy cards - increased gap for 380px cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-[1600px] mx-auto mb-12">
        {/* Long Call */}
        <StrategyCardTemplate
          strategy={{
            ...longCallStrategy,
            strategyId: 'long_call',
            strikes: { strike: 220 },
            premiums: { premium: 3787.50 }
          }}
          onClick={() => handleOpenInBuilder({
            strategyId: 'long_call',
            name: 'Long Call',
            strikes: { strike: 220 },
            premiums: { premium: 3787.50 }
          })}
        />

        {/* Bull Call Spread */}
        <StrategyCardTemplate
          strategy={{
            ...bullCallSpreadStrategy,
            strategyId: 'bull_call_spread',
            strikes: { lower: 220, higher: 240 },
            premiums: { lower: 3787.50, higher: 2487.50 }
          }}
          onClick={() => handleOpenInBuilder({
            strategyId: 'bull_call_spread',
            name: 'Bull Call Spread',
            strikes: { lower: 220, higher: 240 },
            premiums: { lower: 3787.50, higher: 2487.50 }
          })}
        />

        {/* Long Put */}
        <StrategyCardTemplate
          strategy={{
            ...longPutStrategy,
            strategyId: 'long_put',
            strikes: { strike: 200 },
            premiums: { premium: 2500 }
          }}
          onClick={() => handleOpenInBuilder({
            strategyId: 'long_put',
            name: 'Long Put',
            strikes: { strike: 200 },
            premiums: { premium: 2500 }
          })}
        />

        {/* Bear Call Spread */}
        <StrategyCardTemplate
          strategy={{
            ...bearCallSpreadStrategy,
            strategyId: 'bear_call_spread',
            strikes: { lower: 220, higher: 240 },
            premiums: { lower: 3787.50, higher: 2487.50 }
          }}
          onClick={() => handleOpenInBuilder({
            strategyId: 'bear_call_spread',
            name: 'Bear Call Spread',
            strikes: { lower: 220, higher: 240 },
            premiums: { lower: 3787.50, higher: 2487.50 }
          })}
        />
      </div>

      {/* Features Checklist */}
      <div className="bg-slate-800 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Navigation Flow</h2>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>Click card → Navigate to /builder</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>State: selectedStrategy (Long Call or Bull Call Spread)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>State: openBuildTab: true</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>State: openGraphView: true</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>BuilderV2Page receives state → Opens Build tab → Shows Graph view</span>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-2 text-cyan-400">Testing Instructions</h2>
        <ol className="space-y-2 text-sm list-decimal list-inside">
          <li>Click anywhere on Long Call or Bull Call Spread card</li>
          <li>Should navigate to /builder page</li>
          <li>BuilderV2Page should open Build tab (not Optimize/Strategy/Flow)</li>
          <li>Within Build tab, Graph view should be active (not Table)</li>
          <li>Strategy data (AMZN, $221.09, strikes) should be loaded</li>
          <li>Chart should display with all metrics visible</li>
          <li>Long Call: Single leg (Buy 220C)</li>
          <li>Bull Call Spread: Two legs (Buy 220C, Sell 240C)</li>
          <li>Long Put: Single leg (Buy 200P) - inverse profit curve</li>
          <li>Bear Call Spread: Two legs (Sell 220C, Buy 240C) - credit spread</li>
        </ol>
      </div>
    </div>
  );
}

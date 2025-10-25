import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Plus, RefreshCw } from 'lucide-react';

/**
 * StrategyCardHardcoded - Clonă exactă a cardului hardcodat din BuilderV2Page.jsx (lines 580-720)
 * Structură: Header + Ticker + Expiration Timeline + Strike Scale + Metrics Row
 */
const StrategyCardHardcoded = () => {
  const [selectedDate, setSelectedDate] = useState(18);

  // Data hardcodată din BuilderV2Page
  const strategyData = { strategyName: "Long Call" };
  const symbol = "AMZN";
  const currentPrice = "221.09";
  const priceChangePercent = "1.18";
  const priceChange = "2.58";

  const months = [
    { name: "Oct", dates: [24, 31] },
    { name: "Nov", dates: [7, 14, 21] },
    { name: "Dec", dates: [18] },
  ];

  const strikes = [200, 205, 210, 215, 220, 225, 230, 235, 240];

  return (
    <div className="w-full bg-slate-900 text-white p-6">
      {/* Header with Action Buttons - aligned with 60% container */}
      <div className="w-[52%] mx-auto mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold">{strategyData.strategyName}</h1>
            <button className="text-gray-400 hover:text-gray-300">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <Plus className="w-4 h-4" />
              Add
            </button>
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              Positions (1)
            </button>
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              Save Trade
            </button>
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <RefreshCw className="w-4 h-4" />
              Historical Chart
            </button>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-2 py-1 border border-gray-600 rounded text-sm">{symbol}</div>
          <div className="text-2xl font-semibold text-white">${currentPrice}</div>
          <div className="text-emerald-400 text-sm">
            <div className="text-white">+{priceChangePercent}%</div>
            <div className="text-white">+${priceChange}</div>
          </div>
          <div className="text-gray-400 text-sm flex items-center gap-1">
            Real-time
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Chart Section - 60% width centered */}
      <div className="w-[52%] mx-auto">
        {/* Expiration Timeline */}
        <div className="mb-6">
          <div className="text-sm mb-3">EXPIRATION: 1.2y</div>
          <div className="relative h-20 bg-gray-900/50 rounded overflow-x-auto custom-scrollbar">
            <div className="flex items-center justify-between px-2 h-full">
              {months.map((month, idx) => (
                <div key={idx} className="flex flex-col items-center justify-center min-w-fit">
                  <div className="text-xs text-white mb-2 whitespace-nowrap">{month.name}</div>
                  <div className="flex gap-1.5">
                    {month.dates.map((date) => (
                      <button
                        key={date}
                        onClick={() => setSelectedDate(date)}
                        className={`px-4 py-1.5 rounded text-sm transition-colors ${
                          selectedDate === date && month.name === "Dec"
                            ? "bg-cyan-500 text-white"
                            : "bg-gray-800 text-white hover:bg-gray-700"
                        }`}
                      >
                        {date}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Strike Price Scale */}
        <div className="mb-4">
          <div className="text-sm mb-2">STRIKE:</div>
          <div className="relative h-12 bg-gray-900/50 rounded">
            <div className="absolute inset-0 flex items-center justify-between px-2">
              {strikes.map((strike, idx) => (
                <div key={idx} className="relative flex flex-col items-center">
                  <div className="h-2 w-px bg-gray-600"></div>
                  {idx % 2 === 0 && <div className="text-[10px] text-white mt-1">{strike}</div>}
                  {strike === 220 && (
                    <div className="absolute -top-8 bg-emerald-500 text-white px-2 py-1 rounded text-xs font-semibold">
                      220C
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Metrics Row - Compact Layout */}
        <div className="flex items-center gap-4 mb-6">
          <button className="text-gray-500 hover:text-gray-300 flex-shrink-0">
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex-1 grid grid-cols-5 gap-3">
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">NET DEBIT:</div>
              <div className="text-sm font-semibold text-white">-$3,787.50</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">MAX LOSS:</div>
              <div className="text-sm font-semibold text-white">-$3,787.50</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">MAX PROFIT:</div>
              <div className="text-sm font-semibold text-white">Infinite</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">CHANCE:</div>
              <div className="text-sm font-semibold text-white">34%</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">BREAKEVEN:</div>
              <div className="text-sm font-semibold text-white">$257.68 (+17%)</div>
            </div>
          </div>
          <button className="text-gray-500 hover:text-gray-300 flex-shrink-0">
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default StrategyCardHardcoded;

/**
 * LiveDarkPool Component
 * 
 * Real-time dark pool trades from Unusual Whales.
 * Shows institutional block trades executed off-exchange.
 * 
 * Usage:
 * ```jsx
 * <LiveDarkPool maxItems={50} />
 * ```
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocketContext } from '../context/WebSocketContext';
import ConnectionStatus from './ConnectionStatus';

const LiveDarkPool = ({ maxItems = 50, className = '' }) => {
  const navigate = useNavigate();
  const { subscribe, CHANNELS } = useWebSocketContext();
  
  const [trades, setTrades] = useState([]);

  // Format currency
  const formatValue = (value) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  };

  // Format time
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  // Handle new message
  const handleMessage = useCallback((data) => {
    // Expected: { symbol, quantity, price, value, exchange, timestamp }
    const newItem = {
      ...data,
      id: `${Date.now()}-${Math.random()}`,
      timestamp: data.timestamp || new Date().toISOString()
    };

    setTrades(prev => [newItem, ...prev].slice(0, maxItems));
  }, [maxItems]);

  // Subscribe to dark-pool channel
  useEffect(() => {
    const unsubscribe = subscribe(CHANNELS.DARK_POOL, handleMessage);
    return unsubscribe;
  }, [subscribe, CHANNELS.DARK_POOL, handleMessage]);

  // Navigate to Builder
  const handleSymbolClick = (symbol) => {
    navigate(`/builder?symbol=${symbol}`);
  };

  return (
    <div className={`flex flex-col h-full bg-slate-900 rounded-lg border border-slate-700 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-bold text-white">🕶️ Dark Pool</h3>
          <ConnectionStatus channel={CHANNELS.DARK_POOL} compact />
        </div>

        <button
          onClick={() => setTrades([])}
          className="px-3 py-1.5 rounded text-xs font-semibold bg-slate-800 text-gray-400 hover:text-white hover:bg-slate-700"
        >
          🗑️ Clear
        </button>
      </div>

      {/* Trades List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {trades.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">🕶️</div>
              <div>Waiting for dark pool data...</div>
              <div className="text-xs mt-1">Institutional block trades will appear here</div>
            </div>
          </div>
        ) : (
          trades.map((trade) => (
            <div
              key={trade.id}
              className="flex items-center gap-4 p-3 bg-slate-800/50 hover:bg-slate-800 rounded border border-slate-700/30 hover:border-slate-600 transition-all"
            >
              {/* Time */}
              <div className="text-xs text-gray-400 w-20 flex-shrink-0">
                {formatTime(trade.timestamp)}
              </div>

              {/* Symbol (clickable) */}
              <button
                onClick={() => handleSymbolClick(trade.symbol)}
                className="text-sm font-bold text-purple-400 hover:text-purple-300 hover:underline w-16 flex-shrink-0"
              >
                {trade.symbol}
              </button>

              {/* Quantity */}
              <div className="text-xs text-gray-300 flex-shrink-0">
                <span className="text-gray-500">Qty:</span> {trade.quantity.toLocaleString()}
              </div>

              {/* Price */}
              <div className="text-sm text-white font-semibold flex-shrink-0">
                @${trade.price.toFixed(2)}
              </div>

              {/* Value */}
              <div className="text-sm font-bold text-purple-400 ml-auto flex-shrink-0">
                {formatValue(trade.value)}
              </div>

              {/* Exchange */}
              {trade.exchange && (
                <div className="text-xs px-2 py-0.5 rounded bg-slate-700 text-gray-300 flex-shrink-0">
                  {trade.exchange}
                </div>
              )}

              {/* Large block indicator */}
              {trade.value >= 1000000 && (
                <div className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-semibold flex-shrink-0">
                  🐋 WHALE
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default LiveDarkPool;

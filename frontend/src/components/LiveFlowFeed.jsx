/**
 * LiveFlowFeed Component
 * 
 * Real-time options flow alerts from Unusual Whales.
 * Displays live trades with premium amounts, sentiment, and tickers.
 * 
 * Features:
 * - Auto-scroll to latest trades
 * - Audio alerts for high-premium trades
 * - Click ticker to navigate to Builder
 * - Premium color coding
 * - Pause/resume streaming
 * 
 * Usage:
 * ```jsx
 * <LiveFlowFeed maxItems={100} />
 * ```
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocketContext } from '../context/WebSocketContext';
import ConnectionStatus from './ConnectionStatus';

const LiveFlowFeed = ({ 
  maxItems = 100, 
  audioAlerts = true,
  premiumThreshold = 500000, // $500K for audio alerts
  className = '' 
}) => {
  const navigate = useNavigate();
  const { subscribe, CHANNELS } = useWebSocketContext();
  
  // State
  const [flowItems, setFlowItems] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [stats, setStats] = useState({ total: 0, bullish: 0, bearish: 0, avgPremium: 0 });
  const [filter, setFilter] = useState('all'); // 'all', 'bullish', 'bearish'
  
  // Refs
  const feedRef = useRef(null);
  const audioRef = useRef(null);
  const pausedMessagesRef = useRef([]);

  // Format currency
  const formatPremium = (value) => {
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

  // Determine sentiment from trade data
  const getSentiment = (trade) => {
    // Logic: BUY calls = bullish, BUY puts = bearish, SELL calls = bearish, SELL puts = bullish
    if (trade.kind === 'CALL') {
      return trade.side === 'BUY' ? 'bullish' : 'bearish';
    } else {
      return trade.side === 'BUY' ? 'bearish' : 'bullish';
    }
  };

  // Get premium color based on sentiment
  const getPremiumColor = (sentiment, premium) => {
    if (premium >= premiumThreshold) {
      return sentiment === 'bullish' ? 'text-green-400 font-bold' : 'text-red-400 font-bold';
    }
    return sentiment === 'bullish' ? 'text-green-500' : 'text-red-500';
  };

  // Get sentiment badge
  const getSentimentBadge = (sentiment) => {
    if (sentiment === 'bullish') {
      return <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400 font-semibold">🐂 BULL</span>;
    }
    return <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-semibold">🐻 BEAR</span>;
  };

  // Play audio alert
  const playAlert = useCallback(() => {
    if (audioAlerts && audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(err => console.log('Audio play failed:', err));
    }
  }, [audioAlerts]);

  // Handle new message
  const handleMessage = useCallback((data) => {
    // Expected format: { symbol, strike, expiry, kind, side, quantity, price, premium, timestamp, is_sweep }
    const newItem = {
      ...data,
      id: `${Date.now()}-${Math.random()}`,
      sentiment: getSentiment(data),
      timestamp: data.timestamp || new Date().toISOString()
    };

    if (isPaused) {
      // Queue messages while paused
      pausedMessagesRef.current.push(newItem);
    } else {
      // Add to feed
      setFlowItems(prev => {
        const updated = [newItem, ...prev].slice(0, maxItems);
        
        // Update stats
        const totalPremium = updated.reduce((sum, item) => sum + (item.premium || 0), 0);
        const bullCount = updated.filter(item => item.sentiment === 'bullish').length;
        const bearCount = updated.filter(item => item.sentiment === 'bearish').length;
        
        setStats({
          total: updated.length,
          bullish: bullCount,
          bearish: bearCount,
          avgPremium: totalPremium / updated.length || 0
        });

        return updated;
      });

      // Play alert for high-premium trades
      if (newItem.premium >= premiumThreshold) {
        playAlert();
      }

      // Auto-scroll to top
      if (feedRef.current && !isPaused) {
        feedRef.current.scrollTop = 0;
      }
    }
  }, [isPaused, maxItems, premiumThreshold, playAlert]);

  // Subscribe to flow channel
  useEffect(() => {
    const unsubscribe = subscribe(CHANNELS.FLOW, handleMessage);
    return unsubscribe;
  }, [subscribe, CHANNELS.FLOW, handleMessage]);

  // Resume handler
  const handleResume = () => {
    setIsPaused(false);
    
    // Process queued messages
    if (pausedMessagesRef.current.length > 0) {
      setFlowItems(prev => {
        const combined = [...pausedMessagesRef.current, ...prev].slice(0, maxItems);
        pausedMessagesRef.current = [];
        return combined;
      });
    }
  };

  // Navigate to Builder
  const handleTickerClick = (item) => {
    navigate(`/builder?symbol=${item.symbol}&strike=${item.strike}&expiry=${item.expiry}&type=${item.kind.toLowerCase()}`);
  };

  // Filter items
  const filteredItems = filter === 'all' 
    ? flowItems 
    : flowItems.filter(item => item.sentiment === filter);

  return (
    <div className={`flex flex-col h-full bg-slate-900 rounded-lg border border-slate-700 ${className}`}>
      {/* Audio element for alerts */}
      <audio ref={audioRef} preload="auto">
        <source src="/alert.mp3" type="audio/mpeg" />
        {/* Fallback: beep sound using data URI */}
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBCiJ0vbTgjMGHm7A7+OZVRE" type="audio/wav" />
      </audio>

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-bold text-white">📡 Live Flow</h3>
          <ConnectionStatus channel={CHANNELS.FLOW} compact />
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Pause/Resume */}
          <button
            onClick={() => isPaused ? handleResume() : setIsPaused(true)}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
              isPaused 
                ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                : 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
            }`}
          >
            {isPaused ? '▶️ Resume' : '⏸️ Pause'}
          </button>

          {/* Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1.5 rounded text-xs font-semibold bg-slate-800 text-white border border-slate-600 hover:border-slate-500"
          >
            <option value="all">All Trades</option>
            <option value="bullish">🐂 Bullish Only</option>
            <option value="bearish">🐻 Bearish Only</option>
          </select>

          {/* Clear */}
          <button
            onClick={() => setFlowItems([])}
            className="px-3 py-1.5 rounded text-xs font-semibold bg-slate-800 text-gray-400 hover:text-white hover:bg-slate-700"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="flex items-center gap-6 px-4 py-2 bg-slate-800/50 border-b border-slate-700/30 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Total:</span>
          <span className="text-white font-semibold">{stats.total}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">🐂 Bull:</span>
          <span className="text-green-400 font-semibold">{stats.bullish}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">🐻 Bear:</span>
          <span className="text-red-400 font-semibold">{stats.bearish}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Avg Premium:</span>
          <span className="text-blue-400 font-semibold">{formatPremium(stats.avgPremium)}</span>
        </div>
      </div>

      {/* Feed Items */}
      <div 
        ref={feedRef}
        className="flex-1 overflow-y-auto p-4 space-y-2"
      >
        {filteredItems.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">📡</div>
              <div>Waiting for live flow data...</div>
              <div className="text-xs mt-1">Trades will appear here in real-time</div>
            </div>
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-4 p-3 bg-slate-800/50 hover:bg-slate-800 rounded border border-slate-700/30 hover:border-slate-600 transition-all"
            >
              {/* Time */}
              <div className="text-xs text-gray-400 w-20 flex-shrink-0">
                {formatTime(item.timestamp)}
              </div>

              {/* Ticker (clickable) */}
              <button
                onClick={() => handleTickerClick(item)}
                className="text-sm font-bold text-blue-400 hover:text-blue-300 hover:underline w-16 text-left flex-shrink-0"
              >
                {item.symbol}
              </button>

              {/* Sentiment */}
              <div className="flex-shrink-0">
                {getSentimentBadge(item.sentiment)}
              </div>

              {/* Strike & Expiry */}
              <div className="text-xs text-gray-300 flex-shrink-0">
                <span className="font-semibold">${item.strike}</span>
                <span className="text-gray-500 mx-1">•</span>
                <span>{item.expiry}</span>
              </div>

              {/* Type */}
              <div className={`text-xs font-semibold px-2 py-0.5 rounded flex-shrink-0 ${
                item.kind === 'CALL' 
                  ? 'bg-blue-500/20 text-blue-400' 
                  : 'bg-purple-500/20 text-purple-400'
              }`}>
                {item.kind}
              </div>

              {/* Side */}
              <div className={`text-xs font-semibold px-2 py-0.5 rounded flex-shrink-0 ${
                item.side === 'BUY' 
                  ? 'bg-green-500/20 text-green-400' 
                  : 'bg-red-500/20 text-red-400'
              }`}>
                {item.side}
              </div>

              {/* Quantity */}
              <div className="text-xs text-gray-400 flex-shrink-0">
                x{item.quantity}
              </div>

              {/* Premium */}
              <div className={`text-sm font-bold ml-auto flex-shrink-0 ${getPremiumColor(item.sentiment, item.premium)}`}>
                {formatPremium(item.premium)}
              </div>

              {/* Sweep indicator */}
              {item.is_sweep && (
                <div className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 font-semibold flex-shrink-0">
                  🚨 SWEEP
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Paused Overlay */}
      {isPaused && pausedMessagesRef.current.length > 0 && (
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-600 text-center">
            <div className="text-2xl mb-2">⏸️</div>
            <div className="text-white font-semibold mb-2">Feed Paused</div>
            <div className="text-sm text-gray-400 mb-4">
              {pausedMessagesRef.current.length} new trades queued
            </div>
            <button
              onClick={handleResume}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded transition-colors"
            >
              Resume & Load New Trades
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveFlowFeed;

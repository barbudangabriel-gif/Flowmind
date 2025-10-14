import React, { useState, useEffect, useMemo } from 'react';
import useWebSocket from '../hooks/useWebSocket';

/**
 * LiveOffLitTradesFeed - Dark pool (off-exchange) trades feed
 * 
 * Displays real-time dark pool executions - large institutional block trades
 * executed away from public exchanges. Smart money tracking.
 * 
 * @param {Object} props
 * @param {string} props.ticker - Stock symbol (e.g., "TSLA", "SPY")
 * @param {number} props.maxTrades - Maximum trades to display (default: 50)
 * @param {number} props.minSize - Minimum size filter (default: 0)
 */
export default function LiveOffLitTradesFeed({ 
    ticker = 'SPY', 
    maxTrades = 50,
    minSize = 0
}) {
    const [trades, setTrades] = useState([]);
    const [stats, setStats] = useState({
        totalVolume: 0,
        totalValue: 0,
        tradeCount: 0,
        blockCount: 0,
        avgSize: 0,
        avgPrice: 0,
        venues: {}
    });
    
    const wsUrl = `/api/stream/ws/off-lit-trades/${ticker.toUpperCase()}`;
    const { messages, status, error } = useWebSocket(wsUrl);

    // Process incoming trades
    useEffect(() => {
        if (messages.length > 0) {
            const latestMessage = messages[messages.length - 1];
            if (latestMessage?.data) {
                const trade = latestMessage.data;
                
                // Filter by minimum size
                if (minSize > 0 && (trade.size || 0) < minSize) {
                    return;
                }
                
                setTrades(prev => {
                    const updated = [trade, ...prev].slice(0, maxTrades);
                    return updated;
                });
                
                // Update stats
                setStats(prev => {
                    const newVolume = prev.totalVolume + (trade.size || 0);
                    const newValue = prev.totalValue + (trade.notional || ((trade.price || 0) * (trade.size || 0)));
                    const newCount = prev.tradeCount + 1;
                    const isBlock = trade.is_block || (trade.size >= 10000);
                    const newBlockCount = prev.blockCount + (isBlock ? 1 : 0);
                    
                    const venues = { ...prev.venues };
                    const venue = trade.venue_name || trade.venue || 'UNKNOWN';
                    venues[venue] = (venues[venue] || 0) + 1;
                    
                    return {
                        totalVolume: newVolume,
                        totalValue: newValue,
                        tradeCount: newCount,
                        blockCount: newBlockCount,
                        avgSize: newCount > 0 ? newVolume / newCount : 0,
                        avgPrice: newVolume > 0 ? newValue / newVolume : 0,
                        venues
                    };
                });
            }
        }
    }, [messages, maxTrades, minSize]);

    // Format numbers
    const formatNumber = (num) => {
        if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
        if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
        if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
        return num.toFixed(0);
    };

    // Venue color mapping (major dark pools)
    const getVenueColor = (venue) => {
        if (!venue) return 'bg-gray-700';
        const venueLower = venue.toLowerCase();
        
        if (venueLower.includes('ubs')) return 'bg-red-700';
        if (venueLower.includes('morgan') || venueLower.includes('ms')) return 'bg-blue-700';
        if (venueLower.includes('citadel') || venueLower.includes('level')) return 'bg-orange-700';
        if (venueLower.includes('goldman') || venueLower.includes('sigma')) return 'bg-purple-700';
        if (venueLower.includes('liquidnet')) return 'bg-green-700';
        if (venueLower.includes('bids')) return 'bg-cyan-700';
        
        return 'bg-gray-700';
    };

    // Size category
    const getSizeCategory = (size) => {
        if (size >= 100000) return { label: 'MEGA', color: 'text-red-400' };
        if (size >= 50000) return { label: 'HUGE', color: 'text-orange-400' };
        if (size >= 10000) return { label: 'BLOCK', color: 'text-yellow-400' };
        if (size >= 5000) return { label: 'LARGE', color: 'text-green-400' };
        return { label: 'NORMAL', color: 'text-gray-400' };
    };

    // Status indicator
    const StatusIndicator = () => (
        <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
                status === 'connected' ? 'bg-green-500' : 
                status === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
                'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-400">
                {status === 'connected' ? 'Live' : 
                 status === 'connecting' ? 'Connecting...' : 
                 'Disconnected'}
            </span>
        </div>
    );

    // Top venues
    const topVenues = useMemo(() => {
        return Object.entries(stats.venues)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5);
    }, [stats.venues]);

    // Dark pool percentage (rough estimate)
    const darkPoolPercentage = useMemo(() => {
        // Assume ~30% of volume is dark pool (industry average)
        // This is illustrative - would need lit volume for accurate calculation
        return stats.totalVolume > 0 ? 30 : 0;
    }, [stats.totalVolume]);

    return (
        <div className="bg-gray-900 rounded-lg shadow-lg p-6 text-white">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold flex items-center space-x-2">
                        <span>🕶️ Dark Pool Trades</span>
                        <span className="text-purple-400">{ticker}</span>
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">
                        Off-exchange institutional executions
                    </p>
                </div>
                <StatusIndicator />
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <div className="bg-gray-800 rounded p-4">
                    <div className="text-gray-400 text-xs uppercase mb-1">Total Volume</div>
                    <div className="text-2xl font-bold text-purple-400">
                        {formatNumber(stats.totalVolume)}
                    </div>
                </div>
                <div className="bg-gray-800 rounded p-4">
                    <div className="text-gray-400 text-xs uppercase mb-1">Total Value</div>
                    <div className="text-2xl font-bold text-blue-400">
                        ${formatNumber(stats.totalValue)}
                    </div>
                </div>
                <div className="bg-gray-800 rounded p-4">
                    <div className="text-gray-400 text-xs uppercase mb-1">Trade Count</div>
                    <div className="text-2xl font-bold text-green-400">
                        {formatNumber(stats.tradeCount)}
                    </div>
                </div>
                <div className="bg-gray-800 rounded p-4">
                    <div className="text-gray-400 text-xs uppercase mb-1">Block Trades</div>
                    <div className="text-2xl font-bold text-yellow-400">
                        {formatNumber(stats.blockCount)}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                        {stats.tradeCount > 0 ? ((stats.blockCount / stats.tradeCount) * 100).toFixed(1) : 0}%
                    </div>
                </div>
                <div className="bg-gray-800 rounded p-4">
                    <div className="text-gray-400 text-xs uppercase mb-1">Avg Size</div>
                    <div className="text-2xl font-bold text-cyan-400">
                        {formatNumber(stats.avgSize)}
                    </div>
                </div>
            </div>

            {/* Top Dark Pools */}
            {topVenues.length > 0 && (
                <div className="mb-6">
                    <h3 className="text-sm font-semibold text-gray-400 mb-3">Top Dark Pools</h3>
                    <div className="flex flex-wrap gap-2">
                        {topVenues.map(([venue, count]) => (
                            <div 
                                key={venue}
                                className={`px-3 py-1 rounded-full text-sm font-medium ${getVenueColor(venue)}`}
                            >
                                {venue}: {count}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Dark Pool Indicator */}
            {stats.totalVolume > 0 && (
                <div className="mb-6 bg-purple-900/20 border border-purple-700 rounded p-4">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Estimated Dark Pool %</span>
                        <span className="text-lg font-bold text-purple-400">{darkPoolPercentage}%</span>
                    </div>
                    <div className="mt-2 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-purple-600 transition-all"
                            style={{ width: `${darkPoolPercentage}%` }}
                        ></div>
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="bg-red-900/20 border border-red-700 rounded p-4 mb-4">
                    <p className="text-red-400 text-sm">{error}</p>
                </div>
            )}

            {/* Waiting State */}
            {status === 'connected' && trades.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <p className="text-lg mb-2">🔍 Waiting for dark pool trades...</p>
                    <p className="text-sm">Institutional blocks will appear here</p>
                </div>
            )}

            {/* Trades Table */}
            {trades.length > 0 && (
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                        <thead className="border-b border-gray-700 sticky top-0 bg-gray-900">
                            <tr>
                                <th className="px-3 py-2 text-left text-gray-400">Time</th>
                                <th className="px-3 py-2 text-right text-gray-400">Price</th>
                                <th className="px-3 py-2 text-right text-gray-400">Size</th>
                                <th className="px-3 py-2 text-center text-gray-400">Type</th>
                                <th className="px-3 py-2 text-right text-gray-400">Notional</th>
                                <th className="px-3 py-2 text-center text-gray-400">Venue</th>
                                <th className="px-3 py-2 text-left text-gray-400">Conditions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trades.map((trade, idx) => {
                                const notional = trade.notional || ((trade.price || 0) * (trade.size || 0));
                                const time = trade.timestamp ? 
                                    new Date(trade.timestamp).toLocaleTimeString() : 
                                    '--:--:--';
                                const sizeCategory = getSizeCategory(trade.size || 0);
                                
                                return (
                                    <tr 
                                        key={idx} 
                                        className={`border-b border-gray-800 hover:bg-gray-800 transition-colors ${
                                            trade.is_block || (trade.size >= 10000) ? 'bg-purple-900/10' : ''
                                        }`}
                                    >
                                        <td className="px-3 py-2 text-gray-300 font-mono text-xs">
                                            {time}
                                        </td>
                                        <td className="px-3 py-2 text-right font-semibold">
                                            ${trade.price?.toFixed(2)}
                                        </td>
                                        <td className="px-3 py-2 text-right font-bold text-purple-400">
                                            {formatNumber(trade.size)}
                                        </td>
                                        <td className="px-3 py-2 text-center">
                                            <span className={`text-xs font-bold ${sizeCategory.color}`}>
                                                {sizeCategory.label}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2 text-right text-blue-400 font-semibold">
                                            ${formatNumber(notional)}
                                        </td>
                                        <td className="px-3 py-2 text-center">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                getVenueColor(trade.venue_name || trade.venue)
                                            }`}>
                                                {(trade.venue_name || trade.venue || 'DARK').substring(0, 15)}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2 text-gray-400 text-xs">
                                            {trade.conditions?.join(', ') || 'D'}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Legend */}
            {trades.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-800">
                    <div className="text-xs text-gray-500 space-y-1">
                        <p><strong>Size Types:</strong> MEGA (100K+), HUGE (50K+), BLOCK (10K+), LARGE (5K+)</p>
                        <p><strong>Major Dark Pools:</strong> UBS ATS, MS Pool, Level ATS (Citadel), SIGMA X (Goldman), Liquidnet</p>
                        <p><strong>Conditions:</strong> D = Dark Pool, B = Block Trade, I = Odd Lot, T = Extended Hours</p>
                        <p><strong>Significance:</strong> Large blocks indicate institutional activity - "smart money" positioning</p>
                    </div>
                </div>
            )}
        </div>
    );
}

import React, { useState, useEffect } from 'react';
import { pfClient } from '../services/portfolioClient';

export default function PositionsTable({ portfolioId }) {
  const [positions, setPositions] = useState([]);
  const [realizedPnL, setRealizedPnL] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    if (!portfolioId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const [positionsData, pnlData] = await Promise.all([
        pfClient.getPositions(portfolioId),
        pfClient.getRealizedPnL(portfolioId)
      ]);
      
      setPositions(positionsData);
      setRealizedPnL(pnlData);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [portfolioId]);

  const totalCostBasis = positions.reduce((sum, pos) => sum + pos.cost_basis, 0);
  const totalRealizedPnL = realizedPnL.reduce((sum, pnl) => sum + pnl.realized, 0);

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="text-center text-gray-500">Loading positions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="text-red-800 font-semibold">Error loading positions</div>
        <div className="text-red-600">{error}</div>
        <button 
          onClick={loadData}
          className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Positions */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Current Positions (FIFO)</h3>
          <p className="text-sm text-gray-500 mt-1">
            Calculated using First-In-First-Out accounting method
          </p>
        </div>

        {positions.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No open positions
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="p-3 text-left">Symbol</th>
                    <th className="p-3 text-right">Quantity</th>
                    <th className="p-3 text-right">Avg Cost</th>
                    <th className="p-3 text-right">Cost Basis</th>
                    <th className="p-3 text-right">Market Value</th>
                    <th className="p-3 text-right">Unrealized P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((pos, idx) => (
                    <tr key={pos.symbol || idx} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="p-3">
                        <span className="font-mono font-semibold text-gray-900">
                          {pos.symbol}
                        </span>
                      </td>
                      <td className="p-3 text-right font-mono">
                        {pos.qty.toLocaleString()}
                      </td>
                      <td className="p-3 text-right font-mono">
                        ${pos.avg_cost.toFixed(2)}
                      </td>
                      <td className="p-3 text-right font-mono">
                        ${pos.cost_basis.toFixed(2)}
                      </td>
                      <td className="p-3 text-right font-mono text-gray-500">
                        {pos.market_value ? `$${pos.market_value.toFixed(2)}` : 'N/A'}
                      </td>
                      <td className="p-3 text-right font-mono">
                        {pos.unrealized_pnl ? (
                          <span className={pos.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                            ${pos.unrealized_pnl.toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-gray-500">N/A</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-gray-200 bg-gray-50">
                    <td colSpan="3" className="p-3 text-right font-semibold text-gray-700">
                      Total Cost Basis:
                    </td>
                    <td className="p-3 text-right font-mono font-semibold text-gray-900">
                      ${totalCostBasis.toFixed(2)}
                    </td>
                    <td colSpan="2"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Realized P&L */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Realized P&L by Symbol</h3>
          <p className="text-sm text-gray-500 mt-1">
            Profit/Loss from closed positions using FIFO accounting
          </p>
        </div>

        {realizedPnL.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No realized P&L data yet
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="p-3 text-left">Symbol</th>
                    <th className="p-3 text-right">Realized P&L</th>
                    <th className="p-3 text-right">Closed Trades</th>
                    <th className="p-3 text-right">Avg P&L/Trade</th>
                  </tr>
                </thead>
                <tbody>
                  {realizedPnL.map((pnl, idx) => {
                    const avgPnL = pnl.trades > 0 ? pnl.realized / pnl.trades : 0;
                    
                    return (
                      <tr key={pnl.symbol || idx} className="border-t border-gray-100 hover:bg-gray-50">
                        <td className="p-3">
                          <span className="font-mono font-semibold text-gray-900">
                            {pnl.symbol}
                          </span>
                        </td>
                        <td className="p-3 text-right font-mono font-semibold">
                          <span className={pnl.realized >= 0 ? 'text-green-600' : 'text-red-600'}>
                            ${pnl.realized.toFixed(2)}
                          </span>
                        </td>
                        <td className="p-3 text-right font-mono">
                          {pnl.trades}
                        </td>
                        <td className="p-3 text-right font-mono">
                          <span className={avgPnL >= 0 ? 'text-green-600' : 'text-red-600'}>
                            ${avgPnL.toFixed(2)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-gray-200 bg-gray-50">
                    <td className="p-3 font-semibold text-gray-700">
                      TOTAL
                    </td>
                    <td className="p-3 text-right font-mono font-semibold">
                      <span className={totalRealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}>
                        ${totalRealizedPnL.toFixed(2)}
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono font-semibold">
                      {realizedPnL.reduce((sum, pnl) => sum + pnl.trades, 0)}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
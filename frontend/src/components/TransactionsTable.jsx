import React, { useState, useEffect } from 'react';
import { pfClient } from '../services/portfolioClient';

export default function TransactionsTable({ portfolioId, symbolFilter = null }) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'datetime', direction: 'desc' });

  const loadTransactions = async () => {
    if (!portfolioId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await pfClient.getTransactions(portfolioId, symbolFilter);
      setTransactions(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [portfolioId, symbolFilter]);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedTransactions = React.useMemo(() => {
    const sorted = [...transactions].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (sortConfig.key === 'datetime') {
        return sortConfig.direction === 'asc' 
          ? new Date(aValue) - new Date(bValue)
          : new Date(bValue) - new Date(aValue);
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }

      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      
      if (sortConfig.direction === 'asc') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
    return sorted;
  }, [transactions, sortConfig]);

  const totalFees = transactions.reduce((sum, tx) => sum + (tx.fee || 0), 0);

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="text-center text-gray-500">Loading transactions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="text-red-800 font-semibold">Error loading transactions</div>
        <div className="text-red-600">{error}</div>
        <button 
          onClick={loadTransactions}
          className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const SortHeader = ({ label, sortKey }) => (
    <th 
      className="p-3 text-left cursor-pointer hover:bg-gray-50 select-none"
      onClick={() => handleSort(sortKey)}
    >
      <div className="flex items-center gap-1">
        <span>{label}</span>
        {sortConfig.key === sortKey && (
          <span className="text-gray-400">
            {sortConfig.direction === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </div>
    </th>
  );

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Transactions {symbolFilter && `(${symbolFilter})`}
          </h3>
          <div className="text-sm text-gray-500">
            {transactions.length} transaction{transactions.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {transactions.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          No transactions found
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <SortHeader label="Date & Time" sortKey="datetime" />
                  <SortHeader label="Symbol" sortKey="symbol" />
                  <SortHeader label="Side" sortKey="side" />
                  <th className="p-3 text-right">Qty</th>
                  <th className="p-3 text-right">Price</th>
                  <th className="p-3 text-right">Fee</th>
                  <th className="p-3 text-right">Total Value</th>
                  <SortHeader label="Currency" sortKey="currency" />
                  <th className="p-3 text-left">Notes</th>
                </tr>
              </thead>
              <tbody>
                {sortedTransactions.map((tx, idx) => {
                  const totalValue = tx.qty * tx.price + (tx.side === 'BUY' ? tx.fee : -tx.fee);
                  
                  return (
                    <tr key={tx.id || idx} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="p-3">
                        <div className="text-gray-900">
                          {new Date(tx.datetime).toLocaleDateString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(tx.datetime).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="p-3">
                        <span className="font-mono font-medium">{tx.symbol}</span>
                      </td>
                      <td className="p-3">
                        <span className={`font-semibold ${
                          tx.side === 'BUY' 
                            ? 'text-green-600' 
                            : 'text-red-600'
                        }`}>
                          {tx.side}
                        </span>
                      </td>
                      <td className="p-3 text-right font-mono">
                        {tx.qty.toLocaleString()}
                      </td>
                      <td className="p-3 text-right font-mono">
                        ${tx.price.toFixed(2)}
                      </td>
                      <td className="p-3 text-right font-mono">
                        ${(tx.fee || 0).toFixed(2)}
                      </td>
                      <td className="p-3 text-right font-mono font-semibold">
                        <span className={tx.side === 'BUY' ? 'text-red-600' : 'text-green-600'}>
                          {tx.side === 'BUY' ? '-' : '+'}${Math.abs(totalValue).toFixed(2)}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-xs">
                        {tx.currency}
                      </td>
                      <td className="p-3 text-xs text-gray-600">
                        {tx.notes || '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-gray-200 bg-gray-50">
                  <td colSpan="5" className="p-3 text-right font-semibold text-gray-700">
                    Total Fees:
                  </td>
                  <td className="p-3 text-right font-mono font-semibold text-gray-900">
                    ${totalFees.toFixed(2)}
                  </td>
                  <td colSpan="3"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
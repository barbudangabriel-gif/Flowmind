import React, { useState, useEffect } from 'react';
import { mfClient } from '../services/mindfolioClient';

const CashTransferModal = ({ isOpen, onClose, fromMindfolio, onTransferComplete }) => {
  const [toMindfolio, setToMindfolio] = useState(null);
  const [amount, setAmount] = useState(0);
  const [allMindfolios, setAllMindfolios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      // Fetch all mindfolios for destination selection
      mfClient.list().then(data => {
        // Exclude the source mindfolio
        const filtered = data.filter(mf => mf.id !== fromMindfolio?.id);
        setAllMindfolios(filtered);
      });
    }
  }, [isOpen, fromMindfolio]);

  const handleTransfer = async () => {
    if (!toMindfolio || amount <= 0) {
      setError('Please fill all fields');
      return;
    }

    if (amount > fromMindfolio.cash_balance) {
      setError(`Insufficient cash (have $${fromMindfolio.cash_balance.toFixed(2)}, need $${amount.toFixed(2)})`);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const API = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${API}/api/mindfolio/transfer/cash`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'default'
        },
        body: JSON.stringify({
          from_mindfolio_id: fromMindfolio.id,
          to_mindfolio_id: toMindfolio.id,
          amount: amount
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        if (onTransferComplete) {
          onTransferComplete(result);
        }
        onClose();
        // Reset form
        setToMindfolio(null);
        setAmount(0);
      } else {
        setError(result.message || 'Transfer failed');
      }
    } catch (err) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base text-white">Transfer Cash</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-3 p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Available Cash */}
        <div className="mb-3 p-3 bg-green-500/10 border border-green-500/30 rounded">
          <div className="text-xs text-green-400 mb-1">Available Cash</div>
          <div className="text-base text-white font-semibold">
            ${fromMindfolio?.cash_balance?.toFixed(2) || '0.00'}
          </div>
        </div>

        {/* Select Destination */}
        <div className="mb-3">
          <label className="block text-xs text-gray-400 mb-1">Transfer To</label>
          <select
            value={toMindfolio ? JSON.stringify(toMindfolio) : ''}
            onChange={(e) => {
              if (e.target.value) {
                setToMindfolio(JSON.parse(e.target.value));
              } else {
                setToMindfolio(null);
              }
            }}
            className="w-full bg-[#0f1419] border border-[#1a1f26] text-white rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="">-- Select mindfolio --</option>
            {allMindfolios.map(mf => (
              <option key={mf.id} value={JSON.stringify(mf)}>
                {mf.name} (${mf.cash_balance?.toFixed(2) || '0.00'})
              </option>
            ))}
          </select>
        </div>

        {/* Amount Input */}
        <div className="mb-4">
          <label className="block text-xs text-gray-400 mb-1">
            Amount (max: ${fromMindfolio?.cash_balance?.toFixed(2) || '0.00'})
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
            <input
              type="number"
              min="0"
              max={fromMindfolio?.cash_balance || 0}
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              className="w-full bg-[#0f1419] border border-[#1a1f26] text-white rounded-lg pl-7 pr-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setAmount(fromMindfolio?.cash_balance * 0.25)}
              className="px-2 py-1 bg-[#0f1419] hover:bg-slate-700 text-white rounded text-xs border border-[#1a1f26]"
            >
              25%
            </button>
            <button
              onClick={() => setAmount(fromMindfolio?.cash_balance * 0.50)}
              className="px-2 py-1 bg-[#0f1419] hover:bg-slate-700 text-white rounded text-xs border border-[#1a1f26]"
            >
              50%
            </button>
            <button
              onClick={() => setAmount(fromMindfolio?.cash_balance * 0.75)}
              className="px-2 py-1 bg-[#0f1419] hover:bg-slate-700 text-white rounded text-xs border border-[#1a1f26]"
            >
              75%
            </button>
            <button
              onClick={() => setAmount(fromMindfolio?.cash_balance)}
              className="px-2 py-1 bg-[#0f1419] hover:bg-slate-700 text-white rounded text-xs border border-[#1a1f26]"
            >
              100%
            </button>
          </div>
        </div>

        {/* Transfer Summary */}
        {toMindfolio && amount > 0 && (
          <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded">
            <div className="text-xs text-blue-400 mb-2">Transfer Summary</div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between text-white">
                <span>From:</span>
                <span>${fromMindfolio.cash_balance.toFixed(2)} → ${(fromMindfolio.cash_balance - amount).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-white">
                <span>To:</span>
                <span>${toMindfolio.cash_balance.toFixed(2)} → ${(toMindfolio.cash_balance + amount).toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={onClose}
            className="flex-1 px-3 py-2 bg-[#0a0e1a] hover:bg-slate-700 text-white rounded-lg border border-[#1a1f26] text-sm"
          >
            Cancel
          </button>
          <button
            onClick={handleTransfer}
            disabled={loading || !toMindfolio || amount <= 0}
            className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Transferring...' : 'Transfer'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CashTransferModal;

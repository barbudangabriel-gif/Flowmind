import React, { useState, useEffect } from 'react';
import { mfClient } from '../services/mindfolioClient';

const PositionTransferModal = ({ isOpen, onClose, fromMindfolio, positions, onTransferComplete }) => {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [toMindfolio, setToMindfolio] = useState(null);
  const [quantity, setQuantity] = useState(0);
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
    if (!selectedPosition || !toMindfolio || quantity <= 0) {
      setError('Please fill all fields');
      return;
    }

    if (quantity > selectedPosition.qty) {
      setError(`Insufficient quantity (have ${selectedPosition.qty}, need ${quantity})`);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const API = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${API}/api/mindfolio/transfer/position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'default'
        },
        body: JSON.stringify({
          from_mindfolio_id: fromMindfolio.id,
          to_mindfolio_id: toMindfolio.id,
          symbol: selectedPosition.symbol,
          quantity: quantity
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        if (onTransferComplete) {
          onTransferComplete(result);
        }
        onClose();
        // Reset form
        setSelectedPosition(null);
        setToMindfolio(null);
        setQuantity(0);
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
          <h2 className="text-base text-white">Transfer Position</h2>
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

        {/* Select Position */}
        <div className="mb-3">
          <label className="block text-xs text-gray-400 mb-1">Select Position</label>
          <select 
            value={selectedPosition ? JSON.stringify(selectedPosition) : ''}
            onChange={(e) => {
              if (e.target.value) {
                const pos = JSON.parse(e.target.value);
                setSelectedPosition(pos);
                setQuantity(pos.qty); // Default to full quantity
              } else {
                setSelectedPosition(null);
                setQuantity(0);
              }
            }}
            className="w-full bg-[#0f1419] border border-[#1a1f26] text-white rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="">-- Select position --</option>
            {positions?.map(pos => (
              <option key={pos.symbol} value={JSON.stringify(pos)}>
                {pos.symbol} - {pos.qty} shares @ ${pos.avg_cost.toFixed(2)}
              </option>
            ))}
          </select>
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
                {mf.name}
              </option>
            ))}
          </select>
        </div>

        {/* Quantity Input */}
        <div className="mb-4">
          <label className="block text-xs text-gray-400 mb-1">
            Quantity (max: {selectedPosition?.qty || 0})
          </label>
          <input
            type="number"
            min="0"
            max={selectedPosition?.qty || 0}
            step="1"
            value={quantity}
            onChange={(e) => setQuantity(parseFloat(e.target.value) || 0)}
            className="w-full bg-[#0f1419] border border-[#1a1f26] text-white rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* Transfer Summary */}
        {selectedPosition && toMindfolio && quantity > 0 && (
          <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded">
            <div className="text-xs text-blue-400 mb-2">Transfer Summary</div>
            <div className="text-sm text-white">
              {quantity} shares of {selectedPosition.symbol} → {toMindfolio.name}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Cost basis: ${(quantity * selectedPosition.avg_cost).toFixed(2)}
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
            disabled={loading || !selectedPosition || !toMindfolio || quantity <= 0}
            className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Transferring...' : 'Transfer'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PositionTransferModal;

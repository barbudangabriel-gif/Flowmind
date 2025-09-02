import { useState } from 'react';
import { portfolioAPI } from '../lib/portfolioAPI';

export default function BucketForm({ portfolioId, onCreated }) {
  const [name, setName] = useState('Sell Puts Income');
  const [startValue, setStartValue] = useState(100000);
  const [symbolContains, setSymbolContains] = useState('');
  const [side, setSide] = useState('SELL');
  const [optType, setOptType] = useState('PUT');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError('Bucket name is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await portfolioAPI.createBucket(portfolioId, {
        name: name.trim(),
        start_value: startValue,
        description: `Auto-created bucket for ${side} ${optType} strategy`,
        rules: [{
          symbol_contains: symbolContains || undefined,
          side: side || undefined,
          opt_type: optType || undefined
        }]
      });

      // Reset form
      setName('Sell Puts Income');
      setStartValue(100000);
      setSymbolContains('');
      setSide('SELL');
      setOptType('PUT');

      // Notify parent
      if (onCreated) {
        onCreated();
      }
    } catch (err) {
      console.error('Failed to create bucket:', err);
      setError(err.message || 'Failed to create bucket');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow p-4 space-y-4">
      <div className="font-semibold">Add Strategy Bucket</div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Bucket Name</label>
          <input 
            className="w-full border rounded px-3 py-2" 
            placeholder="Strategy name" 
            value={name} 
            onChange={e => setName(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div>
          <label className="block text-xs text-gray-500 mb-1">Start Budget</label>
          <input 
            className="w-full border rounded px-3 py-2" 
            type="number" 
            placeholder="100000" 
            value={startValue} 
            onChange={e => setStartValue(Number(e.target.value))}
            disabled={loading}
          />
        </div>
        
        <div>
          <label className="block text-xs text-gray-500 mb-1">Symbol Filter</label>
          <input 
            className="w-full border rounded px-3 py-2" 
            placeholder="SPY, QQQ, etc (optional)" 
            value={symbolContains} 
            onChange={e => setSymbolContains(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div>
          <label className="block text-xs text-gray-500 mb-1">Trade Side</label>
          <select 
            className="w-full border rounded px-3 py-2" 
            value={side} 
            onChange={e => setSide(e.target.value)}
            disabled={loading}
          >
            <option value="">Any Side</option>
            <option value="SELL">SELL</option>
            <option value="BUY">BUY</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs text-gray-500 mb-1">Option Type</label>
          <select 
            className="w-full border rounded px-3 py-2" 
            value={optType} 
            onChange={e => setOptType(e.target.value)}
            disabled={loading}
          >
            <option value="">Any Type</option>
            <option value="PUT">PUT</option>
            <option value="CALL">CALL</option>
          </select>
        </div>
      </div>

      <button 
        className="bg-black text-white px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={handleSubmit}
        disabled={loading || !name.trim()}
      >
        {loading ? 'Creating...' : 'Create Bucket'}
      </button>
      
      <div className="text-xs text-gray-500">
        Buckets help track performance of specific trading strategies by filtering transactions based on rules.
      </div>
    </div>
  );
}
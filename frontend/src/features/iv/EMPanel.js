import React, { useState, useEffect } from 'react';
import { ivAPI } from './api';

export default function EMPanel() {
  const [symbol, setSymbol] = useState('NVDA');
  const [spotData, setSpotData] = useState(null);
  const [termData, setTermData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [spot, term] = await Promise.all([
        ivAPI.getSpot(symbol),
        ivAPI.getTerm(symbol)
      ]);
      setSpotData(spot);
      setTermData(term);
    } catch (err) {
      console.error('IV data error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [symbol]);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-4">EM Panel</h1>
        
        <div className="mb-4">
          <input
            className="px-3 py-2 border rounded"
            value={symbol}
            onChange={e => setSymbol(e.target.value.toUpperCase())}
            placeholder="Symbol"
          />
          <button
            className="ml-2 px-4 py-2 bg-blue-600 text-white rounded"
            onClick={loadData}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Load'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">Spot Data</h3>
            <pre className="bg-gray-100 dark:bg-gray-700 p-3 rounded text-sm">
              {JSON.stringify(spotData, null, 2)}
            </pre>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-2">Term Structure</h3>
            <pre className="bg-gray-100 dark:bg-gray-700 p-3 rounded text-sm">
              {JSON.stringify(termData, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, Activity, RefreshCw, Search, Filter, Star, ExternalLink } from 'lucide-react';

const InvestmentScoringDisplay = () => {
  const navigate = useNavigate();
  const [scannerStatus, setScannerStatus] = useState(null);
  const [topStocks, setTopStocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [limit, setLimit] = useState(50);
  const [error, setError] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch scanner status
  const fetchScannerStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/scanner/status`);
      const data = await response.json();
      setScannerStatus(data);
    } catch (err) {
      console.error('Error fetching scanner status:', err);
      setError('Eroare la obținerea statusului scanner-ului');
    }
  };

  // Fetch top stocks
  const fetchTopStocks = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/scanner/top-stocks?limit=${limit}`);
      const data = await response.json();
      setTopStocks(data.top_stocks || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching top stocks:', err);
      setError('Eroare la obținerea acțiunilor top');
    } finally {
      setLoading(false);
    }
  };

  // Start scan
  const startScan = async () => {
    setScanning(true);
    try {
      const response = await fetch(`${backendUrl}/api/scanner/start-scan`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (response.ok) {
        setError(null);
        // Refresh status and data after starting scan
        setTimeout(() => {
          fetchScannerStatus();
          fetchTopStocks();
        }, 2000);
      } else {
        setError(data.detail || 'Eroare la pornirea scanării');
      }
    } catch (err) {
      console.error('Error starting scan:', err);
      setError('Eroare la pornirea scanării');
    } finally {
      setScanning(false);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchScannerStatus();
    fetchTopStocks();
  }, [limit]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchScannerStatus();
      if (!scanning) {
        fetchTopStocks();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [scanning]);

  // Filter stocks based on search term
  const filteredStocks = topStocks.filter(stock =>
    stock.ticker?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.sector?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Navigate to stock analysis page
  const handleTickerClick = (ticker) => {
    navigate(`/stock-analysis/${ticker}`);
  };

  // Get rating color
  const getRatingColor = (rating) => {
    if (rating?.includes('BUY')) return 'text-green-400';
    if (rating?.includes('HOLD')) return 'text-yellow-400';
    if (rating?.includes('SELL')) return 'text-red-400';
    return 'text-gray-400';
  };

  // Get score color
  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-600 p-3 rounded-lg">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Investment Scoring</h1>
              <p className="text-gray-400">Scanner pentru cele mai bune oportunități de investiții</p>
            </div>
          </div>

          {/* Status Card */}
          {scannerStatus && (
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Status Scanner</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      fetchScannerStatus();
                      fetchTopStocks();
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                  </button>
                  <button
                    onClick={startScan}
                    disabled={scanning}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <Activity className="w-4 h-4" />
                    {scanning ? 'Scanez...' : 'Start Scan'}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Status</div>
                  <div className={`font-semibold ${scannerStatus.status === 'completed' ? 'text-green-400' : 'text-yellow-400'}`}>
                    {scannerStatus.status === 'completed' ? 'Completat' : 
                     scannerStatus.status === 'no_scans' ? 'Fără scanări' : 
                     scannerStatus.status}
                  </div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Total Acțiuni</div>
                  <div className="text-2xl font-bold text-white">{scannerStatus.total_stocks_scanned || 0}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Ultima Scanare</div>
                  <div className="text-white">
                    {scannerStatus.last_scan_date ? 
                      new Date(scannerStatus.last_scan_date).toLocaleDateString('ro-RO') : 
                      'N/A'}
                  </div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Database</div>
                  <div className={`font-semibold ${scannerStatus.database_status === 'active' ? 'text-green-400' : 'text-red-400'}`}>
                    {scannerStatus.database_status === 'active' ? 'Activ' : 'Inactiv'}
                  </div>
                </div>
              </div>

              {/* Top 5 Quick View */}
              {scannerStatus.top_5_stocks && scannerStatus.top_5_stocks.length > 0 && (
                <div className="mt-4">
                  <div className="text-sm text-gray-400 mb-2">Top 5 Acțiuni:</div>
                  <div className="flex flex-wrap gap-2">
                    {scannerStatus.top_5_stocks.map((stock, index) => (
                      <div key={index} className="bg-gray-700 rounded-lg px-3 py-2 flex items-center gap-2">
                        <Star className="w-4 h-4 text-yellow-400" />
                        <span className="text-white font-medium">{stock.ticker}</span>
                        <span className={`text-sm ${getScoreColor(stock.score)}`}>
                          {stock.score}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <div className="relative">
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Caută ticker sau sector..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-gray-700 text-white pl-10 pr-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none w-64"
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value))}
                  className="bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                >
                  <option value={25}>25 rezultate</option>
                  <option value={50}>50 rezultate</option>
                  <option value={100}>100 rezultate</option>
                </select>
              </div>
            </div>
            <div className="text-gray-400 text-sm">
              {filteredStocks.length} din {topStocks.length} acțiuni
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <div className="text-red-400">{error}</div>
          </div>
        )}

        {/* Stocks Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
            <span className="ml-3 text-gray-400">Se încarcă datele...</span>
          </div>
        ) : filteredStocks.length > 0 ? (
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Rank</th>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Ticker</th>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Scor</th>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Rating</th>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Preț</th>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Sector</th>
                    <th className="text-left px-6 py-4 text-gray-300 font-semibold">Explicație</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {filteredStocks.map((stock, index) => (
                    <tr key={index} className="hover:bg-gray-700 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="bg-blue-600 text-white px-2 py-1 rounded text-sm font-medium">
                            #{index + 1}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-semibold text-white text-lg">{stock.ticker}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`text-xl font-bold ${getScoreColor(stock.score)}`}>
                          {stock.score}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`font-medium ${getRatingColor(stock.rating)}`}>
                          {stock.rating}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-white">
                          {stock.price !== 'N/A' ? `$${stock.price}` : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-gray-300">{stock.sector}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-gray-400 text-sm max-w-xs truncate">
                          {stock.explanation}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-xl p-12 text-center border border-gray-700">
            <TrendingUp className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-300 mb-2">Nu există date</h3>
            <p className="text-gray-500 mb-6">
              {scannerStatus?.status === 'no_scans' 
                ? 'Nu s-au efectuat scanări încă. Apasă "Start Scan" pentru a începe.'
                : 'Nu s-au găsit acțiuni conform criteriilor de căutare.'}
            </p>
            {scannerStatus?.status === 'no_scans' && (
              <button
                onClick={startScan}
                disabled={scanning}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 mx-auto transition-colors"
              >
                <Activity className="w-5 h-5" />
                {scanning ? 'Se scanează...' : 'Pornește Scanarea'}
              </button>
            )}
          </div>
        )}

        {/* Stats Footer */}
        {topStocks.length > 0 && (
          <div className="mt-6 bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-400">
                  {topStocks.filter(s => s.score >= 70).length}
                </div>
                <div className="text-gray-400">Scor ≥ 70 (Excelent)</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-400">
                  {topStocks.filter(s => s.score >= 60 && s.score < 70).length}
                </div>
                <div className="text-gray-400">Scor 60-69 (Bun)</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-400">
                  {topStocks.filter(s => s.score < 60).length}
                </div>
                <div className="text-gray-400">Scor &lt; 60 (Moderat)</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InvestmentScoringDisplay;
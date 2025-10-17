// Enhanced Portfolio Component - Hybrid UI + Real TradeStation Data
const EnhancedPortfolio = () => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // UI State
  const [activeTab, setActiveTab] = useState('positions');
  const [assetFilter, setAssetFilter] = useState('all');
  const [expandedSymbols, setExpandedSymbols] = useState(new Set());
  
  const { isDarkMode } = useTheme();

  // Load accounts and data
  useEffect(() => {
    loadAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      loadPortfolioData(selectedAccount);
    }
  }, [selectedAccount]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tradestation/accounts`);
      if (response.data?.accounts?.length > 0) {
        setAccounts(response.data.accounts);
        setSelectedAccount(response.data.accounts[0].AccountID);
      }
    } catch (err) {
      setError(`Failed to load accounts: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadPortfolioData = async (accountId) => {
    if (!accountId) return;
    
    try {
      setLoading(true);
      const response = await fetch(`${API}/tradestation/accounts/${accountId}/positions-simple`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      if (data.data) {
        setPortfolioData(data.data);
        setError(null);
      } else {
        throw new Error('Invalid data structure received');
      }
    } catch (err) {
      setError(`Failed to load portfolio data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Helper functions
  const getBaseSymbol = (symbol) => {
    const match = symbol.match(/^([A-Z]+)/);
    return match ? match[1] : symbol;
  };

  const isOptionPosition = (position) => {
    return position.asset_type === 'STOCKOPTION' || position.symbol.includes(' ');
  };

  const groupPositionsByTicker = (positions) => {
    const groups = {};
    positions.forEach(position => {
      const baseSymbol = getBaseSymbol(position.symbol);
      if (!groups[baseSymbol]) {
        groups[baseSymbol] = {
          baseSymbol: baseSymbol,
          positions: [],
          hasMultiplePositions: false
        };
      }
      groups[baseSymbol].positions.push(position);
    });
    
    Object.keys(groups).forEach(symbol => {
      groups[symbol].hasMultiplePositions = groups[symbol].positions.length > 1;
    });
    
    return groups;
  };

  const filterPositionsByAsset = (positions) => {
    if (!positions) return [];
    if (assetFilter === 'all') return positions;
    if (assetFilter === 'stocks') return positions.filter(p => p.asset_type === 'STOCK');
    if (assetFilter === 'options') return positions.filter(p => p.asset_type === 'STOCKOPTION');
    return positions;
  };

  const toggleSymbolExpansion = (symbol) => {
    const newExpanded = new Set(expandedSymbols);
    if (newExpanded.has(symbol)) {
      newExpanded.delete(symbol);
    } else {
      newExpanded.add(symbol);
    }
    setExpandedSymbols(newExpanded);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  };

  const formatPercent = (value) => {
    return `${value?.toFixed(2) || '0.00'}%`;
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(Math.abs(value));
  };

  const getPnlColor = (value) => {
    if (value > 0) return 'text-green-400';
    if (value < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const calculateTotalCost = (position) => {
    return position.quantity * position.average_price;
  };

  // Generate chart data from real positions
  const generateChartData = () => {
    if (!portfolioData?.positions) return [];
    
    const grouped = groupPositionsByTicker(filterPositionsByAsset(portfolioData.positions));
    return Object.entries(grouped).map(([symbol, group]) => ({
      symbol: symbol,
      value: group.positions.reduce((sum, pos) => sum + Math.abs(pos.market_value), 0),
      count: group.positions.length
    })).sort((a, b) => b.value - a.value).slice(0, 10);
  };

  const chartData = generateChartData();

  // Tabs configuration
  const tabs = [
    { id: 'positions', label: 'Positions', icon: BarChart3 },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'allocation', label: 'Allocation', icon: PieChart },
    { id: 'risk', label: 'Risk Analysis', icon: Shield }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'positions':
        return renderPositionsTab();
      case 'performance':
        return renderPerformanceTab();
      case 'allocation':
        return renderAllocationTab();
      case 'risk':
        return renderRiskTab();
      default:
        return renderPositionsTab();
    }
  };

  const renderPositionsTab = () => {
    if (!portfolioData?.positions) return <div>No positions data</div>;

    const filteredPositions = filterPositionsByAsset(portfolioData.positions);
    const groupedByTicker = groupPositionsByTicker(filteredPositions);
    
    const rows = [];
    
    Object.entries(groupedByTicker).forEach(([ticker, group]) => {
      const isExpanded = expandedSymbols.has(ticker);
      const { positions, hasMultiplePositions } = group;
      
      if (hasMultiplePositions) {
        const totalMarketValue = positions.reduce((sum, pos) => sum + pos.market_value, 0);
        const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0);
        
        rows.push(
          <tr key={`ticker-${ticker}`} className="bg-gradient-to-r from-blue-900 to-blue-800 hover:from-blue-850 hover:to-blue-750 transition-all duration-200 border-b-2 border-blue-600">
            <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
              <div className="flex items-center gap-1">
                <button 
                  className="text-gray-300 hover:text-[rgb(252, 251, 255)] transition-colors flex-shrink-0"
                  onClick={() => toggleSymbolExpansion(ticker)}
                >
                  <div className={`ts-double-arrow ${isExpanded ? 'expanded' : ''}`}></div>
                </button>
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="font-bold text-[rgb(252, 251, 255)] text-base truncate">{ticker}</span>
                  <span className="text-xs text-blue-200 truncate">{positions.length} positions</span>
                </div>
              </div>
            </td>
            <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
              <div className="text-sm text-blue-100 truncate">GROUP: {ticker}</div>
            </td>
            <td className="px-3 py-2 text-center border-r border-gray-600 w-24 min-w-24">
              <div className="text-sm font-medium text-blue-100">{positions.length}</div>
            </td>
            <td className={`px-3 py-2 text-right font-bold border-r border-gray-600 w-28 min-w-28 ${getPnlColor(totalPnL)} truncate`}>
              {totalPnL > 0 ? '+' : ''}{formatCurrency(totalPnL)}
            </td>
            <td className="px-3 py-2 text-right font-bold border-r border-gray-600 w-32 min-w-32 text-blue-100 truncate">
              {formatCurrency(totalMarketValue)}
            </td>
          </tr>
        );
        
        if (isExpanded) {
          positions.forEach((position, posIndex) => {
            rows.push(
              <tr key={`${ticker}-pos-${posIndex}`} className="bg-gradient-to-r from-gray-750 to-gray-800 hover:from-gray-700 hover:to-gray-750 transition-all duration-200 border-b border-gray-600 border-l-4 border-l-cyan-400">
                <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
                  <div className="flex items-center gap-1 pl-8">
                    <div className="flex flex-col min-w-0 flex-1">
                      <span className="font-semibold text-cyan-300 text-sm truncate">{position.symbol}</span>
                      <span className="text-xs text-gray-500 uppercase truncate">{position.asset_type || 'POS'}</span>
                    </div>
                  </div>
                </td>
                <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
                  <div className="text-sm text-gray-300 truncate">{position.description || `${position.symbol} Position`}</div>
                </td>
                <td className="px-3 py-2 text-center border-r border-gray-600 w-24 min-w-24">
                  <div className="flex flex-col items-center">
                    <span className={`text-xs font-medium px-1 py-0.5 rounded ${position.quantity > 0 ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'}`}>
                      {position.quantity > 0 ? 'LONG' : 'SHORT'}
                    </span>
                    <span className="text-sm font-medium text-gray-200">{Math.abs(position.quantity)}</span>
                  </div>
                </td>
                <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-28 min-w-28 ${getPnlColor(position.unrealized_pnl)} truncate`}>
                  {position.unrealized_pnl > 0 ? '+' : ''}{formatCurrency(position.unrealized_pnl)}
                </td>
                <td className="px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 text-gray-200 truncate">
                  {formatCurrency(position.market_value)}
                </td>
              </tr>
            );
          });
        }
      } else {
        const position = positions[0];
        rows.push(
          <tr key={`single-${ticker}`} className="bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-750 hover:to-gray-850 transition-all duration-200 border-b border-gray-600">
            <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 flex-shrink-0"></div>
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="font-semibold text-blue-300 text-sm truncate">{position.symbol}</span>
                  <span className="text-xs text-gray-400 uppercase truncate">{position.asset_type || 'SINGLE'}</span>
                </div>
              </div>
            </td>
            <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
              <div className="text-sm text-gray-300 truncate">{position.description || `${position.symbol} Position`}</div>
            </td>
            <td className="px-3 py-2 text-center border-r border-gray-600 w-24 min-w-24">
              <div className="flex flex-col items-center">
                <span className={`text-xs font-medium px-1 py-0.5 rounded ${position.quantity > 0 ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'}`}>
                  {position.quantity > 0 ? 'LONG' : 'SHORT'}
                </span>
                <span className="text-sm font-medium text-gray-200">{Math.abs(position.quantity)}</span>
              </div>
            </td>
            <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-28 min-w-28 ${getPnlColor(position.unrealized_pnl)} truncate`}>
              {position.unrealized_pnl > 0 ? '+' : ''}{formatCurrency(position.unrealized_pnl)}
            </td>
            <td className="px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 text-gray-200 truncate">
              {formatCurrency(position.market_value)}
            </td>
          </tr>
        );
      }
    });
    
    return (
      <div className="overflow-hidden">
        <div className="mb-4 flex flex-wrap gap-2">
          {['all', 'stocks', 'options'].map((filter) => (
            <button
              key={filter}
              onClick={() => setAssetFilter(filter)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                assetFilter === filter
                  ? 'bg-blue-600 text-[rgb(252, 251, 255)]'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900 text-gray-300">
              <tr>
                <th className="px-3 py-2 text-left">Symbol</th>
                <th className="px-3 py-2 text-left">Description</th>
                <th className="px-3 py-2 text-center">Quantity</th>
                <th className="px-3 py-2 text-right">P&L</th>
                <th className="px-3 py-2 text-right">Market Value</th>
              </tr>
            </thead>
            <tbody>
              {rows}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderPerformanceTab = () => (
    <div className="text-center py-8">
      <TrendingUp size={48} className="mx-auto text-gray-400 mb-4" />
      <p className="text-gray-500">Performance analytics coming soon...</p>
    </div>
  );

  const renderAllocationTab = () => (
    <div className="space-y-6">
      <div className="bg-white/80 backdrop-blur-sm p-6 rounded-xl shadow-lg">
        <h3 className="text-lg font-semibold mb-4">Portfolio Allocation</h3>
        {chartData.length > 0 ? (
          <div className="space-y-2">
            {chartData.map((item, index) => (
              <div key={item.symbol} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full`} style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                  <span className="font-medium">{item.symbol}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{formatCurrency(item.value)}</div>
                  <div className="text-sm text-gray-500">{item.count} positions</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No allocation data available</p>
        )}
      </div>
    </div>
  );

  const renderRiskTab = () => (
    <div className="text-center py-8">
      <Shield size={48} className="mx-auto text-gray-400 mb-4" />
      <p className="text-gray-500">Risk analysis coming soon...</p>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-xl text-[rgb(252, 251, 255)]">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Enhanced Portfolio</h1>
            <p className="text-blue-100">Real-time TradeStation integration</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedAccount || ''}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="bg-white/20 border border-white/30 rounded-lg px-3 py-2 text-[rgb(252, 251, 255)] placeholder-white/70"
            >
              <option value="">Select Account</option>
              {accounts.map(account => (
                <option key={account.AccountID} value={account.AccountID} className="text-gray-900">
                  {account.DisplayName} ({account.AccountID})
                </option>
              ))}
            </select>
            {error && (
              <button
                onClick={() => selectedAccount && loadPortfolioData(selectedAccount)}
                className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
              >
                Refresh
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Portfolio Metrics Cards */}
      {portfolioData?.portfolio_metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 p-6 rounded-xl text-[rgb(252, 251, 255)] shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-100 text-sm">Total Value</p>
                <p className="text-2xl font-bold">{formatCurrency(portfolioData.portfolio_metrics.total_market_value)}</p>
              </div>
              <DollarSign size={32} className="text-emerald-200" />
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl text-[rgb(252, 251, 255)] shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Positions</p>
                <p className="text-2xl font-bold">{portfolioData.portfolio_metrics.position_count || portfolioData.positions?.length || 0}</p>
              </div>
              <Briefcase size={32} className="text-blue-200" />
            </div>
          </div>
          
          <div className={`bg-gradient-to-br ${portfolioData.portfolio_metrics.total_unrealized_pnl >= 0 ? 'from-green-500 to-green-600' : 'from-red-500 to-red-600'} p-6 rounded-xl text-[rgb(252, 251, 255)] shadow-lg`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[rgb(252, 251, 255)]/80 text-sm">P&L</p>
                <p className="text-2xl font-bold">
                  {portfolioData.portfolio_metrics.total_unrealized_pnl > 0 ? '+' : ''}
                  {formatCurrency(portfolioData.portfolio_metrics.total_unrealized_pnl)}
                </p>
              </div>
              <TrendingUp size={32} className="text-[rgb(252, 251, 255)]/80" />
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl text-[rgb(252, 251, 255)] shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Daily P&L</p>
                <p className="text-2xl font-bold">
                  {portfolioData.portfolio_metrics.total_daily_pnl > 0 ? '+' : ''}
                  {formatCurrency(portfolioData.portfolio_metrics.total_daily_pnl)}
                </p>
              </div>
              <Activity size={32} className="text-purple-200" />
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <div className="flex items-center">
            <AlertTriangle className="h-4 w-4 mr-2" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white/80 backdrop-blur-sm rounded-xl p-1 shadow-lg">
        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-[rgb(252, 251, 255)] shadow-lg'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <tab.icon size={16} />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg overflow-hidden">
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};
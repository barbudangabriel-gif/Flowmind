import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ChevronDown, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  AlertTriangle,
  X,
  Eye,
  BarChart3,
  FileText,
  Brain,
  PieChart as PieChartIcon
} from 'lucide-react';
import ContextMenu from './ContextMenu';
import usePortfolioManagement from '../hooks/usePortfolioManagement';

const IndividualPortfolio = () => {
  const navigate = useNavigate();
  const { portfolioId } = useParams();
  const [activeTab, setActiveTab] = useState('holdings');
  
  // Context menu state
  const [contextMenu, setContextMenu] = useState({
    isVisible: false,
    position: { x: 0, y: 0 },
    selectedPosition: null
  });

  // Portfolio management hook
  const {
    portfolios,
    positions,
    availablePortfolios,
    loading,
    error,
    fetchPortfolioPositions,
    fetchAvailablePortfolios,
    movePosition,
    clearError
  } = usePortfolioManagement();

  // Current portfolio data
  const [currentPortfolio, setCurrentPortfolio] = useState(null);

  // Load portfolio and positions data
  useEffect(() => {
    if (portfolioId && portfolios.length > 0) {
      // Find current portfolio
      const portfolio = portfolios.find(p => p.id === portfolioId);
      setCurrentPortfolio(portfolio);
      
      // Load positions for this portfolio
      fetchPortfolioPositions(portfolioId);
      
      // Load available portfolios for moving
      fetchAvailablePortfolios(portfolioId);
    }
  }, [portfolioId, portfolios]);

  // Handle right-click context menu
  const handleContextMenu = (event, position) => {
    event.preventDefault();
    
    setContextMenu({
      isVisible: true,
      position: { x: event.clientX, y: event.clientY },
      selectedPosition: position
    });
  };

  // Close context menu
  const closeContextMenu = () => {
    setContextMenu({
      isVisible: false,
      position: { x: 0, y: 0 },
      selectedPosition: null
    });
  };

  // Handle position move
  const handleMovePosition = async (positionId, toPortfolioId, portfolioName) => {
    try {
      const result = await movePosition(positionId, toPortfolioId);
      
      if (result.success) {
        // Show success message
        alert(`Position moved successfully to ${portfolioName}`);
        
        // Refresh positions
        fetchPortfolioPositions(portfolioId);
      } else {
        throw new Error(result.error || 'Failed to move position');
      }
    } catch (error) {
      alert(`Error moving position: ${error.message}`);
    }
  };

  // Default to TradeStation Main if no portfolio found
  const displayPortfolio = currentPortfolio || {
    name: 'TradeStation Main',
    total_value: 0,
    total_pnl: 0,
    positions_count: 0
  };

  const changePercent = displayPortfolio.total_value > 0 
    ? (displayPortfolio.total_pnl / (displayPortfolio.total_value - displayPortfolio.total_pnl)) * 100 
    : 0;

  const getRatingColor = (rating) => {
    if (rating >= 4) return 'bg-green-500 text-white';
    if (rating >= 3.5) return 'bg-green-400 text-white';
    if (rating >= 3) return 'bg-yellow-500 text-white';
    if (rating >= 2.5) return 'bg-yellow-400 text-white';
    if (rating >= 2) return 'bg-orange-500 text-white';
    return 'bg-red-500 text-white';
  };

  const getChangeColor = (change) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
    return num.toString();
  };

  const tabs = [
    { id: 'summary', label: 'Summary' },
    { id: 'health-score', label: 'Health Score' },
    { id: 'ratings', label: 'Ratings' },
    { id: 'holdings', label: 'Holdings' },
    { id: 'dividends', label: 'Dividends' },
    { id: 'add-edit-views', label: '+ Add / Edit Views', hasArrow: true }
  ];

  const newsItems = [
    {
      symbol: 'MCHP',
      title: 'Microchip Technology Incorporated (MCHP) Presents at KeyBanc Technology Leadership Forum Conference Transcript',
      source: 'SA Transcripts',
      date: 'Thu, Aug 14'
    },
    {
      symbol: 'SWKS',
      title: 'Skyworks Solutions, Inc. (SWKS) KeyBanc Technology Leadership Forum Conference (Transcript)',
      source: 'SA Transcripts',
      date: 'Tue, Aug 12'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-blue-500 px-6 py-4">
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold text-white flex items-center">
            Portfolio {currentPortfolio.name}
            <ChevronDown className="ml-2" size={20} />
          </h1>
        </div>
        
        <div className="flex items-center mt-2">
          <Eye className="text-white mr-2" size={16} />
          <span className="text-3xl font-bold text-white">
            ${currentPortfolio.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className={`ml-4 text-lg font-medium ${currentPortfolio.change >= 0 ? 'text-green-300' : 'text-red-300'}`}>
            {currentPortfolio.change >= 0 ? '+' : ''}${Math.abs(currentPortfolio.change).toFixed(2)} ({currentPortfolio.changePercent >= 0 ? '+' : ''}{currentPortfolio.changePercent.toFixed(2)}%)
          </span>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center mt-4 space-x-3">
          <button
            onClick={() => navigate(`/portfolios/${portfolioId}/charts`)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PieChartIcon size={16} />
            <span>Charts</span>
          </button>
          
          <button
            onClick={() => navigate(`/portfolios/${portfolioId}/rebalancing`)}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Brain size={16} />
            <span>AI Rebalancing</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                if (tab.id === 'add-edit-views') {
                  // Handle Add/Edit Views click - you mentioned you'll show the method
                  navigate(`/portfolios/${portfolioId}/add-edit-views`);
                } else {
                  setActiveTab(tab.id);
                }
              }}
              className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.hasArrow && <span className="ml-1 text-red-500">→</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        
        {/* Holdings Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2 font-medium text-gray-600">Symbol</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Price</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Change</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Change %</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Weight</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Volume</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Avg. Vol</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Prev Close</th>
                <th className="text-right py-3 px-2 font-medium text-gray-600">Open</th>
                <th className="text-center py-3 px-2 font-medium text-gray-600">Day Range</th>
                <th className="text-center py-3 px-2 font-medium text-gray-600">52W Range</th>
                <th className="text-center py-3 px-2 font-medium text-gray-600">Quant SA Analyst Rating</th>
                <th className="text-center py-3 px-2 font-medium text-gray-600">SA Analyst Ratings</th>
                <th className="text-center py-3 px-2 font-medium text-gray-600">Wall Street Ratings</th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((holding, index) => (
                <tr key={holding.symbol} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-2">
                    <span className="text-blue-600 font-medium cursor-pointer hover:underline">
                      {holding.symbol}
                    </span>
                  </td>
                  <td className="text-right py-3 px-2 font-medium">{holding.price.toFixed(2)}</td>
                  <td className={`text-right py-3 px-2 font-medium ${getChangeColor(holding.change)}`}>
                    {holding.change >= 0 ? '+' : ''}{holding.change.toFixed(2)}
                  </td>
                  <td className={`text-right py-3 px-2 font-medium ${getChangeColor(holding.changePercent)}`}>
                    {holding.changePercent >= 0 ? '+' : ''}{holding.changePercent.toFixed(2)}%
                  </td>
                  <td className="text-right py-3 px-2">{holding.weight}</td>
                  <td className="text-right py-3 px-2">{holding.volume}</td>
                  <td className="text-right py-3 px-2">{holding.avgVol}</td>
                  <td className="text-right py-3 px-2">{holding.prevClose.toFixed(2)}</td>
                  <td className="text-right py-3 px-2">{holding.open.toFixed(2)}</td>
                  <td className="text-center py-3 px-2 text-gray-600">{holding.dayRange}</td>
                  <td className="text-center py-3 px-2 text-gray-600">{holding.week52Range}</td>
                  <td className="text-center py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${getRatingColor(holding.quantRating)}`}>
                      {holding.quantRating.toFixed(2)}
                    </span>
                  </td>
                  <td className="text-center py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${getRatingColor(holding.saRating)}`}>
                      {holding.saRating.toFixed(2)}
                    </span>
                  </td>
                  <td className="text-center py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${getRatingColor(holding.wsRating)}`}>
                      {holding.wsRating.toFixed(2)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Warnings */}
        <div className="mt-6 space-y-3">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-500 mr-3" size={20} />
              <span className="text-red-700">
                <strong>Warning:</strong> ASGN is at high risk of performing badly. <span className="text-blue-600 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-500 hover:text-red-700">
              <X size={20} />
            </button>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-500 mr-3" size={20} />
              <span className="text-red-700">
                <strong>Warning:</strong> IT is at high risk of performing badly. <span className="text-blue-600 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-500 hover:text-red-700">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Bottom Tabs */}
        <div className="mt-8 border-b border-gray-200">
          <div className="flex space-x-8">
            {['Latest', 'Analysis', 'News', 'Warnings', 'Transcripts', 'Press Releases'].map((tabName, index) => (
              <button
                key={tabName}
                className={`py-3 px-2 border-b-2 font-medium text-sm ${
                  index === 4 // Transcripts active
                    ? 'border-black text-black'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tabName}
              </button>
            ))}
          </div>
        </div>

        {/* News/Transcripts Section */}
        <div className="mt-6 space-y-4">
          {newsItems.map((item, index) => (
            <div key={index} className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg cursor-pointer">
              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <FileText className="text-gray-500" size={16} />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 hover:text-blue-600">
                  {item.title}
                </h3>
                <div className="flex items-center mt-1 space-x-2 text-sm text-gray-500">
                  <span className="text-blue-600 font-medium">{item.symbol}</span>
                  <span>•</span>
                  <span>{item.source}</span>
                  <span>•</span>
                  <span>{item.date}</span>
                  <span>•</span>
                  <span>📄</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IndividualPortfolio;
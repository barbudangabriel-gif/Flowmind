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

const IndividualPortfolio = () => {
  const navigate = useNavigate();
  const { portfolioId } = useParams();
  const [activeTab, setActiveTab] = useState('summary');
  
  // Portfolio data
  const portfolioData = {
    'portfolio-1': { 
      name: 'Portfolio 1', 
      value: 125450.00, 
      change: -1450.23, 
      changePercent: -1.15 
    },
    'portfolio-2': { 
      name: 'Portfolio 2', 
      value: 89230.00, 
      change: 481.64, 
      changePercent: 0.54 
    },
    'portfolio-3': { 
      name: 'Portfolio 3', 
      value: 205890.00, 
      change: 2828.36, 
      changePercent: 1.39 
    },
    'htech-15t': { 
      name: 'HTech 15T', 
      value: 139902.60, 
      change: 111.80, 
      changePercent: 0.28 
    }
  };

  const currentPortfolio = portfolioData[portfolioId] || portfolioData['htech-15t'];

  // Holdings data
  const holdings = [
    { symbol: 'YOU', price: 33.58, change: -0.42, changePercent: -1.24, weight: '-', volume: '1.90M', avgVol: '1.59M', prevClose: 34.00, open: 33.76, dayRange: '33.44-34.12', week52Range: '21.87-36.85', quantRating: 3.94, saRating: 4.00, wsRating: 3.37 },
    { symbol: 'V5AT', price: 25.97, change: -0.11, changePercent: -0.42, weight: '-', volume: '3.03M', avgVol: '4.11M', prevClose: 26.08, open: 25.70, dayRange: '25.50-26.18', week52Range: '9.09-26.59', quantRating: 4.90, saRating: 4.00, wsRating: 3.55 },
    { symbol: 'SPNS', price: 42.71, change: 0.07, changePercent: 0.16, weight: '-', volume: '1.18M', avgVol: '679.587', prevClose: 42.64, open: 42.63, dayRange: '42.57-42.75', week52Range: '23.89-42.76', quantRating: 3.00, saRating: 3.00, wsRating: 2.75 },
    { symbol: 'BILL', price: 41.65, change: 0.31, changePercent: 0.75, weight: '1.49%', volume: '5.07M', avgVol: '2.26M', prevClose: 41.34, open: 41.25, dayRange: '40.52-41.78', week52Range: '36.56-100.19', quantRating: 2.67, saRating: 3.75, wsRating: 3.81 },
    { symbol: 'WDAY', price: 227.49, change: -2.30, changePercent: -1.00, weight: '2.44%', volume: '3.97M', avgVol: '2.67M', prevClose: 229.79, open: 229.18, dayRange: '227.13-231.72', week52Range: '205.33-294.00', quantRating: 3.32, saRating: 3.60, wsRating: 4.23 },
    { symbol: 'FTNT', price: 79.51, change: 1.52, changePercent: 1.95, weight: '2.85%', volume: '12.24M', avgVol: '6.23M', prevClose: 78.09, open: 78.09, dayRange: '77.90-80.30', week52Range: '70.12-114.82', quantRating: 3.26, saRating: 3.91, wsRating: 3.31 },
    { symbol: 'CHKP', price: 189.29, change: 1.29, changePercent: 0.69, weight: '2.71%', volume: '776.241', avgVol: '886.661', prevClose: 188.00, open: 188.72, dayRange: '186.86-190.00', week52Range: '169.02-234.38', quantRating: 3.05, saRating: 3.06, wsRating: 3.73 },
    { symbol: 'ADBE', price: 353.43, change: -7.60, changePercent: -2.11, weight: '2.53%', volume: '3.72M', avgVol: '3.78M', prevClose: 361.03, open: 361.68, dayRange: '353.30-363.00', week52Range: '330.54-587.75', quantRating: 3.37, saRating: 4.16, wsRating: 4.05 },
    { symbol: 'IT', price: 244.20, change: 1.32, changePercent: 0.54, weight: '4.36%', volume: '1.30M', avgVol: '1.11M', prevClose: 242.88, open: 243.18, dayRange: '242.55-246.76', week52Range: '222.85-554.01', quantRating: 1.13, saRating: 4.00, wsRating: 1.50 },
    { symbol: 'ON', price: 49.47, change: -0.30, changePercent: -0.60, weight: '1.77%', volume: '10.33M', avgVol: '9.80M', prevClose: 49.77, open: 49.67, dayRange: '48.31-49.99', week52Range: '31.04-78.61', quantRating: 2.92, saRating: 3.40, wsRating: 3.78 },
    { symbol: 'ASGN', price: 51.57, change: -1.06, changePercent: -2.01, weight: '1.84%', volume: '392.933', avgVol: '555.364', prevClose: 52.63, open: 52.70, dayRange: '51.39-53.10', week52Range: '46.64-101.66', quantRating: 2.02, saRating: 2.00, wsRating: 3.28 },
    { symbol: 'TXN', price: 200.77, change: 4.83, changePercent: 2.47, weight: '2.87%', volume: '8.10M', avgVol: '6.69M', prevClose: 195.94, open: 197.50, dayRange: '193.45-201.23', week52Range: '139.95-221.09', quantRating: 3.16, saRating: 3.11, wsRating: 3.55 },
    { symbol: 'SWKS', price: 75.12, change: 0.19, changePercent: 0.25, weight: '1.88%', volume: '2.39M', avgVol: '3.01M', prevClose: 74.93, open: 74.81, dayRange: '73.86-75.29', week52Range: '47.82-110.76', quantRating: 3.32, saRating: 3.50, wsRating: 2.92 },
    { symbol: 'MCHP', price: 66.76, change: 2.05, changePercent: 3.17, weight: '1.43%', volume: '10.21M', avgVol: '9.06M', prevClose: 64.71, open: 65.00, dayRange: '63.68-66.91', week52Range: '34.13-92.87', quantRating: 3.80, saRating: 2.50, wsRating: 4.32 },
    { symbol: 'QLYS', price: 132.11, change: -0.99, changePercent: -0.74, weight: '2.36%', volume: '298.992', avgVol: '320.296', prevClose: 133.10, open: 133.28, dayRange: '131.35-133.57', week52Range: '112.91-170.50', quantRating: 3.30, saRating: 3.00, wsRating: 3.17 }
  ];

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
          <div className="flex items-center space-x-3">
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
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { X, Search, GripVertical } from 'lucide-react';

const CreateNewView = () => {
  const navigate = useNavigate();
  const { portfolioId } = useParams();
  const [activeTab, setActiveTab] = useState('add');
  const [viewName, setViewName] = useState('My View 1');
  const [filterTerm, setFilterTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Holdings');

  const [selectedColumns, setSelectedColumns] = useState([
    { id: 'symbol', name: 'Symbol', locked: true },
    { id: 'price', name: 'Price', locked: false },
    { id: 'change', name: 'Change', locked: false },
    { id: 'change_percent', name: 'Change %', locked: false }
  ]);

  const categories = [
    'ETL Grades',
    'Holdings',
    'After Hours',
    'Earnings',
    'Dividends',
    'Valuation',
    'Growth',
    'Performance',
    'Momentum',
    'Profitability',
    'Ownership',
    'Debt'
  ];

  const availableColumnsByCategory = {
    'Holdings': [
      { id: 'change_percent', name: 'Change %', selected: true },
      { id: 'company_sector', name: 'Company / Fund Sector', selected: false },
      { id: 'company_industry', name: 'Company Industry / Fund Sub Class', selected: false },
      { id: 'volume', name: 'Volume', selected: false },
      { id: 'avg_volume', name: 'Average Volume', selected: false },
      { id: 'prev_close', name: 'Previous Close', selected: false },
      { id: 'open', name: 'Open', selected: false },
      { id: 'day_range', name: 'Day Range', selected: false },
      { id: 'week_52_range', name: '52 Week Range', selected: false },
      { id: 'expense_ratio', name: 'Expense Ratio', selected: false }
    ],
    'Valuation': [
      { id: 'pe_ratio', name: 'P/E Ratio', selected: false },
      { id: 'pb_ratio', name: 'P/B Ratio', selected: false },
      { id: 'ps_ratio', name: 'P/S Ratio', selected: false },
      { id: 'peg_ratio', name: 'PEG Ratio', selected: false },
      { id: 'market_cap', name: 'Market Cap', selected: false },
      { id: 'enterprise_value', name: 'Enterprise Value', selected: false }
    ],
    'Performance': [
      { id: 'ytd_return', name: 'YTD Return', selected: false },
      { id: 'one_year_return', name: '1 Year Return', selected: false },
      { id: 'three_year_return', name: '3 Year Return', selected: false },
      { id: 'five_year_return', name: '5 Year Return', selected: false },
      { id: 'beta', name: 'Beta', selected: false },
      { id: 'volatility', name: 'Volatility', selected: false }
    ],
    'Dividends': [
      { id: 'dividend_yield', name: 'Dividend Yield', selected: false },
      { id: 'dividend_rate', name: 'Dividend Rate', selected: false },
      { id: 'payout_ratio', name: 'Payout Ratio', selected: false },
      { id: 'ex_dividend_date', name: 'Ex-Dividend Date', selected: false },
      { id: 'dividend_growth', name: 'Dividend Growth', selected: false }
    ],
    'Growth': [
      { id: 'revenue_growth', name: 'Revenue Growth', selected: false },
      { id: 'earnings_growth', name: 'Earnings Growth', selected: false },
      { id: 'book_value_growth', name: 'Book Value Growth', selected: false },
      { id: 'sales_growth', name: 'Sales Growth', selected: false }
    ],
    'Profitability': [
      { id: 'roe', name: 'Return on Equity (ROE)', selected: false },
      { id: 'roa', name: 'Return on Assets (ROA)', selected: false },
      { id: 'gross_margin', name: 'Gross Margin', selected: false },
      { id: 'operating_margin', name: 'Operating Margin', selected: false },
      { id: 'net_margin', name: 'Net Margin', selected: false }
    ]
  };

  const getCurrentColumns = () => {
    const categoryColumns = availableColumnsByCategory[selectedCategory] || [];
    if (filterTerm) {
      return categoryColumns.filter(col => 
        col.name.toLowerCase().includes(filterTerm.toLowerCase())
      );
    }
    return categoryColumns;
  };

  const handleColumnToggle = (column) => {
    const isSelected = selectedColumns.some(col => col.id === column.id);
    
    if (isSelected) {
      // Remove from selected
      setSelectedColumns(prev => prev.filter(col => col.id !== column.id));
    } else {
      // Add to selected
      setSelectedColumns(prev => [...prev, { 
        id: column.id, 
        name: column.name, 
        locked: false 
      }]);
    }
  };

  const removeColumn = (columnId) => {
    setSelectedColumns(prev => prev.filter(col => col.id !== columnId));
  };

  const handleDone = () => {
    // Save the view configuration and navigate back
    navigate(`/portfolios/${portfolioId}`, { 
      state: { 
        newView: {
          name: viewName,
          columns: selectedColumns
        }
      } 
    });
  };

  const handleCancel = () => {
    navigate(`/portfolios/${portfolioId}`);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <h1 className="text-3xl font-medium text-gray-800">Create a New View</h1>
        <button
          onClick={handleCancel}
          className="text-lg font-medium text-gray-600 hover:text-gray-800"
        >
          Cancel
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-8 px-6">
          <button
            onClick={() => setActiveTab('add')}
            className={`py-4 px-2 font-medium text-lg ${
              activeTab === 'add'
                ? 'border-b-2 border-black text-black'
                : 'text-gray-500'
            }`}
          >
            Add New View
          </button>
          <button
            onClick={() => setActiveTab('edit')}
            className={`py-4 px-2 font-medium text-lg ${
              activeTab === 'edit'
                ? 'border-b-2 border-black text-black'
                : 'text-gray-500'
            }`}
          >
            Edit Views
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        
        {/* View Name */}
        <div className="mb-6">
          <label className="block text-gray-600 text-lg mb-3">View name:</label>
          <input
            type="text"
            value={viewName}
            onChange={(e) => setViewName(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-lg"
          />
        </div>

        {/* Filter */}
        <div className="mb-6">
          <label className="block text-gray-600 text-lg mb-3">Filter:</label>
          <div className="relative">
            <input
              type="text"
              value={filterTerm}
              onChange={(e) => setFilterTerm(e.target.value)}
              placeholder="Filter by column name"
              className="w-full px-4 py-3 pr-12 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-lg"
            />
            <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
          </div>
        </div>

        {/* Three Column Layout */}
        <div className="grid grid-cols-3 gap-6 h-96">
          
          {/* Categories */}
          <div>
            <h3 className="text-lg font-medium text-gray-600 mb-4">Category</h3>
            <div className="bg-gray-50 border rounded-lg h-full overflow-y-auto">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-100 ${
                    selectedCategory === category ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* Available Columns */}
          <div>
            <h3 className="text-lg font-medium text-gray-600 mb-4">Available Columns</h3>
            <div className="bg-gray-50 border rounded-lg h-full overflow-y-auto p-4">
              {getCurrentColumns().map((column) => {
                const isSelected = selectedColumns.some(col => col.id === column.id);
                
                return (
                  <div key={column.id} className="flex items-center mb-3">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleColumnToggle(column)}
                      className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
                    />
                    <label className="ml-3 text-gray-700 cursor-pointer">
                      {column.name}
                    </label>
                    {isSelected && (
                      <div className="ml-2 w-2 h-2 bg-green-500 rounded-full"></div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Columns */}
          <div>
            <h3 className="text-lg font-medium text-gray-600 mb-4">
              Selected Columns ({selectedColumns.length}/40)
            </h3>
            <div className="bg-gray-50 border rounded-lg h-full overflow-y-auto p-4">
              {selectedColumns.map((column, index) => (
                <div
                  key={column.id}
                  className="flex items-center justify-between mb-3 p-2 bg-white border rounded hover:bg-gray-50"
                >
                  <div className="flex items-center">
                    {column.locked ? (
                      <div className="w-5 h-5 flex items-center justify-center">
                        <div className="w-3 h-3 bg-gray-400 rounded-sm"></div>
                      </div>
                    ) : (
                      <GripVertical className="text-gray-400 cursor-move" size={16} />
                    )}
                    <span className="ml-3 text-gray-700">{column.name}</span>
                  </div>
                  {!column.locked && (
                    <button
                      onClick={() => removeColumn(column.id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Done Button */}
        <div className="mt-8">
          <button
            onClick={handleDone}
            className="w-full bg-black text-white text-xl font-semibold py-4 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateNewView;
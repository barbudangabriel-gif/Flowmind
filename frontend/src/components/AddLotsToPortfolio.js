import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Plus, Trash2 } from 'lucide-react';

const AddLotsToPortfolio = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { symbols = [] } = location.state || {};
  
  const [portfolioData, setPortfolioData] = useState([]);
  const [cashBalance, setCashBalance] = useState(0);

  // Mock current prices
  const getCurrentPrice = (symbol) => {
    const prices = {
      'TSL': 13.00,
      'TSLA': 245.80,
      'AAPL': 230.56,
      'MSFT': 415.23,
      'GOOGL': 162.84,
      'AMZN': 186.50,
      'META': 520.45,
      'NVDA': 138.92
    };
    return prices[symbol.toUpperCase()] || 100.00;
  };

  // Initialize portfolio data with current prices and today's date
  useEffect(() => {
    if (symbols.length > 0) {
      const today = new Date().toISOString().split('T')[0].replace(/-/g, '/').replace(/(\d{4})\/(\d{2})\/(\d{2})/, '$2/$3/$1');
      
      const initialData = symbols.map(symbol => ({
        id: Math.random().toString(36).substr(2, 9),
        symbol: symbol.symbol || symbol,
        shares: '',
        date: today,
        cost: getCurrentPrice(symbol.symbol || symbol),
        lots: [{ 
          id: Math.random().toString(36).substr(2, 9),
          shares: '', 
          date: today, 
          cost: getCurrentPrice(symbol.symbol || symbol) 
        }]
      }));
      
      setPortfolioData(initialData);
    }
  }, [symbols]);

  const handleSkip = () => {
    // Skip lots entry and create portfolio with just symbols
    const portfolioWithDefaults = portfolioData.map(item => ({
      ...item,
      shares: 0,
      totalValue: 0
    }));
    
    navigate('/portfolios', { 
      state: { 
        newPortfolio: { 
          name: 'Portfolio 4',
          holdings: portfolioWithDefaults,
          cashBalance: cashBalance || 0,
          totalValue: cashBalance || 0
        } 
      } 
    });
  };

  const updateLot = (symbolIndex, lotIndex, field, value) => {
    setPortfolioData(prev => {
      const updated = [...prev];
      if (lotIndex === undefined) {
        // Update main row
        updated[symbolIndex][field] = value;
      } else {
        // Update specific lot
        updated[symbolIndex].lots[lotIndex][field] = value;
      }
      return updated;
    });
  };

  const addLot = (symbolIndex) => {
    setPortfolioData(prev => {
      const updated = [...prev];
      const newLot = {
        id: Math.random().toString(36).substr(2, 9),
        shares: '',
        date: new Date().toISOString().split('T')[0].replace(/-/g, '/').replace(/(\d{4})\/(\d{2})\/(\d{2})/, '$2/$3/$1'),
        cost: updated[symbolIndex].cost
      };
      updated[symbolIndex].lots.push(newLot);
      return updated;
    });
  };

  const deleteLot = (symbolIndex, lotIndex) => {
    setPortfolioData(prev => {
      const updated = [...prev];
      if (updated[symbolIndex].lots.length > 1) {
        updated[symbolIndex].lots.splice(lotIndex, 1);
      }
      return updated;
    });
  };

  const deleteSymbol = (symbolIndex) => {
    setPortfolioData(prev => prev.filter((_, index) => index !== symbolIndex));
  };

  const handleSave = () => {
    // Calculate portfolio totals
    const totalValue = portfolioData.reduce((total, item) => {
      const symbolTotal = item.lots.reduce((symbolSum, lot) => {
        const shares = parseFloat(lot.shares) || 0;
        const cost = parseFloat(lot.cost) || 0;
        return symbolSum + (shares * cost);
      }, 0);
      return total + symbolTotal;
    }, 0);

    const portfolioSummary = {
      name: 'Portfolio 4',
      holdings: portfolioData.map(item => ({
        symbol: item.symbol,
        totalShares: item.lots.reduce((sum, lot) => sum + (parseFloat(lot.shares) || 0), 0),
        averageCost: item.lots.reduce((sum, lot) => sum + (parseFloat(lot.cost) || 0), 0) / item.lots.length,
        totalValue: item.lots.reduce((sum, lot) => sum + ((parseFloat(lot.shares) || 0) * (parseFloat(lot.cost) || 0)), 0),
        lots: item.lots
      })),
      cashBalance: parseFloat(cashBalance) || 0,
      totalValue: totalValue + (parseFloat(cashBalance) || 0)
    };

    // Navigate to All Portfolios with success message
    navigate('/portfolios', { 
      state: { 
        newPortfolio: portfolioSummary,
        message: `Portfolio "${portfolioSummary.name}" created successfully!`
      } 
    });
  };

  if (symbols.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">No Symbols Selected</h2>
          <p className="text-gray-600 mb-6">Please go back and select symbols first.</p>
          <button
            onClick={() => navigate('/portfolios/create/manual')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Symbol Selection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      {/* Modal Container */}
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl relative max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between p-8 pb-4 flex-shrink-0">
          <h1 className="text-3xl font-bold text-gray-800">Add Lots</h1>
          <button
            onClick={handleSkip}
            className="text-2xl font-bold text-gray-600 hover:text-gray-800 transition-colors"
          >
            Skip
          </button>
        </div>

        {/* Subtitle */}
        <div className="px-8 pb-6 flex-shrink-0">
          <p className="text-gray-600">
            If you do not wish to enter shares click "Skip" and the below symbols will be added to your portfolio.
          </p>
        </div>

        {/* Table Header */}
        <div className="px-8 flex-shrink-0">
          <div className="grid grid-cols-12 gap-4 text-gray-600 font-medium text-lg mb-4">
            <div className="col-span-2"></div>
            <div className="col-span-2 text-center"># of Shares</div>
            <div className="col-span-2 text-center">Date</div>
            <div className="col-span-2 text-center">Cost</div>
            <div className="col-span-2 text-center">+ Lot</div>
            <div className="col-span-2 text-center">Del</div>
          </div>
        </div>

        {/* Content - Scrollable */}
        <div className="px-8 flex-1 overflow-y-auto">
          <div className="space-y-6">
            {portfolioData.map((item, symbolIndex) => (
              <div key={item.id} className="space-y-3">
                {/* Symbol Row */}
                <div className="grid grid-cols-12 gap-4 items-center">
                  <div className="col-span-2">
                    <div className="text-2xl font-bold text-gray-800">{item.symbol}</div>
                  </div>
                  <div className="col-span-2">
                    <input
                      type="number"
                      value={item.lots[0].shares}
                      onChange={(e) => updateLot(symbolIndex, 0, 'shares', e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center text-lg"
                      placeholder="0"
                    />
                  </div>
                  <div className="col-span-2">
                    <input
                      type="text"
                      value={item.lots[0].date}
                      onChange={(e) => updateLot(symbolIndex, 0, 'date', e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center text-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <input
                      type="number"
                      value={item.lots[0].cost}
                      onChange={(e) => updateLot(symbolIndex, 0, 'cost', e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center text-lg"
                      step="0.01"
                    />
                  </div>
                  <div className="col-span-2 flex justify-center">
                    <button
                      onClick={() => addLot(symbolIndex)}
                      className="p-3 text-gray-600 hover:text-blue-600 transition-colors"
                    >
                      <Plus size={24} />
                    </button>
                  </div>
                  <div className="col-span-2 flex justify-center">
                    <button
                      onClick={() => deleteSymbol(symbolIndex)}
                      className="p-3 text-gray-600 hover:text-red-600 transition-colors"
                    >
                      <Trash2 size={24} />
                    </button>
                  </div>
                </div>

                {/* Additional Lots */}
                {item.lots.slice(1).map((lot, lotIndex) => (
                  <div key={lot.id} className="grid grid-cols-12 gap-4 items-center ml-8">
                    <div className="col-span-2"></div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        value={lot.shares}
                        onChange={(e) => updateLot(symbolIndex, lotIndex + 1, 'shares', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center"
                        placeholder="0"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="text"
                        value={lot.date}
                        onChange={(e) => updateLot(symbolIndex, lotIndex + 1, 'date', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        value={lot.cost}
                        onChange={(e) => updateLot(symbolIndex, lotIndex + 1, 'cost', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center"
                        step="0.01"
                      />
                    </div>
                    <div className="col-span-2"></div>
                    <div className="col-span-2 flex justify-center">
                      <button
                        onClick={() => deleteLot(symbolIndex, lotIndex + 1)}
                        className="p-3 text-gray-600 hover:text-red-600 transition-colors"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Section */}
        <div className="px-8 py-6 flex-shrink-0 border-t border-gray-200 mt-6">
          {/* Cash Balance */}
          <div className="flex items-center justify-between mb-6">
            <div className="text-xl font-medium text-gray-700">Cash Balance In Portfolio</div>
            <div className="w-64">
              <input
                type="number"
                value={cashBalance}
                onChange={(e) => setCashBalance(e.target.value)}
                className="w-full px-6 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none text-center text-lg"
                placeholder="0"
                step="0.01"
              />
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            className="w-full py-4 bg-gray-600 text-white text-xl font-semibold rounded-xl hover:bg-gray-700 transition-colors"
          >
            Save
          </button>
        </div>
      </div>

      {/* Background Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-50 -z-10"></div>
    </div>
  );
};

export default AddLotsToPortfolio;
// Simplified table implementation for Live Portfolio
// Every position gets a dropdown with simple expand/collapse functionality

const SimplePortfolioTable = () => {
  return (
    <tbody className={`${isDarkMode ? 'text-gray-200' : 'text-gray-800'}`} style={{ minHeight: '600px' }}>
      {(() => {
        const filteredPositions = filterPositionsByAsset(portfolioData.positions);
        
        return filteredPositions.map((position, index) => {
          const positionKey = `pos-${index}`;
          const isExpanded = expandedSymbols.has(positionKey);
          
          return (
            <React.Fragment key={positionKey}>
              {/* Main Position Row */}
              <tr className="bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-750 hover:to-gray-850 transition-all duration-200 border-b border-gray-600">
                {/* Symbol Column with Dropdown */}
                <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
                  <div className="flex items-center gap-1">
                    <button 
                      className="text-gray-400 hover:text-gray-200 transition-colors flex-shrink-0"
                      onClick={() => {
                        console.log(`Toggle dropdown for ${position.symbol} (Position #${index + 1})`);
                        toggleSymbolExpansion(positionKey);
                      }}
                    >
                      <div className={`ts-double-arrow ${isExpanded ? 'expanded' : ''}`}></div>
                    </button>
                    
                    <div className="flex flex-col min-w-0 flex-1">
                      <span className="font-semibold text-blue-300 text-sm truncate">{position.symbol}</span>
                      <span className="text-xs text-gray-400 uppercase truncate">
                        {position.asset_type || 'POSITION'} #{index + 1}
                      </span>
                    </div>
                  </div>
                </td>
                
                {/* Description Column */}
                <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
                  <div className="text-sm text-gray-300 truncate">
                    {position.description || `${position.symbol} Position`}
                  </div>
                </td>
                
                {/* Position Column */}
                <td className="px-3 py-2 text-center border-r border-gray-600 w-24 min-w-24">
                  <div className="flex flex-col items-center">
                    <span className={`text-xs font-medium px-1 py-0.5 rounded ${position.quantity > 0 ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'}`}>
                      {position.quantity > 0 ? 'LONG' : 'SHORT'}
                    </span>
                    <span className="text-sm font-medium text-gray-200">{Math.abs(position.quantity)}</span>
                  </div>
                </td>
                
                {/* Open P&L */}
                <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-28 min-w-28 ${getPnlColor(position.unrealized_pnl)} truncate`}>
                  {position.unrealized_pnl > 0 ? '+' : ''}{formatCurrency(position.unrealized_pnl)}
                </td>
                
                {/* Average Price */}
                <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-gray-200 truncate">
                  {formatCurrency(position.average_price)}
                </td>
                
                {/* Today's Open P/L */}
                <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 ${getPnlColor(position.daily_pnl || 0)} truncate`}>
                  {(position.daily_pnl || 0) > 0 ? '+' : ''}{formatCurrency(position.daily_pnl || 0)}
                </td>
                
                {/* Open P/L Qty */}
                <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-gray-200 truncate">
                  {formatNumber(Math.abs(position.quantity))}
                </td>
                
                {/* Open P&L % */}
                <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-24 min-w-24 ${getPnlColor(position.unrealized_pnl_percent)} truncate`}>
                  {position.unrealized_pnl_percent > 0 ? '+' : ''}{formatPercent(position.unrealized_pnl_percent)}
                </td>
                
                {/* Total Cost */}
                <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-28 min-w-28 text-gray-200 truncate">
                  {formatCurrency(calculateTotalCost(position))}
                </td>
                
                {/* Market Value */}
                <td className="px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 text-gray-200 truncate">
                  {formatCurrency(position.market_value)}
                </td>
                
                {/* Quantity */}
                <td className="px-3 py-2 text-center font-medium w-20 min-w-20 text-gray-200 truncate">
                  {formatNumber(Math.abs(position.quantity))}
                </td>
              </tr>
              
              {/* Expanded Details Row */}
              {isExpanded && (
                <tr className="bg-gradient-to-r from-gray-700 to-gray-800 border-b border-gray-600">
                  <td colSpan="11" className="px-6 py-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="bg-gray-600 p-3 rounded">
                        <div className="text-gray-300 mb-1">📊 Position Details</div>
                        <div className="text-white font-semibold">#{index + 1} of {filteredPositions.length}</div>
                        <div className="text-gray-400 text-xs">Index: {index}</div>
                      </div>
                      
                      <div className="bg-gray-600 p-3 rounded">
                        <div className="text-gray-300 mb-1">💰 Financial Data</div>
                        <div className="text-white font-semibold">{formatCurrency(position.market_value)}</div>
                        <div className={`text-xs ${getPnlColor(position.unrealized_pnl)}`}>
                          P&L: {position.unrealized_pnl > 0 ? '+' : ''}{formatCurrency(position.unrealized_pnl)}
                        </div>
                      </div>
                      
                      <div className="bg-gray-600 p-3 rounded">
                        <div className="text-gray-300 mb-1">📈 Performance</div>
                        <div className={`text-white font-semibold ${getPnlColor(position.unrealized_pnl_percent)}`}>
                          {position.unrealized_pnl_percent > 0 ? '+' : ''}{formatPercent(position.unrealized_pnl_percent)}
                        </div>
                        <div className="text-gray-400 text-xs">Return %</div>
                      </div>
                      
                      <div className="bg-gray-600 p-3 rounded">
                        <div className="text-gray-300 mb-1">🔢 Quantity Info</div>
                        <div className="text-white font-semibold">{Math.abs(position.quantity)} shares</div>
                        <div className="text-gray-400 text-xs">
                          {position.quantity > 0 ? 'Long Position' : 'Short Position'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 pt-3 border-t border-gray-500">
                      <div className="text-xs text-gray-400">
                        Asset Type: {position.asset_type || 'N/A'} | 
                        Avg Price: {formatCurrency(position.average_price)} | 
                        Symbol: {position.symbol}
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          );
        });
      })()}
    </tbody>
  );
};
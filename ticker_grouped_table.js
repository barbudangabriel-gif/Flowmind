// New table implementation with proper ticker grouping
// Each ticker gets a dropdown if it has multiple positions

const renderTickerGroupedTable = () => {
  const filteredPositions = filterPositionsByAsset(mindfolioData.positions);
  const groupedByTicker = groupPositionsByTicker(filteredPositions);
  
  const rows = [];
  
  // Iterate through each ticker group
  Object.entries(groupedByTicker).forEach(([ticker, group]) => {
    const isExpanded = expandedSymbols.has(ticker);
    const { positions, hasMultiplePositions } = group;
    
    if (hasMultiplePositions) {
      // TICKER GROUP WITH MULTIPLE POSITIONS - Show header row with dropdown
      const totalMarketValue = positions.reduce((sum, pos) => sum + pos.market_value, 0);
      const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0);
      const totalPositions = positions.length;
      
      // Ticker header row
      rows.push(
        <tr 
          key={`ticker-${ticker}`}
          className="bg-gradient-to-r from-blue-900 to-blue-800 hover:from-blue-850 hover:to-blue-750 transition-all duration-200 border-b-2 border-blue-600"
        >
          {/* Ticker Symbol Column with Dropdown */}
          <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
            <div className="flex items-center gap-1">
              <button 
                className="text-gray-300 hover:text-[rgb(252, 251, 255)] transition-colors flex-shrink-0"
                onClick={() => {
                  console.log(`Toggle ${ticker} positions (${totalPositions} positions)`);
                  toggleSymbolExpansion(ticker);
                }}
              >
                <div className={`ts-double-arrow ${isExpanded ? 'expanded' : ''}`}></div>
              </button>
              
              <div className="flex flex-col min-w-0 flex-1">
                <span className="font-bold text-[rgb(252, 251, 255)] text-base truncate">{ticker}</span>
                <span className="text-xs text-blue-200 truncate">
                  {totalPositions} positions {isExpanded ? '▼' : '▶'}
                </span>
              </div>
            </div>
          </td>
          
          {/* Ticker Summary Columns */}
          <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
            <div className="text-sm text-blue-100 truncate">
              {ticker} Group Summary
            </div>
          </td>
          
          <td className="px-3 py-2 text-center border-r border-gray-600 w-24 min-w-24">
            <div className="text-sm font-medium text-blue-100">{totalPositions}</div>
          </td>
          
          <td className={`px-3 py-2 text-right font-bold border-r border-gray-600 w-28 min-w-28 ${getPnlColor(totalPnL)} truncate`}>
            {totalPnL > 0 ? '+' : ''}{formatCurrency(totalPnL)}
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-blue-100 truncate">
            Combined
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-32 min-w-32 text-blue-100 truncate">
            Group Total
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-blue-100 truncate">
            -
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-blue-100 truncate">
            -
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-28 min-w-28 text-blue-100 truncate">
            -
          </td>
          
          <td className="px-3 py-2 text-right font-bold border-r border-gray-600 w-32 min-w-32 text-blue-100 truncate">
            {formatCurrency(totalMarketValue)}
          </td>
          
          <td className="px-3 py-2 text-center font-medium w-20 min-w-20 text-blue-100 truncate">
            {totalPositions}
          </td>
        </tr>
      );
      
      // Individual positions (shown when expanded)
      if (isExpanded) {
        positions.forEach((position, posIndex) => {
          rows.push(
            <tr 
              key={`${ticker}-pos-${posIndex}`}
              className="bg-gradient-to-r from-gray-750 to-gray-800 hover:from-gray-700 hover:to-gray-750 transition-all duration-200 border-b border-gray-600 border-l-4 border-l-blue-400"
            >
              {/* Individual Position Symbol (indented) */}
              <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
                <div className="flex items-center gap-1 pl-6">
                  <div className="flex flex-col min-w-0 flex-1">
                    <span className="font-semibold text-cyan-300 text-sm truncate">{position.symbol}</span>
                    <span className="text-xs text-gray-500 uppercase truncate">
                      {position.asset_type || 'POSITION'}
                    </span>
                  </div>
                </div>
              </td>
              
              {/* Standard position columns */}
              <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
                <div className="text-sm text-gray-300 truncate">
                  {position.description || `${position.symbol} Position`}
                </div>
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
              
              <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-gray-200 truncate">
                {formatCurrency(position.average_price)}
              </td>
              
              <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 ${getPnlColor(position.daily_pnl || 0)} truncate`}>
                {(position.daily_pnl || 0) > 0 ? '+' : ''}{formatCurrency(position.daily_pnl || 0)}
              </td>
              
              <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-gray-200 truncate">
                {formatNumber(Math.abs(position.quantity))}
              </td>
              
              <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-24 min-w-24 ${getPnlColor(position.unrealized_pnl_percent)} truncate`}>
                {position.unrealized_pnl_percent > 0 ? '+' : ''}{formatPercent(position.unrealized_pnl_percent)}
              </td>
              
              <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-28 min-w-28 text-gray-200 truncate">
                {formatCurrency(calculateTotalCost(position))}
              </td>
              
              <td className="px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 text-gray-200 truncate">
                {formatCurrency(position.market_value)}
              </td>
              
              <td className="px-3 py-2 text-center font-medium w-20 min-w-20 text-gray-200 truncate">
                {formatNumber(Math.abs(position.quantity))}
              </td>
            </tr>
          );
        });
      }
      
    } else {
      // SINGLE POSITION - No dropdown, show directly
      const position = positions[0];
      
      rows.push(
        <tr 
          key={`single-${ticker}`}
          className="bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-750 hover:to-gray-850 transition-all duration-200 border-b border-gray-600"
        >
          {/* Single Position Symbol (no dropdown) */}
          <td className="px-3 py-2 border-r border-gray-600 w-32 min-w-32">
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 flex-shrink-0"></div> {/* Spacer for alignment */}
              
              <div className="flex flex-col min-w-0 flex-1">
                <span className="font-semibold text-blue-300 text-sm truncate">{position.symbol}</span>
                <span className="text-xs text-gray-400 uppercase truncate">
                  {position.asset_type || 'SINGLE'}
                </span>
              </div>
            </div>
          </td>
          
          {/* Standard single position columns */}
          <td className="px-3 py-2 text-left border-r border-gray-600 w-48 min-w-48">
            <div className="text-sm text-gray-300 truncate">
              {position.description || `${position.symbol} Position`}
            </div>
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
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-gray-200 truncate">
            {formatCurrency(position.average_price)}
          </td>
          
          <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 ${getPnlColor(position.daily_pnl || 0)} truncate`}>
            {(position.daily_pnl || 0) > 0 ? '+' : ''}{formatCurrency(position.daily_pnl || 0)}
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-24 min-w-24 text-gray-200 truncate">
            {formatNumber(Math.abs(position.quantity))}
          </td>
          
          <td className={`px-3 py-2 text-right font-semibold border-r border-gray-600 w-24 min-w-24 ${getPnlColor(position.unrealized_pnl_percent)} truncate`}>
            {position.unrealized_pnl_percent > 0 ? '+' : ''}{formatPercent(position.unrealized_pnl_percent)}
          </td>
          
          <td className="px-3 py-2 text-right font-medium border-r border-gray-600 w-28 min-w-28 text-gray-200 truncate">
            {formatCurrency(calculateTotalCost(position))}
          </td>
          
          <td className="px-3 py-2 text-right font-semibold border-r border-gray-600 w-32 min-w-32 text-gray-200 truncate">
            {formatCurrency(position.market_value)}
          </td>
          
          <td className="px-3 py-2 text-center font-medium w-20 min-w-20 text-gray-200 truncate">
            {formatNumber(Math.abs(position.quantity))}
          </td>
        </tr>
      );
    }
  });
  
  return rows;
};
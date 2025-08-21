import React, { useState, useEffect } from 'react';
import { 
  ArrowRightLeft, 
  TrendingUp, 
  TrendingDown, 
  MoreHorizontal,
  Target,
  Clock,
  DollarSign
} from 'lucide-react';

const PositionContextMenu = ({ 
  position, 
  isVisible, 
  x, 
  y, 
  onClose, 
  onMovePosition,
  availablePortfolios = []
}) => {
  const [showMoveSubmenu, setShowMoveSubmenu] = useState(false);

  useEffect(() => {
    const handleClickOutside = () => {
      onClose();
    };

    if (isVisible) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isVisible, onClose]);

  if (!isVisible) return null;

  const handleMoveToPortfolio = (targetPortfolio) => {
    onMovePosition(position, targetPortfolio);
    onClose();
  };

  const getPortfolioIcon = (category) => {
    switch (category) {
      case 'long_term': return <Clock size={14} className="text-green-500" />;
      case 'medium_term': return <TrendingUp size={14} className="text-blue-500" />;
      case 'short_term': return <TrendingDown size={14} className="text-orange-500" />;
      default: return <Target size={14} className="text-purple-500" />;
    }
  };

  const getPnLColor = (pnl) => {
    return pnl >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div 
      className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg py-1 min-w-48"
      style={{ 
        left: Math.min(x, window.innerWidth - 200), 
        top: Math.min(y, window.innerHeight - 300) 
      }}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Position Info Header */}
      <div className="px-3 py-2 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-gray-900">{position.symbol}</span>
          <span className="text-xs text-gray-600">{position.quantity} shares</span>
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-sm text-gray-600">${position.current_price?.toFixed(2)}</span>
          <span className={`text-sm font-medium ${getPnLColor(position.unrealized_pnl)}`}>
            {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl?.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Move to Portfolio Option */}
      <div
        className="relative"
        onMouseEnter={() => setShowMoveSubmenu(true)}
        onMouseLeave={() => setShowMoveSubmenu(false)}
      >
        <button className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 text-gray-700">
          <ArrowRightLeft size={16} />
          <span>Move to Portfolio</span>
          <span className="ml-auto text-gray-400">›</span>
        </button>

        {/* Submenu for Portfolio Selection */}
        {showMoveSubmenu && availablePortfolios.length > 0 && (
          <div className="absolute left-full top-0 ml-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 min-w-56 z-60">
            <div className="px-3 py-1 text-xs font-medium text-gray-500 border-b border-gray-100">
              Select Destination Portfolio
            </div>
            {availablePortfolios.map((portfolio) => (
              <button
                key={portfolio.id}
                onClick={() => handleMoveToPortfolio(portfolio)}
                className="w-full px-3 py-2 text-left hover:bg-blue-50 flex items-center space-x-2"
              >
                {getPortfolioIcon(portfolio.category)}
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{portfolio.name}</div>
                  <div className="text-xs text-gray-600">{portfolio.description}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {portfolio.positions_count} positions • ${portfolio.total_value?.toLocaleString()}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Separator */}
      <div className="border-t border-gray-100 my-1"></div>

      {/* Additional Actions */}
      <button className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 text-gray-700">
        <DollarSign size={16} />
        <span>View Details</span>
      </button>

      <button className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 text-gray-700">
        <MoreHorizontal size={16} />
        <span>More Actions</span>
      </button>
    </div>
  );
};

export default PositionContextMenu;
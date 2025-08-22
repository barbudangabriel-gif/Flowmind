import React, { useState, useEffect } from 'react';
import { ArrowRight, Folder, X } from 'lucide-react';

const ContextMenu = ({ 
  isVisible, 
  position, 
  onClose, 
  selectedPosition,
  availablePortfolios,
  onMovePosition
}) => {
  const [isSubmenuOpen, setIsSubmenuOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isVisible) {
        onClose();
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isVisible) {
        onClose();
      }
    };

    if (isVisible) {
      document.addEventListener('click', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isVisible, onClose]);

  const handleMoveToPortfolio = async (portfolioId, portfolioName) => {
    setLoading(true);
    try {
      await onMovePosition(selectedPosition.id, portfolioId, portfolioName);
      onClose();
    } catch (error) {
      console.error('Error moving position:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <>
      {/* Main Context Menu */}
      <div 
        className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg min-w-48"
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="py-1">
          {/* Position Info Header */}
          <div className="px-4 py-2 border-b border-gray-100 bg-gray-50">
            <div className="text-sm font-medium text-gray-900">
              {selectedPosition?.symbol}
            </div>
            <div className="text-xs text-gray-500">
              {selectedPosition?.quantity} shares • ${selectedPosition?.market_value?.toFixed(2)}
            </div>
          </div>

          {/* Move to Portfolio Option */}
          <div 
            className="px-4 py-2 hover:bg-blue-50 cursor-pointer flex items-center justify-between group"
            onMouseEnter={() => setIsSubmenuOpen(true)}
            onMouseLeave={() => setIsSubmenuOpen(false)}
          >
            <div className="flex items-center">
              <Folder className="w-4 h-4 mr-2 text-gray-600 group-hover:text-blue-600" />
              <span className="text-sm text-gray-700 group-hover:text-blue-700">
                Move to Portfolio
              </span>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
          </div>

          {/* Other Context Menu Options (for future expansion) */}
          <div className="border-t border-gray-100">
            <div className="px-4 py-2 hover:bg-gray-50 cursor-pointer">
              <span className="text-sm text-gray-500">View Details</span>
            </div>
            <div className="px-4 py-2 hover:bg-gray-50 cursor-pointer">
              <span className="text-sm text-gray-500">Add Notes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Submenu for Portfolio Selection */}
      {isSubmenuOpen && (
        <div 
          className="fixed z-60 bg-white border border-gray-200 rounded-lg shadow-lg min-w-48"
          style={{
            left: `${position.x + 200}px`,
            top: `${position.y + 50}px`,
          }}
          onMouseEnter={() => setIsSubmenuOpen(true)}
          onMouseLeave={() => setIsSubmenuOpen(false)}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="py-1">
            {/* Submenu Header */}
            <div className="px-4 py-2 border-b border-gray-100 bg-gray-50">
              <div className="text-sm font-medium text-gray-900">
                Select Portfolio
              </div>
            </div>

            {/* Available Portfolios */}
            {availablePortfolios && availablePortfolios.length > 0 ? (
              availablePortfolios.map((portfolio) => (
                <div 
                  key={portfolio.id}
                  className="px-4 py-2 hover:bg-blue-50 cursor-pointer"
                  onClick={() => handleMoveToPortfolio(portfolio.id, portfolio.name)}
                >
                  <div className="flex items-center">
                    <Folder className="w-4 h-4 mr-2 text-blue-600" />
                    <div>
                      <div className="text-sm text-gray-900">{portfolio.name}</div>
                      <div className="text-xs text-gray-500">{portfolio.description}</div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-4 py-2 text-sm text-gray-500">
                No portfolios available
              </div>
            )}

            {/* Create New Portfolio Option */}
            <div className="border-t border-gray-100">
              <div className="px-4 py-2 hover:bg-green-50 cursor-pointer">
                <div className="flex items-center">
                  <div className="w-4 h-4 mr-2 rounded border-2 border-dashed border-green-400 flex items-center justify-center">
                    <span className="text-green-600 text-xs font-bold">+</span>
                  </div>
                  <span className="text-sm text-green-700">Create New Portfolio</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-20 z-70 flex items-center justify-center">
          <div className="bg-white rounded-lg p-4 shadow-lg">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
              <span className="text-sm text-gray-700">Moving position...</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ContextMenu;
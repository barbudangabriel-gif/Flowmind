import { useState, useEffect } from 'react';

const usePortfolioManagement = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [positions, setPositions] = useState([]);
  const [availablePortfolios, setAvailablePortfolios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch all portfolios
  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/portfolio-management/portfolios`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setPortfolios(data.portfolios);
      } else {
        throw new Error('Failed to fetch portfolios');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching portfolios:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch positions for a specific portfolio
  const fetchPortfolioPositions = async (portfolioId) => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/portfolio-management/portfolios/${portfolioId}/positions`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setPositions(data.positions);
        return data.positions;
      } else {
        throw new Error('Failed to fetch positions');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching positions:', err);
      return [];
    } finally {
      setLoading(false);
    }
  };

  // Fetch available portfolios for moving (excluding current portfolio)
  const fetchAvailablePortfolios = async (currentPortfolioId) => {
    try {
      const response = await fetch(`${backendUrl}/api/portfolio-management/available-portfolios/${currentPortfolioId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setAvailablePortfolios(data.available_portfolios);
        return data.available_portfolios;
      } else {
        throw new Error('Failed to fetch available portfolios');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching available portfolios:', err);
      return [];
    }
  };

  // Move a position to another portfolio
  const movePosition = async (positionId, toPortfolioId, quantityToMove = null, reason = "Manual move via context menu") => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/portfolio-management/move-position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          position_id: positionId,
          to_portfolio_id: toPortfolioId,
          quantity_to_move: quantityToMove,
          reason: reason
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Refresh positions after successful move
        return data.result;
      } else {
        throw new Error(data.result?.error || 'Failed to move position');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error moving position:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Create a new custom portfolio
  const createPortfolio = async (name, description = "", category = "custom") => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/portfolio-management/create-portfolio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          description,
          category
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Refresh portfolios after creation
        await fetchPortfolios();
        return data.portfolio;
      } else {
        throw new Error('Failed to create portfolio');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error creating portfolio:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get aggregate view of all portfolios
  const fetchAggregateView = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/portfolio-management/aggregate-view`);
      const data = await response.json();
      
      if (data.status === 'success') {
        return data.aggregate_data;
      } else {
        throw new Error('Failed to fetch aggregate view');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching aggregate view:', err);
      return null;
    }
  };

  // Get move history for a portfolio
  const fetchMoveHistory = async (portfolioId) => {
    try {
      const response = await fetch(`${backendUrl}/api/portfolio-management/move-history/${portfolioId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        return data.move_history;
      } else {
        throw new Error('Failed to fetch move history');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching move history:', err);
      return [];
    }
  };

  // Initialize portfolios on mount
  useEffect(() => {
    fetchPortfolios();
  }, []);

  return {
    // State
    portfolios,
    positions,
    availablePortfolios,
    loading,
    error,
    
    // Actions
    fetchPortfolios,
    fetchPortfolioPositions,
    fetchAvailablePortfolios,
    movePosition,
    createPortfolio,
    fetchAggregateView,
    fetchMoveHistory,
    
    // Utilities
    clearError: () => setError(null)
  };
};

export default usePortfolioManagement;
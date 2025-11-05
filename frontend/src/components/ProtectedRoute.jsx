import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = checking
  const location = useLocation();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('auth_token');
    const expires = localStorage.getItem('auth_expires');

    // No token or expired
    if (!token || !expires || Date.now() > parseInt(expires)) {
      setIsAuthenticated(false);
      return;
    }

    // Verify token with backend
    try {
      const response = await fetch(`${API}/api/auth/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        // Token invalid
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_email');
        localStorage.removeItem('auth_expires');
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
    }
  };

  // Still checking
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-[#0f1419] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="text-gray-400 mt-4">Authenticating...</p>
        </div>
      </div>
    );
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Authenticated - render children
  return children;
}

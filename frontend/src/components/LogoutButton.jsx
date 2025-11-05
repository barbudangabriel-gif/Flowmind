import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';

export default function LogoutButton() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear auth data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_email');
    localStorage.removeItem('auth_expires');
    
    // Redirect to login
    navigate('/login');
  };

  const email = localStorage.getItem('auth_email');

  return (
    <div className="flex items-center gap-3">
      {email && (
        <span className="text-sm text-gray-400 hidden md:inline">{email}</span>
      )}
      <button
        onClick={handleLogout}
        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
        title="Logout"
      >
        <LogOut size={18} />
        <span className="hidden md:inline">Logout</span>
      </button>
    </div>
  );
}

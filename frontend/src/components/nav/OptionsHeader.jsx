import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function OptionsHeader() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const Tab = ({ label, to, dropdown = false }) => {
    let active = false;
    
    // Determine active state based on current path
    if (to === 'build' && pathname === '/options/analytics') active = true;
    else if (to === 'optimize' && pathname === '/optimize') active = true;
    else if (to === 'flow' && pathname === '/flow') active = true;
    
    const base = 'px-3 py-2 rounded-xl border border-slate-800 hover:bg-slate-800 transition-colors text-slate-200';
    
    return (
      <button
        onClick={() => {
          if (to === 'build') navigate('/options/analytics');
          else if (to === 'optimize') navigate('/optimize');
          else if (to === 'flow') navigate('/flow');
        }}
        className={`${base} ${active ? 'bg-slate-800' : ''}`}
        title={label}
      >
        {label}{dropdown ? ' ▾' : ''}
      </button>
    );
  };

  // Only show this header on Options-related pages
  const shouldShowHeader = pathname === '/options/analytics' || pathname === '/optimize' || pathname === '/flow';
  
  // Debug logging - ALWAYS log
  console.log('🔥 OptionsHeader - pathname:', pathname, 'shouldShowHeader:', shouldShowHeader);
  
  // TEMPORARILY REMOVE the return null to see if it renders
  // if (!shouldShowHeader) return null;

  console.log('🎯 OptionsHeader rendering!');
  
  return (
    <div className="bg-slate-950 border-b border-slate-800 px-6 py-4">
      <div className="flex items-center gap-2">
        <Tab label="Build" to="build" dropdown />
        <Tab label="Optimize" to="optimize" />
        <Tab label="Flow" to="flow" />
      </div>
    </div>
  );
}
import React, { useEffect, useState } from "react";
import { pfClient } from "../services/portfolioClient";
import { Link } from "react-router-dom";

export default function PortfoliosList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    let mounted = true;
    
    pfClient.list()
      .then(data => {
        if (!mounted) return;
        setItems(data);
      })
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
    
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="p-4 text-sm text-gray-500">Loading portfolios…</div>
    );
  }
  
  if (err) {
    return (
      <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
        <div className="font-semibold">Error loading portfolios</div>
        <div>{err}</div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Portfolios</h1>
        <Link 
          to="/portfolios/new" 
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          + Create Portfolio
        </Link>
      </div>
      
      {items.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">No portfolios found</div>
          <Link 
            to="/portfolios/new"
            className="text-blue-600 hover:text-blue-700"
          >
            Create your first portfolio
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map(p => (
            <Link 
              key={p.id} 
              to={`/portfolios/${p.id}`} 
              className="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="text-lg font-semibold text-gray-900 mb-2">
                {p.name}
              </div>
              <div className="text-sm text-gray-600 mb-2">
                NAV: <span className="font-mono">${p.cash_balance?.toFixed?.(2) ?? p.cash_balance}</span>
              </div>
              <div className="text-xs text-gray-500">
                Status: <span className={`font-medium ${p.status === 'ACTIVE' ? 'text-green-600' : 'text-gray-600'}`}>
                  {p.status}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Modules: {p.modules?.map(m => m.module).join(", ") || "None"}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
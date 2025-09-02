import React, { useState } from "react";
import { pfClient } from "../services/portfolioClient";
import { useNavigate, Link } from "react-router-dom";

export default function PortfolioCreate() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [balance, setBalance] = useState(10000);
  const [err, setErr] = useState("");
  const [creating, setCreating] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || creating) return;

    setCreating(true);
    setErr("");
    
    try {
      const portfolio = await pfClient.create({
        name: name.trim(),
        starting_balance: Number(balance),
        modules: []
      });
      navigate(`/portfolios/${portfolio.id}`);
    } catch (ex) {
      setErr(String(ex));
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Link to="/portfolios" className="text-blue-600 hover:text-blue-700">
            ← Back
          </Link>
          <h1 className="text-xl font-semibold text-gray-900">Create Portfolio</h1>
        </div>
        <p className="text-sm text-gray-600">
          Create a new virtual portfolio to track your trading strategies
        </p>
      </div>

      {err && (
        <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-3">
          <div className="font-semibold">Creation failed</div>
          <div>{err}</div>
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700 mb-1 block">
            Portfolio Name
          </label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g. My Options Strategy"
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700 mb-1 block">
            Starting Balance (USD)
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={balance}
            onChange={e => setBalance(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          />
          <div className="text-xs text-gray-500 mt-1">
            This will be your initial cash balance for trading
          </div>
        </div>

        <div className="pt-4 space-y-3">
          <button
            type="submit"
            disabled={!name.trim() || creating}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {creating ? "Creating..." : "Create Portfolio"}
          </button>
          
          <Link
            to="/portfolios"
            className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors text-center block"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
import React from "react";
import { Link } from "react-router-dom";

export default function TopScoredStocks({ limit = 5, fields = [], ctaText = "Run Full Scan", ctaLink = "/stocks/scoring" }) {
  // TODO: Replace with real API data
  const stocks = [
    { symbol: "NVDA", score: 92, sector: "Technology", momentum: 0.85, value: 0.78 },
    { symbol: "MSFT", score: 88, sector: "Technology", momentum: 0.82, value: 0.81 },
    { symbol: "AAPL", score: 85, sector: "Technology", momentum: 0.79, value: 0.83 },
    { symbol: "TSLA", score: 82, sector: "Automotive", momentum: 0.88, value: 0.65 },
    { symbol: "GOOGL", score: 80, sector: "Technology", momentum: 0.75, value: 0.80 }
  ].slice(0, limit);

  return (
    <div className="space-y-3">
      {stocks.map((stock, idx) => (
        <div key={idx} className="bg-slate-900/60 border border-slate-700 rounded-lg p-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="text-2xl font-bold text-white">{stock.symbol}</div>
            <div className="space-y-1">
              <div className="text-sm text-gray-400">{stock.sector}</div>
              <div className="flex gap-3 text-xs">
                <span className="text-green-400">Momentum: {(stock.momentum * 100).toFixed(0)}%</span>
                <span className="text-blue-400">Value: {(stock.value * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-green-400">{stock.score}</div>
            <div className="text-xs text-gray-400">Score</div>
          </div>
        </div>
      ))}
      <Link to={ctaLink} className="block text-center py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors mt-4">
        {ctaText}
      </Link>
    </div>
  );
}

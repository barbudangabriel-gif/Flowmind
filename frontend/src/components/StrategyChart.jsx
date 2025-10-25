/**
 * StrategyChart - Universal P&L Chart Component
 * 
 * Renders P&L visualization for ANY strategy defined in strategies.json
 * Supports two sizes: "card" (360x180) for Optimize tab, "full" (1000x400) for Build tab
 * 
 * Features:
 * - Universal P&L curve generation via StrategyEngine
 * - Interactive tooltip with price/P&L tracking
 * - Profit/loss color coding (cyan/red gradients)
 * - Reference lines (current price, breakeven, strike)
 * - Probability distribution overlay (optional)
 * - Same visual style as BuilderV2Page Build tab
 */

import React, { useState } from 'react';
import StrategyEngine from '../services/StrategyEngine';

// Black-Scholes helper functions (copied from BuilderV2Page)
const normCDF = (x) => {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989423 * Math.exp((-x * x) / 2);
  const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return x > 0 ? 1 - prob : prob;
};

const blackScholesCall = (S, K, r, q, sigma, tau) => {
  if (tau <= 0) return Math.max(S - K, 0);
  const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * tau) / (sigma * Math.sqrt(tau));
  const d2 = d1 - sigma * Math.sqrt(tau);
  return S * Math.exp(-q * tau) * normCDF(d1) - K * Math.exp(-r * tau) * normCDF(d2);
};

export default function StrategyChart({ 
  strategyId = 'long_call',
  currentPrice = 221.09,
  size = 'card', // 'card' | 'full'
  strikes = { strike: 220 },
  premiums = { premium: 3787.50 },
  volatility = 0.348, // IV as decimal (34.8%)
  daysToExpiry = 420,
  showProbability = true,
  showTooltip = true,
  className = ''
}) {
  const [tooltip, setTooltip] = useState({ 
    show: false, 
    x: 0, 
    y: 0, 
    viewBoxX: 0,
    price: 0, 
    pnl: 0 
  });

  // Initialize StrategyEngine
  const engine = new StrategyEngine(strategyId, currentPrice);
  engine.initialize({ strikes, premiums });
  const metrics = engine.getMetrics();

  // Chart dimensions based on size
  const dimensions = size === 'card' 
    ? { 
        width: 360, 
        height: 180, 
        padding: { top: 15, right: 5, bottom: 25, left: 45 },
        fontSize: { axis: 9, label: 8, tooltip: 10 }
      }
    : { 
        width: 1000, 
        height: 400, 
        padding: { top: 20, right: 1, bottom: 40, left: 70 },
        fontSize: { axis: 12, label: 11, tooltip: 12 }
      };

  const { width, height, padding } = dimensions;
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate price range (extend loss zone for better visualization)
  const priceMin = currentPrice * 0.45; // 55% below
  const priceMax = currentPrice * 1.50; // 50% above
  const priceRange = priceMax - priceMin;

  // Generate P&L curve
  const pnlData = engine.generatePnLCurve(priceMin, priceMax, size === 'card' ? 3 : 2);

  // Calculate Y-axis range (auto-scale with padding)
  const pnlValues = pnlData.map(d => d.pnl);
  const pnlMin = Math.min(...pnlValues) * 1.3;
  const pnlMax = Math.max(...pnlValues) * 1.3;
  const pnlRange = pnlMax - pnlMin;

  // Scale functions
  const scaleX = (price) => {
    return padding.left + ((price - priceMin) / priceRange) * chartWidth;
  };

  const scaleY = (pnl) => {
    return height - padding.bottom - ((pnl - pnlMin) / pnlRange) * chartHeight;
  };

  // Split into profit/loss segments
  let lossPoints = [];
  let profitPoints = [];
  let intersectionPoint = null;

  for (let i = 0; i < pnlData.length - 1; i++) {
    if ((pnlData[i].pnl <= 0 && pnlData[i + 1].pnl > 0) || 
        (pnlData[i].pnl > 0 && pnlData[i + 1].pnl <= 0)) {
      const t = -pnlData[i].pnl / (pnlData[i + 1].pnl - pnlData[i].pnl);
      const xIntersect = pnlData[i].price + t * (pnlData[i + 1].price - pnlData[i].price);
      intersectionPoint = { price: xIntersect, pnl: 0 };
      lossPoints = pnlData.slice(0, i + 1);
      lossPoints.push(intersectionPoint);
      profitPoints = [intersectionPoint, ...pnlData.slice(i + 1)];
      break;
    }
  }

  if (!intersectionPoint) {
    if (pnlData[0].pnl <= 0) lossPoints = pnlData;
    else profitPoints = pnlData;
  }

  // Build SVG paths
  const buildPath = (points) => {
    return points.map((point, i) => {
      const x = scaleX(point.price);
      const y = scaleY(point.pnl);
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
  };

  const lossPath = buildPath(lossPoints);
  const profitPath = buildPath(profitPoints);

  // Close paths for gradient fill
  const closePath = (points, type) => {
    if (points.length === 0) return '';
    const zeroY = scaleY(0);
    const firstX = scaleX(points[0].price);
    const lastX = scaleX(points[points.length - 1].price);
    return ` L ${lastX} ${zeroY} L ${firstX} ${zeroY} Z`;
  };

  // Y-axis labels
  const numYLabels = size === 'card' ? 5 : 10;
  const yLabels = Array.from({ length: numYLabels }, (_, i) => {
    return Math.round(pnlMin + (i * pnlRange) / (numYLabels - 1));
  });

  // X-axis labels
  const numXLabels = size === 'card' ? 5 : 10;
  const xLabels = Array.from({ length: numXLabels }, (_, i) => {
    return Math.round(priceMin + (i * priceRange) / (numXLabels - 1));
  });

  // Mouse move handler
  const handleMouseMove = (e) => {
    if (!showTooltip) return;

    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const scaleXFactor = width / rect.width;
    const scaleYFactor = height / rect.height;
    const viewBoxX = x * scaleXFactor;
    const viewBoxY = y * scaleYFactor;

    if (viewBoxX >= padding.left && viewBoxX <= width - padding.right &&
        viewBoxY >= padding.top && viewBoxY <= height - padding.bottom) {
      
      const price = priceMin + ((viewBoxX - padding.left) / chartWidth) * priceRange;
      const pnl = engine.calculatePnL(price);

      setTooltip({
        show: true,
        x: e.clientX,
        y: e.clientY,
        viewBoxX,
        price,
        pnl
      });
    } else {
      setTooltip({ show: false, x: 0, y: 0, viewBoxX: 0, price: 0, pnl: 0 });
    }
  };

  return (
    <div className={`relative bg-[#0d1230] rounded-lg ${className}`} style={{ height: `${height}px` }}>
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setTooltip({ show: false, x: 0, y: 0, viewBoxX: 0, price: 0, pnl: 0 })}
      >
        {/* Gradient definitions */}
        <defs>
          <linearGradient id={`redGradient-${size}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(220, 38, 38, 0)" />
            <stop offset="100%" stopColor="rgba(220, 38, 38, 0.85)" />
          </linearGradient>
          <linearGradient id={`cyanGradient-${size}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(6, 182, 212, 0.85)" />
            <stop offset="100%" stopColor="rgba(6, 182, 212, 0)" />
          </linearGradient>
        </defs>

        {/* Y-axis grid and labels */}
        {yLabels.map((value, i) => {
          const y = scaleY(value);
          return (
            <g key={`y-${i}`}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="rgba(255, 255, 255, 0.12)"
                strokeWidth="1"
              />
              {size === 'full' && (
                <>
                  <line
                    x1={padding.left - 5}
                    y1={y}
                    x2={padding.left}
                    y2={y}
                    stroke="rgba(255, 255, 255, 0.7)"
                    strokeWidth="2"
                  />
                  <text
                    x={padding.left - 10}
                    y={y + 4}
                    textAnchor="end"
                    fill="rgba(255, 255, 255, 0.9)"
                    fontSize={dimensions.fontSize.axis}
                    fontWeight="700"
                  >
                    ${value >= 0 ? value.toLocaleString() : value.toLocaleString()}
                  </text>
                </>
              )}
            </g>
          );
        })}

        {/* Zero line */}
        <line
          x1={padding.left}
          y1={scaleY(0)}
          x2={width - padding.right}
          y2={scaleY(0)}
          stroke="rgba(255, 255, 255, 0.3)"
          strokeWidth="1.5"
        />

        {/* Strike price line (white dashed) */}
        {metrics.strikes.strike && (
          <line
            x1={scaleX(metrics.strikes.strike)}
            y1={padding.top}
            x2={scaleX(metrics.strikes.strike)}
            y2={height - padding.bottom}
            stroke="rgba(255, 255, 255, 0.5)"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />
        )}

        {/* Breakeven line (cyan) */}
        {metrics.breakeven[0] && (
          <>
            <line
              x1={scaleX(metrics.breakeven[0])}
              y1={padding.top}
              x2={scaleX(metrics.breakeven[0])}
              y2={height - padding.bottom}
              stroke="rgba(6, 182, 212, 0.6)"
              strokeWidth="1.5"
            />
            {size === 'full' && (
              <text
                x={scaleX(metrics.breakeven[0])}
                y={padding.top - 5}
                textAnchor="middle"
                fill="#06b6d4"
                fontSize={dimensions.fontSize.label}
                fontWeight="600"
              >
                ${metrics.breakeven[0].toFixed(2)}
              </text>
            )}
          </>
        )}

        {/* Loss section (red) */}
        {lossPoints.length > 0 && (
          <>
            <path
              d={lossPath}
              stroke="#dc2626"
              strokeWidth={size === 'card' ? 2 : 2.5}
              fill="none"
            />
            <path
              d={lossPath + closePath(lossPoints, 'loss')}
              fill={`url(#redGradient-${size})`}
            />
          </>
        )}

        {/* Profit section (cyan) */}
        {profitPoints.length > 0 && (
          <>
            <path
              d={profitPath}
              stroke="#06b6d4"
              strokeWidth={size === 'card' ? 2 : 2.5}
              fill="none"
            />
            <path
              d={profitPath + closePath(profitPoints, 'profit')}
              fill={`url(#cyanGradient-${size})`}
            />
          </>
        )}

        {/* Mouse tracking line and dot */}
        {tooltip.show && (
          <>
            <line
              x1={tooltip.viewBoxX}
              y1={padding.top}
              x2={tooltip.viewBoxX}
              y2={height - padding.bottom}
              stroke="white"
              strokeWidth="1.5"
            />
            <text
              x={tooltip.viewBoxX}
              y={padding.top - 5}
              fill="white"
              fontSize={dimensions.fontSize.label}
              textAnchor="middle"
            >
              ${tooltip.price.toFixed(2)}
            </text>
            <circle
              cx={tooltip.viewBoxX}
              cy={scaleY(tooltip.pnl)}
              r={size === 'card' ? 4 : 5}
              fill={tooltip.pnl >= 0 ? "#06b6d4" : "#dc2626"}
              stroke="white"
              strokeWidth="2"
            />
          </>
        )}
      </svg>

      {/* Tooltip for P&L value */}
      {tooltip.show && (
        <div
          className="absolute z-50 pointer-events-none"
          style={{
            left: `${(tooltip.viewBoxX / width) * 100}%`,
            top: `${(scaleY(tooltip.pnl) / height) * 100}%`,
            transform: 'translate(10px, -50%)',
          }}
        >
          <div className={`rounded-lg px-2 py-1 shadow-xl ${tooltip.pnl >= 0 ? 'bg-cyan-600' : 'bg-red-600'}`}>
            <div className={`text-white font-bold whitespace-nowrap`} 
                 style={{ fontSize: `${dimensions.fontSize.tooltip}px` }}>
              {tooltip.pnl >= 0 ? '+' : ''}${tooltip.pnl.toFixed(0)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';

/**
 * StrategyCard - EXACT design from Screenshot_545.png (Long Call)
 * Matches colors, layout, spacing, and chart style precisely
 */
export default function StrategyCard({ strategy, metrics = {}, onClick }) {
  const {
    name = 'Strategy Name',
    legs = [],
    returnPercent = 0,
    chancePercent = 0,
    profit = 0,
    risk = 0,
    collateral = 0,
  } = { ...strategy, ...metrics };

  // Format currency exactly as in screenshot
  const formatCurrency = (val) => {
    if (!val) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(val);
  };

  // Dynamic color for Return (orange gradient: darker at low values, brighter at high)
  const getReturnColor = (percent) => {
    if (percent <= 0) return 'rgba(255, 255, 255, 0.5)';
    // 0-100% → Orange gradient (darker to brighter)
    // Low (0-30%): #d97706 (darker orange)
    // Mid (30-70%): #f97316 (medium orange)
    // High (70-100%): #fb923c (bright orange)
    const intensity = Math.min(percent / 100, 1);
    const r = Math.round(217 + (251 - 217) * intensity);
    const g = Math.round(119 + (146 - 119) * intensity);
    const b = Math.round(6 + (60 - 6) * intensity);
    return `rgb(${r}, ${g}, ${b})`;
  };

  // Dynamic color for Chance (green gradient: lighter at low, darker at high)
  const getChanceColor = (percent) => {
    if (percent <= 0) return 'rgba(255, 255, 255, 0.5)';
    // 0-100% → Green gradient (lighter to darker)
    // Low (0-40%): #86efac (light green)
    // Mid (40-70%): #4ade80 (medium green)
    // High (70-100%): #22c55e (dark green)
    const intensity = Math.min(percent / 100, 1);
    const r = Math.round(134 - (134 - 34) * intensity);
    const g = Math.round(239 - (239 - 197) * intensity);
    const b = Math.round(172 - (172 - 94) * intensity);
    return `rgb(${r}, ${g}, ${b})`;
  };

  // Format legs description (clean, concise: "Buy 195C")
  const formatLegs = (legs) => {
    if (!legs || legs.length === 0) return 'No configuration';
    
    return legs.map(leg => {
      const action = leg.side === 'BUY' ? 'Buy' : 'Sell';
      const strike = typeof leg.strike === 'string' ? leg.strike.replace('ATM', '195') : '195';
      const type = leg.kind === 'CALL' ? 'C' : 'P';
      return `${action} ${strike}${type}`;
    }).join(', ');
  };

  // Generate realistic P&L curve
  const generatePnLCurve = () => {
    const points = [];
    const basePrice = 200;
    const numPoints = 50;
    
    for (let i = 0; i < numPoints; i++) {
      const pricePercent = (i / numPoints) * 0.55 + 0.775; // 77.5% to 132.5%
      const price = Math.round(basePrice * pricePercent);
      
      let pnl;
      
      if (name.includes('Bull Call Spread')) {
        // Bull Call Spread: Buy lower strike, Sell higher strike
        const lowerStrike = 220;
        const higherStrike = 240;
        const netDebit = risk || 1300;
        
        if (price <= lowerStrike) {
          pnl = -netDebit;
        } else if (price >= higherStrike) {
          const maxProfit = (higherStrike - lowerStrike) * 100 - netDebit;
          pnl = maxProfit;
        } else {
          const intrinsicValue = (price - lowerStrike) * 100;
          pnl = intrinsicValue - netDebit;
        }
      } else if (name.includes('Long Put')) {
        // Long Put: profit increases as price goes down (inverse hockey stick)
        const strikePrice = 200;
        const premium = risk || 2500;
        if (price >= strikePrice) {
          // Above strike: put expires worthless
          pnl = -premium;
        } else {
          // Below strike: intrinsic value = (strike - price) * 100 - premium
          pnl = (strikePrice - price) * 100 - premium;
        }
      } else if (name.includes('Call') && !name.includes('Spread')) {
        // Long Call: hockey stick - loss limited, profit unlimited
        const strikePrice = 220;
        const premium = risk || 3787.50;
        if (price < strikePrice) {
          pnl = -premium;
        } else {
          pnl = (price - strikePrice) * 100 - premium;
        }
      } else if (name.includes('Spread')) {
        // Other spreads: bounded profit (generic)
        const center = numPoints / 2;
        const distance = Math.abs(i - center);
        pnl = (profit || 1000) * (1 - Math.pow(distance / center, 2)) - (risk || 500) * 0.3;
      } else {
        // Default: linear
        pnl = ((i / numPoints) - 0.5) * (profit || 2000) * 2;
      }
      
      points.push([price, Math.round(pnl)]);
    }
    
    return points;
  };

  // Render P&L chart matching screenshot exactly
  const renderChart = () => {
    const data = generatePnLCurve();
    
    const width = 360;
    const height = 180;
    const padding = { top: 10, right: -8, bottom: 45, left: 33 };  // Moved 18px right total: left 33, right -8
    
    // Y-axis range - adjusted for better loss visibility
    const yMin = -4000;  // Increased from -2000 to show loss zone better
    const yMax = 6000;
    const yRange = yMax - yMin;
    
    // X-axis range (from screenshot: $160 to $280)
    const xMin = data[0][0];
    const xMax = data[data.length - 1][0];
    
    // Scale functions
    const scaleX = (price) => {
      return padding.left + ((price - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);
    };
    
    const scaleY = (pnl) => {
      return height - padding.bottom - ((pnl - yMin) / yRange) * (height - padding.top - padding.bottom);
    };
    
    // Generate path
    const pathD = data.map((point, i) => {
      const x = scaleX(point[0]);
      const y = scaleY(point[1]);
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
    
    // Zero line
    const zeroY = scaleY(0);
    
    // Y-axis labels - adjusted for new range
    const yLabels = [-4000, -2000, 0, 2000, 4000, 6000];
    
    // X-axis labels - slightly less loss zone (165-265 range)
    const xLabels = [165, 185, 205, 225, 245, 265];
    
    return (
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="w-full">
        {/* Gradient definitions for fill effects */}
        <defs>
          {/* Red gradient: starts intense at zero line (bottom of loss area), fades down */}
          <linearGradient id="redGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(239, 68, 68, 0)" stopOpacity="0" />
            <stop offset="100%" stopColor="rgba(239, 68, 68, 0.45)" stopOpacity="1" />
          </linearGradient>
          
          {/* Green gradient: starts intense at zero line (top of profit area), fades up */}
          <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(34, 197, 94, 0.45)" stopOpacity="1" />
            <stop offset="100%" stopColor="rgba(34, 197, 94, 0)" stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Y-axis grid lines */}
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
              {/* Y-axis tick mark */}
              <line
                x1={padding.left - 5}
                y1={y}
                x2={padding.left}
                y2={y}
                stroke="rgba(255, 255, 255, 0.7)"
                strokeWidth="2"
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                fill="rgba(255, 255, 255, 0.85)"
                fontSize="11"
                fontFamily="system-ui"
                fontWeight="700"
              >
                {formatCurrency(value)}
              </text>
            </g>
          );
        })}
        
        {/* Zero line (thin, solid, more visible) */}
        <line
          x1={padding.left}
          y1={zeroY}
          x2={width - padding.right}
          y2={zeroY}
          stroke="rgba(255, 255, 255, 0.3)"
          strokeWidth="1.5"
        />
        
        {/* Current price line (white dashed) - spot price */}
        {(() => {
          const currentPrice = 217.26; // Current spot price
          const currentX = scaleX(currentPrice);
          
          return (
            <line
              x1={currentX}
              y1={padding.top}
              x2={currentX}
              y2={height - 20}
              stroke="rgba(255, 255, 255, 0.5)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
          );
        })()}
        
        {/* Breakeven vertical line (cyan) for Long Call */}
        {name.includes('Call') && !name.includes('Spread') && (() => {
          const strikePrice = 195;
          const premium = risk || 2580;
          const breakeven = strikePrice + (premium / 100); // $220.80
          const breakevenX = scaleX(breakeven);
          
          return (
            <g>
              <line
                x1={breakevenX}
                y1={padding.top}
                x2={breakevenX}
                y2={height - 20}
                stroke="rgba(6, 182, 212, 0.6)"
                strokeWidth="1.5"
              />
              <text
                x={breakevenX}
                y={padding.top - 2}
                textAnchor="middle"
                fill="#06b6d4"
                fontSize="11"
                fontWeight="600"
                fontFamily="system-ui"
              >
                ${breakeven.toFixed(2)}
              </text>
            </g>
          );
        })()}

        {/* Chance line (orange vertical) - positioned in profit zone (green area) */}
        {chancePercent > 0 && (() => {
          // Position orange line in the green/profit area
          // For Long Call: should be to the right of breakeven (in profit zone)
          const strikePrice = 195;
          const premium = risk || 2580;
          const breakeven = strikePrice + (premium / 100); // $220.80
          
          // Place orange line in profit zone based on chance percentage
          // Higher chance = further into profit zone
          const maxPrice = 265; // Right edge of chart
          const chancePrice = breakeven + (maxPrice - breakeven) * (chancePercent / 100);
          const chanceX = scaleX(chancePrice);
          
          return (
            <line
              x1={chanceX}
              y1={padding.top}
              x2={chanceX}
              y2={height - 20}
              stroke="rgba(251, 146, 60, 0.6)"
              strokeWidth="1.5"
            />
          );
        })()}
        
        {/* P&L line - split into RED (below 0) and GREEN (above 0) */}
        {(() => {
          // Find intersection point with zero line
          let intersectionPoint = null;
          let intersectionIndex = -1;
          
          for (let i = 0; i < data.length - 1; i++) {
            if ((data[i][1] <= 0 && data[i + 1][1] > 0) || (data[i][1] > 0 && data[i + 1][1] <= 0)) {
              // Linear interpolation to find exact zero crossing
              const x1 = data[i][0], y1 = data[i][1];
              const x2 = data[i + 1][0], y2 = data[i + 1][1];
              const t = -y1 / (y2 - y1);
              const xIntersect = x1 + t * (x2 - x1);
              intersectionPoint = [xIntersect, 0];
              intersectionIndex = i;
              break;
            }
          }
          
          // Split data into loss and profit segments
          let lossPoints = [];
          let profitPoints = [];
          
          if (intersectionPoint) {
            // Add all points before intersection to loss
            lossPoints = data.slice(0, intersectionIndex + 1);
            // Add intersection point to both segments for smooth connection
            lossPoints.push(intersectionPoint);
            
            profitPoints = [intersectionPoint];
            profitPoints.push(...data.slice(intersectionIndex + 1));
          } else {
            // No intersection, all points are either loss or profit
            if (data[0][1] <= 0) {
              lossPoints = data;
            } else {
              profitPoints = data;
            }
          }
          
          // Build loss path (red)
          const lossPath = lossPoints.map((point, i) => {
            const x = scaleX(point[0]);
            const y = scaleY(point[1]);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
          }).join(' ');
          
          // Build profit path (green)
          const profitPath = profitPoints.map((point, i) => {
            const x = scaleX(point[0]);
            const y = scaleY(point[1]);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
          }).join(' ');
          
          return (
            <>
              {/* Loss line (red) */}
              {lossPath && lossPoints.length > 0 && (
                <path
                  d={lossPath}
                  fill="none"
                  stroke="#ef4444"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              )}
              
              {/* Profit line (green) */}
              {profitPath && profitPoints.length > 0 && (
                <path
                  d={profitPath}
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              )}
              
              {/* Fill area under loss curve (red gradient) */}
              {lossPoints.length > 0 && (
                <path
                  d={`${lossPath} L ${scaleX(lossPoints[lossPoints.length - 1][0])} ${zeroY} L ${scaleX(lossPoints[0][0])} ${zeroY} Z`}
                  fill="url(#redGradient)"
                />
              )}
              
              {/* Fill area under profit curve (green gradient) */}
              {profitPoints.length > 0 && (
                <path
                  d={`${profitPath} L ${scaleX(profitPoints[profitPoints.length - 1][0])} ${zeroY} L ${scaleX(profitPoints[0][0])} ${zeroY} Z`}
                  fill="url(#greenGradient)"
                />
              )}
            </>
          );
        })()}
        
        {/* Chart frame (axes) */}
        {/* Bottom horizontal axis - lower position */}
        <line
          x1={padding.left}
          y1={height - 20}
          x2={width - padding.right}
          y2={height - 20}
          stroke="rgba(255, 255, 255, 0.25)"
          strokeWidth="2"
        />
        
        {/* Left vertical axis - extended to meet X-axis */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - 20}
          stroke="rgba(255, 255, 255, 0.25)"
          strokeWidth="2"
        />
        
        {/* X-axis labels */}
        {xLabels.map((price, i) => {
          const x = scaleX(price);
          return (
            <g key={`x-${i}`}>
              {/* X-axis tick mark */}
              <line
                x1={x}
                y1={height - 20}
                x2={x}
                y2={height - 15}
                stroke="rgba(255, 255, 255, 0.7)"
                strokeWidth="2"
              />
              <text
                x={x}
                y={height - 8}
                textAnchor="middle"
                fill="rgba(255, 255, 255, 0.85)"
                fontSize="11"
                fontFamily="system-ui"
                fontWeight="700"
              >
                ${price}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div 
      className="rounded-lg p-4 transition-all cursor-pointer"
      style={{
        backgroundColor: '#282841',
        border: '2px solid #4a4a6a',
        boxShadow: '0 0 0 1px rgba(74, 74, 106, 0.3)'
      }}
      onClick={onClick}
    >
      {/* Title - centered */}
      <h3 className="mb-0.5 text-center" style={{ fontWeight: 700, color: 'rgba(255, 255, 255, 0.95)', fontSize: '1.125rem' }}>{name}</h3>
      
      {/* Legs description - centered */}
      <p className="text-sm mb-1.5 text-center" style={{ fontWeight: 700, color: 'rgba(203, 213, 225, 0.9)' }}>{formatLegs(legs)}</p>
      
      {/* Metrics row */}
      <div className="flex items-center justify-between w-full mb-1.5 text-sm">
        {returnPercent > 0 && (
          <div>
            <span style={{ fontWeight: 700, color: getReturnColor(returnPercent) }}>{returnPercent}%</span>
            <span className="ml-1" style={{ fontWeight: 700, color: 'rgba(203, 213, 225, 0.85)' }}>Return on {collateral > 0 ? 'collateral' : 'risk'}</span>
          </div>
        )}
        {chancePercent > 0 && (
          <div>
            <span style={{ fontWeight: 700, color: getChanceColor(chancePercent) }}>{chancePercent}%</span>
            <span className="ml-1" style={{ fontWeight: 700, color: 'rgba(203, 213, 225, 0.85)' }}>Chance</span>
          </div>
        )}
      </div>
      
      {/* Profit/Risk line */}
      <div className="flex items-center justify-between w-full mb-2.5 text-sm">
        {profit !== 0 && <span style={{ fontWeight: 700, color: 'rgba(203, 213, 225, 0.9)' }}>{formatCurrency(profit)} Profit</span>}
        {risk !== 0 && <span style={{ fontWeight: 700, color: 'rgba(203, 213, 225, 0.9)' }}>{formatCurrency(risk)} Risk</span>}
        {collateral !== 0 && <span style={{ fontWeight: 700, color: 'rgba(203, 213, 225, 0.9)' }}>{formatCurrency(collateral)} Collateral</span>}
      </div>
      
      {/* P&L Chart */}
      <div 
        className="rounded-lg p-2 mb-3"
        style={{
          backgroundColor: '#1e1e35'
        }}
      >
        {renderChart()}
      </div>

      {/* Open in Builder button */}
      <div className="text-center">
        <div 
          className="rounded cursor-pointer transition-all hover:opacity-80 inline-block"
          style={{
            backgroundColor: '#06b6d4',
            border: '1px solid #06b6d4',
            padding: '4px 12px'
          }}
          onClick={(e) => {
            e.stopPropagation();
            if (onClick) {
              onClick();
            }
          }}
        >
          <span style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.875rem' }}>
            Open in Builder
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * StrategyCard - Visual card matching Screenshot_541 design
 * Clean, minimal layout with metrics and P&L chart
 */

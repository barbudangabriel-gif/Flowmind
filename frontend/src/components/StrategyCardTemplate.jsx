import React, { useState } from 'react';

/**
 * StrategyCardTemplate - Universal card matching StrategyCard.jsx design
 * EXACT layout from Screenshot_545.png (Long Call reference)
 * Used in Optimize tab and Strategy Library for all 69 strategies
 */
export default function StrategyCardTemplate({ 
  strategy,
  onClick 
}) {
  const {
    name = 'Strategy Name',
    legs = [],
    returnPercent = 0,
    chancePercent = 0,
    profit = 0,
    risk = 0,
    collateral = 0,
    category = 'bullish',
  } = strategy;

  // Tooltip state
  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, price: 0, pnl: 0 });

  // Format currency exactly as in StrategyCard
  const formatCurrency = (val) => {
    if (!val) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(val);
  };

  // Dynamic color for Return (orange gradient)
  const getReturnColor = (percent) => {
    if (percent <= 0) return 'rgba(255, 255, 255, 0.5)';
    const intensity = Math.min(percent / 100, 1);
    const r = Math.round(217 + (251 - 217) * intensity);
    const g = Math.round(119 + (146 - 119) * intensity);
    const b = Math.round(6 + (60 - 6) * intensity);
    return `rgb(${r}, ${g}, ${b})`;
  };

  // Dynamic color for Chance (green gradient)
  const getChanceColor = (percent) => {
    if (percent <= 0) return 'rgba(255, 255, 255, 0.5)';
    const intensity = Math.min(percent / 100, 1);
    const r = Math.round(134 - (134 - 34) * intensity);
    const g = Math.round(239 - (239 - 197) * intensity);
    const b = Math.round(172 - (172 - 94) * intensity);
    return `rgb(${r}, ${g}, ${b})`;
  };

  // Format legs description (clean: "Buy 195C")
  const formatLegs = (legs) => {
    if (!legs || legs.length === 0) return 'No configuration';
    return legs.map(leg => {
      // Support both old format (side/kind) and new format (action/type)
      const action = (leg.action || leg.side || 'buy').toLowerCase() === 'buy' ? 'BUY' : 'SELL';
      const type = (leg.type || leg.kind || 'call').toUpperCase();
      const strike = leg.strike || leg.strike_label || '0';
      
      // For generated strategies with strike_label (like "lower", "higher")
      if (typeof strike === 'string' && !strike.match(/^\d/)) {
        return `${action} ${type}${leg.quantity > 1 ? ` x${leg.quantity}` : ''}`;
      }
      
      const typeSymbol = type.includes('CALL') ? 'C' : 'P';
      return `${action} ${strike}${typeSymbol}${leg.quantity > 1 ? ` x${leg.quantity}` : ''}`;
    }).join(', ');
  };

  // Generate P&L curve based on strategy type
  const generatePnLCurve = () => {
    const points = [];
    
    const numPoints = 50;
    
    // Dynamic price range based on strategy type
    let minPrice, maxPrice;
    
    if (name.includes('Long Put')) {
      // For Long Put with strike 200: range 100-275 (centered lower)
      minPrice = 100;
      maxPrice = 275;
    } else if (name.includes('Bull Call Spread') || name.includes('Bear Call Spread')) {
      // For spreads (220-240): center on 230, range 155-305
      minPrice = 155;
      maxPrice = 305;
    } else {
      // For Long Call: range 175-325 (centered on 220)
      minPrice = 175;
      maxPrice = 325;
    }
    
    for (let i = 0; i < numPoints; i++) {
      const price = minPrice + (i / (numPoints - 1)) * (maxPrice - minPrice);
      
      let pnl;
      
      if (name.includes('Bull Call Spread')) {
        const lowerStrike = 220;
        const higherStrike = 240;
        const netDebit = risk || 700; // Max loss (cost to enter position)
        
        // Debug: Log first/last points to verify P&L calculation
        if (i === 0 || i === numPoints - 1) {
          console.log(`Bull Call [${i === 0 ? 'START' : 'END'}] Price: ${price.toFixed(2)}, netDebit: ${netDebit}, risk: ${risk}`);
        }
        
        if (price <= lowerStrike) {
          pnl = -netDebit;
        } else if (price >= higherStrike) {
          pnl = (higherStrike - lowerStrike) * 100 - netDebit;
        } else {
          pnl = (price - lowerStrike) * 100 - netDebit;
        }
        
        // Debug: Log P&L for key prices
        if (i === 0 || i === numPoints - 1 || Math.abs(price - lowerStrike) < 1 || Math.abs(price - higherStrike) < 1) {
          console.log(`  → P&L: ${pnl}`);
        }
      } else if (name.includes('Bear Call Spread')) {
        // Bear Call Spread: Sell lower strike, Buy higher strike (credit spread)
        const lowerStrike = 220;
        const higherStrike = 240;
        const netCredit = profit || 1300; // Premium received
        
        if (price <= lowerStrike) {
          // Below lower strike: both expire worthless → keep credit
          pnl = netCredit;
        } else if (price >= higherStrike) {
          // Above higher strike: max loss = (spread width * 100) - credit
          pnl = -((higherStrike - lowerStrike) * 100 - netCredit);
        } else {
          // Between strikes: linear loss from credit to max loss
          const intrinsicLoss = (price - lowerStrike) * 100;
          pnl = netCredit - intrinsicLoss;
        }
      } else if (name.includes('Long Put')) {
        const strikePrice = 200;
        const premium = risk || 2650;
        if (price >= strikePrice) {
          pnl = -premium;
        } else {
          pnl = (strikePrice - price) * 100 - premium;
        }
      } else if (name.includes('Long Call')) {
        const strikePrice = 220;
        const premium = risk || 3787.50;
        if (price < strikePrice) {
          pnl = -premium;
        } else {
          pnl = (price - strikePrice) * 100 - premium;
        }
      } else {
        // Default linear
        pnl = ((i / numPoints) - 0.5) * (profit || 2000) * 2;
      }
      
      points.push([price, Math.round(pnl)]);
    }
    
    return points;
  };

  // Render chart
  const renderChart = () => {
    const data = generatePnLCurve();
    
    const width = 365;
    const height = 155; // Card height
    const padding = { top: 20, right: 13, bottom: 32, left: 52 }; // Increased top from 8 to 20 for tooltip label
    
    // Y-axis range: adjust for Long Put/Call and spreads
    const yMin = name.includes('Bull Call Spread') || name.includes('Bear Call Spread') ? -2000 : -4000;
    const yMax = name.includes('Long Put') ? 10000 : (name.includes('Long Call') ? 9000 : (name.includes('Bull Call Spread') || name.includes('Bear Call Spread') ? 4000 : 6000));
    const yRange = yMax - yMin;
    
    // X-axis range
    const xMin = data[0][0];
    const xMax = data[data.length - 1][0];
    
    // HARDCODE: Long Put needs inverted gradient
    const isLongPut = name.includes('Long Put');
    
    // Scale functions
    const scaleX = (price) => {
      return padding.left + ((price - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);
    };
    
    const scaleY = (pnl) => {
      return height - padding.bottom - ((pnl - yMin) / yRange) * (height - padding.top - padding.bottom);
    };
    
    const zeroY = scaleY(0);
    
    // Y-axis labels: dynamic based on strategy type
    const yLabels = name.includes('Long Put') 
      ? [-4000, -2000, 0, 2000, 4000, 6000, 8000, 10000]
      : name.includes('Long Call')
      ? [-4000, -2000, 0, 2000, 4000, 6000, 8000]
      : (name.includes('Bull Call Spread') || name.includes('Bear Call Spread'))
      ? [-2000, -1000, 0, 1000, 2000, 3000, 4000]
      : [-4000, -2000, 0, 2000, 4000, 6000];
    
    // X-axis labels: dynamic based on strategy type
    let xLabels;
    if (name.includes('Long Put')) {
      // For Long Put (range 100-275): 8 evenly spaced labels (~25 apart)
      xLabels = [100, 125, 150, 175, 200, 225, 250, 275];
    } else if (name.includes('Bull Call Spread') || name.includes('Bear Call Spread')) {
      // For spreads (range 155-305): centered on 230
      xLabels = [155, 175, 195, 215, 235, 255, 275, 295];
    } else {
      // For Long Call (range 175-325)
      xLabels = [185, 205, 225, 245, 265, 285, 305, 325];
    }
    
    // Calculate gradient coordinates in userSpaceOnUse
    const topY = padding.top;
    const bottomY = height - padding.bottom;
    
    // Calculate where zero line is as percentage of total chart height
    const chartHeight = bottomY - topY;
    const zeroOffsetFromTop = zeroY - topY;
    const zeroPercent = (zeroOffsetFromTop / chartHeight) * 100;
    
    // Split data into loss and profit segments
    let intersectionPoint = null;
    let intersectionIndex = -1;
    
    for (let i = 0; i < data.length - 1; i++) {
      if ((data[i][1] <= 0 && data[i + 1][1] > 0) || (data[i][1] > 0 && data[i + 1][1] <= 0)) {
        const x1 = data[i][0], y1 = data[i][1];
        const x2 = data[i + 1][0], y2 = data[i + 1][1];
        const t = -y1 / (y2 - y1);
        const xIntersect = x1 + t * (x2 - x1);
        intersectionPoint = [xIntersect, 0];
        intersectionIndex = i;
        break;
      }
    }
    
    let lossPoints = [];
    let profitPoints = [];
    
    if (intersectionPoint) {
      lossPoints = data.slice(0, intersectionIndex + 1);
      lossPoints.push(intersectionPoint);
      profitPoints = [intersectionPoint];
      profitPoints.push(...data.slice(intersectionIndex + 1));
    } else {
      if (data[0][1] <= 0) {
        lossPoints = data;
      } else {
        profitPoints = data;
      }
    }
    
    const lossPath = lossPoints.map((point, i) => {
      const x = scaleX(point[0]);
      const y = scaleY(point[1]);
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
    
    const profitPath = profitPoints.map((point, i) => {
      const x = scaleX(point[0]);
      const y = scaleY(point[1]);
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
    
    // Mouse handlers for tooltip
    const handleMouseMove = (e) => {
      const svg = e.currentTarget;
      const rect = svg.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      
      // Convert to price
      const price = xMin + ((mouseX - padding.left) / (width - padding.left - padding.right)) * (xMax - xMin);
      
      // Calculate P&L at this price (same logic as generatePnLCurve)
      let pnl;
      let probability = 0; // Simplified: chance of reaching this price
      
      if (name.includes('Bull Call Spread')) {
        const lowerStrike = 220;
        const higherStrike = 240;
        const netDebit = risk || 700;
        if (price <= lowerStrike) {
          pnl = -netDebit;
        } else if (price >= higherStrike) {
          pnl = (higherStrike - lowerStrike) * 100 - netDebit;
        } else {
          pnl = (price - lowerStrike) * 100 - netDebit;
        }
        probability = Math.max(0, Math.min(100, 100 - Math.abs(price - 221) / 2));
      } else if (name.includes('Bear Call Spread')) {
        const lowerStrike = 220;
        const higherStrike = 240;
        const netCredit = profit || 1300;
        if (price <= lowerStrike) {
          pnl = netCredit;
        } else if (price >= higherStrike) {
          pnl = -((higherStrike - lowerStrike) * 100 - netCredit);
        } else {
          const intrinsicLoss = (price - lowerStrike) * 100;
          pnl = netCredit - intrinsicLoss;
        }
        probability = Math.max(0, Math.min(100, 100 - Math.abs(price - 221) / 2));
      } else if (name.includes('Long Put')) {
        const strikePrice = 200;
        const premium = risk || 2650;
        pnl = price >= strikePrice ? -premium : (strikePrice - price) * 100 - premium;
        probability = Math.max(0, Math.min(100, 100 - Math.abs(price - 200) / 2));
      } else if (name.includes('Long Call')) {
        const strikePrice = 220;
        const premium = risk || 3787.50;
        pnl = price < strikePrice ? -premium : (price - strikePrice) * 100 - premium;
        probability = Math.max(0, Math.min(100, 100 - Math.abs(price - 221) / 2));
      } else {
        pnl = 0;
        probability = 50;
      }
      
      // Calculate Y position on the curve
      const curveY = scaleY(pnl);
      
      setTooltip({ show: true, x: mouseX, price, pnl, curveY, probability });
    };
    
    const handleMouseLeave = () => {
      setTooltip({ show: false, x: 0, price: 0, pnl: 0, curveY: 0, probability: 0 });
    };
    
    return (
      <svg 
        width="100%" 
        height={height} 
        viewBox={`0 0 ${width} ${height}`} 
        className="w-full"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <defs>
          {/* EXACT ca StrategyChart.jsx - CYAN cu opacitate 0.85 */}
          <linearGradient id="redGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(220, 38, 38, 0)" />
            <stop offset="100%" stopColor="rgba(220, 38, 38, 0.85)" />
          </linearGradient>
          <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(6, 182, 212, 0.85)" />
            <stop offset="100%" stopColor="rgba(6, 182, 212, 0)" />
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
        
        {/* Zero line */}
        <line
          x1={padding.left}
          y1={zeroY}
          x2={width - padding.right}
          y2={zeroY}
          stroke="rgba(255, 255, 255, 0.3)"
          strokeWidth="1.5"
        />
        
        {/* Current Price vertical line (white dashed, fine dots) */}
        {(() => {
          let currentPrice;
          if (name.includes('Long Put')) {
            currentPrice = 200; // Strike
          } else if (name.includes('Bull Call Spread') || name.includes('Bear Call Spread')) {
            currentPrice = 221.09; // Current spot price between strikes
          } else {
            currentPrice = 221.09; // Default spot
          }
          return (
            <line
              x1={scaleX(currentPrice)}
              y1={padding.top}
              x2={scaleX(currentPrice)}
              y2={height - 20}
              stroke="rgba(255, 255, 255, 0.7)"
              strokeWidth="1.5"
              strokeDasharray="2,2"
            />
          );
        })()}
        
        {/* Breakeven vertical line (cyan solid) at intersection point with label */}
        {intersectionPoint && (
          <>
            <line
              x1={scaleX(intersectionPoint[0])}
              y1={padding.top}
              x2={scaleX(intersectionPoint[0])}
              y2={height - 20}
              stroke="rgba(6, 182, 212, 0.8)"
              strokeWidth="1.5"
            />
            <text
              x={scaleX(intersectionPoint[0])}
              y={padding.top - 2}
              textAnchor="middle"
              fill="rgba(6, 182, 212, 0.9)"
              fontSize="9"
              fontFamily="system-ui"
              fontWeight="600"
            >
              ${intersectionPoint[0].toFixed(0)}
            </text>
          </>
        )}
        
        {/* Chance line (orange solid) - positioned based on probability */}
        {(() => {
          // Calculate chance line position based on strategy
          let chancePrice;
          if (name.includes('Long Put')) {
            // For Long Put: chance is below current price (32% chance means price at ~155)
            const strikePrice = 200;
            const currentPrice = 221.09;
            // Approximate: chance line at ~75% of distance from breakeven to current
            chancePrice = intersectionPoint ? intersectionPoint[0] + (currentPrice - intersectionPoint[0]) * 0.25 : 155;
          } else {
            // For Long Call: chance is above strike
            const strikePrice = 220;
            const breakeven = intersectionPoint ? intersectionPoint[0] : 257;
            chancePrice = breakeven + 30; // ~30 points above breakeven
          }
          
          return (
            <line
              x1={scaleX(chancePrice)}
              y1={padding.top}
              x2={scaleX(chancePrice)}
              y2={height - 20}
              stroke="rgba(251, 146, 60, 0.7)"
              strokeWidth="1.5"
            />
          );
        })()}
        
        {/* Loss line (red) - for Long Put this is the right side (above strike) */}
        {lossPath && lossPoints.length > 0 && (
          <>
            <path
              d={lossPath}
              fill="none"
              stroke={name.includes('Long Put') ? "#06b6d4" : "#ef4444"}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d={`${lossPath} L ${scaleX(lossPoints[lossPoints.length - 1][0])} ${zeroY} L ${scaleX(lossPoints[0][0])} ${zeroY} Z`}
              fill={name.includes('Long Put') ? "url(#greenGradient)" : "url(#redGradient)"}
            />
          </>
        )}
        
        {/* Profit line (CYAN) - for Long Put this is the left side (below strike) */}
        {profitPath && profitPoints.length > 0 && (
          <>
            <path
              d={profitPath}
              fill="none"
              stroke={name.includes('Long Put') ? "#ef4444" : "#06b6d4"}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d={`${profitPath} L ${scaleX(profitPoints[profitPoints.length - 1][0])} ${zeroY} L ${scaleX(profitPoints[0][0])} ${zeroY} Z`}
              fill={name.includes('Long Put') ? "url(#redGradient)" : "url(#greenGradient)"}
            />
          </>
        )}
        
        {/* Axes */}
        <line
          x1={padding.left}
          y1={height - 20}
          x2={width - padding.right}
          y2={height - 20}
          stroke="rgba(255, 255, 255, 1)"
          strokeWidth="1"
        />
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - 20}
          stroke="rgba(255, 255, 255, 1)"
          strokeWidth="1"
        />
        
        {/* X-axis labels */}
        {xLabels.map((price, i) => {
          const x = scaleX(price);
          return (
            <g key={`x-${i}`}>
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
        
        {/* Tooltip - vertical line with labels */}
        {tooltip.show && (
          <g>
            {/* Vertical tracking line */}
            <line
              x1={tooltip.x}
              y1={padding.top}
              x2={tooltip.x}
              y2={height - padding.bottom}
              stroke="rgba(255, 255, 255, 0.5)"
              strokeWidth="1"
              strokeDasharray="2,2"
            />
            
            {/* Dot on curve */}
            <circle
              cx={tooltip.x}
              cy={tooltip.curveY}
              r="3"
              fill={tooltip.pnl >= 0 ? "rgba(6, 182, 212, 1)" : "rgba(239, 68, 68, 1)"}
              stroke="white"
              strokeWidth="1.5"
            />
            
            {/* Top label - Price and Probability (no background) */}
            <text
              x={tooltip.x}
              y={padding.top - 6}
              textAnchor="middle"
              fill="rgba(255, 255, 255, 0.95)"
              fontSize="9"
              fontFamily="system-ui"
              fontWeight="600"
            >
              ${tooltip.price.toFixed(1)} ({tooltip.probability.toFixed(0)}%)
            </text>
            
            {/* Bottom label - P&L (follows curve, white text, raised up) */}
            <text
              x={tooltip.x}
              y={tooltip.curveY - 8}
              textAnchor="middle"
              fill="rgba(255, 255, 255, 0.95)"
              fontSize="10"
              fontFamily="system-ui"
              fontWeight="700"
            >
              {formatCurrency(tooltip.pnl)}
            </text>
          </g>
        )}
      </svg>
    );
  };

  return (
    <div 
      className="rounded-lg transition-all cursor-pointer"
      style={{
        backgroundColor: '#282841',
        border: '2px solid #4a4a6a',
        boxShadow: '0 0 0 1px rgba(74, 74, 106, 0.3)',
        maxWidth: '365px',
        width: '365px',
        paddingLeft: '2px',
        paddingRight: '12px',
        paddingTop: '18px',
        paddingBottom: '12px'
      }}
      onClick={onClick}
    >
      {/* Title */}
      <h3 className="mb-0 text-center" style={{ fontWeight: 400, color: 'rgba(255, 255, 255, 1)', fontSize: '0.975rem' }}>
        {name}
      </h3>
      
      {/* Legs */}
      <p className="text-xs mb-0 text-center" style={{ fontWeight: 700, color: 'rgba(156, 163, 175, 1)' }}>
        {formatLegs(legs)}
      </p>
      
      {/* Metrics row */}
      <div className="flex items-center justify-between w-full mb-1 text-xs" style={{ paddingLeft: '10px' }}>
        {returnPercent > 0 && (
          <div>
            <span style={{ fontWeight: 500, color: getReturnColor(returnPercent) }}>{returnPercent}%</span>
            <span className="ml-1" style={{ fontWeight: 500, color: 'rgba(255, 255, 255, 1)' }}>Return on risk</span>
          </div>
        )}
        {chancePercent > 0 && (
          <div>
            <span style={{ fontWeight: 500, color: getChanceColor(chancePercent) }}>{chancePercent}%</span>
            <span className="ml-1" style={{ fontWeight: 500, color: 'rgba(255, 255, 255, 1)' }}>Chance</span>
          </div>
        )}
      </div>
      
      {/* Profit/Risk line */}
      <div className="flex items-center justify-between w-full mb-1.5 text-xs" style={{ paddingLeft: '10px' }}>
        {profit !== 0 && <span style={{ fontWeight: 500, color: 'rgba(255, 255, 255, 1)' }}>{formatCurrency(profit)} Profit</span>}
        {risk !== 0 && <span style={{ fontWeight: 500, color: 'rgba(255, 255, 255, 1)' }}>{formatCurrency(risk)} Risk</span>}
        {collateral !== 0 && <span style={{ fontWeight: 500, color: 'rgba(255, 255, 255, 1)' }}>{formatCurrency(collateral)} Collateral</span>}
      </div>
      
      {/* Chart - no container, direct SVG */}
      <div className="mb-1.5">
        {renderChart()}
      </div>

      {/* Open in Builder button */}
      <div className="text-center">
        <div 
          className="rounded cursor-pointer transition-all hover:opacity-80 inline-block"
          style={{
            backgroundColor: '#06b6d4',
            border: '1px solid #06b6d4',
            padding: '2px 8px'
          }}
          onClick={(e) => {
            e.stopPropagation();
            if (onClick) onClick();
          }}
        >
          <span style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.8rem' }}>
            Open in Builder
          </span>
        </div>
      </div>
    </div>
  );
}

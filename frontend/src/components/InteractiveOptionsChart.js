import React from 'react';
// import Plot from 'react-plotly.js';

const InteractiveOptionsChart = ({ 
  chartData, 
  strategyName, 
  stockPrice, 
  height = 300,
  showBreakeven = true,
  showCurrentPrice = true 
}) => {
  if (!chartData || !chartData.x || !chartData.y) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 h-64 flex items-center justify-center border border-gray-600">
        <div className="text-gray-400 text-center">
          <div className="text-lg mb-2">📊</div>
          <div>Loading chart data...</div>
        </div>
      </div>
    );
  }

  // Find breakeven points (where P&L crosses zero)
  const breakevenPoints = [];
  for (let i = 0; i < chartData.y.length - 1; i++) {
    if ((chartData.y[i] <= 0 && chartData.y[i + 1] > 0) || 
        (chartData.y[i] >= 0 && chartData.y[i + 1] < 0)) {
      // Linear interpolation for exact breakeven
      const x1 = chartData.x[i];
      const x2 = chartData.x[i + 1];
      const y1 = chartData.y[i];
      const y2 = chartData.y[i + 1];
      
      if (y2 !== y1) {
        const breakevenPrice = x1 + (x2 - x1) * (-y1 / (y2 - y1));
        breakevenPoints.push(breakevenPrice);
      }
    }
  }

  const maxProfit = Math.max(...chartData.y);
  const maxLoss = Math.min(...chartData.y);

  // Create SVG path from data points
  const createPathFromData = (xData, yData) => {
    if (!xData || !yData || xData.length !== yData.length) return '';
    
    const minX = Math.min(...xData);
    const maxX = Math.max(...xData);
    const minY = Math.min(...yData);
    const maxY = Math.max(...yData);
    
    const width = 280;
    const heightSvg = 200;
    
    const scaleX = (x) => ((x - minX) / (maxX - minX)) * width;
    const scaleY = (y) => heightSvg - ((y - minY) / (maxY - minY)) * heightSvg;
    
    let path = `M ${scaleX(xData[0])} ${scaleY(yData[0])}`;
    for (let i = 1; i < xData.length; i++) {
      path += ` L ${scaleX(xData[i])} ${scaleY(yData[i])}`;
    }
    
    return path;
  };

  const svgPath = createPathFromData(chartData.x, chartData.y);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-600 overflow-hidden">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h5 className="text-white font-semibold">{strategyName} - Profit & Loss</h5>
          <div className="flex items-center space-x-2 text-xs text-gray-400">
            <span>At Expiration</span>
          </div>
        </div>
        
        <div className="bg-gray-900 rounded border border-gray-700 relative overflow-hidden" style={{height: `${height - 100}px`}}>
          
          {/* Professional Grid Lines */}
          <div className="absolute inset-0 opacity-30">
            {/* Horizontal grid lines */}
            {Array.from({length: 6}).map((_, i) => (
              <div 
                key={`h-${i}`} 
                className="absolute w-full border-t border-gray-600" 
                style={{top: `${i * 20}%`}}
              ></div>
            ))}
            {/* Vertical grid lines */}
            {Array.from({length: 8}).map((_, i) => (
              <div 
                key={`v-${i}`} 
                className="absolute h-full border-l border-gray-600" 
                style={{left: `${i * 14.28}%`}}
              ></div>
            ))}
          </div>
          
          {/* SVG Chart */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 280 200">
            {/* P&L Curve */}
            <path
              d={svgPath}
              stroke="#3b82f6"
              strokeWidth="2.5"
              fill="none"
              className="drop-shadow-lg"
            />
            
            {/* Breakeven lines */}
            {breakevenPoints.map((breakeven, index) => {
              const xPos = ((breakeven - Math.min(...chartData.x)) / (Math.max(...chartData.x) - Math.min(...chartData.x))) * 280;
              return (
                <line 
                  key={`breakeven-${index}`} 
                  x1={xPos} 
                  y1="0" 
                  x2={xPos} 
                  y2="200" 
                  stroke="#fbbf24" 
                  strokeWidth="1.5" 
                  strokeDasharray="3,3" 
                  opacity="0.8" 
                />
              );
            })}
            
            {/* Current price line */}
            {showCurrentPrice && stockPrice && (
              <line 
                x1={((stockPrice - Math.min(...chartData.x)) / (Math.max(...chartData.x) - Math.min(...chartData.x))) * 280} 
                y1="0" 
                x2={((stockPrice - Math.min(...chartData.x)) / (Math.max(...chartData.x) - Math.min(...chartData.x))) * 280} 
                y2="200" 
                stroke="#f97316" 
                strokeWidth="1.5" 
                strokeDasharray="3,3" 
                opacity="0.8" 
              />
            )}
            
            {/* Zero line */}
            <line 
              x1="0" 
              y1={200 - ((0 - Math.min(...chartData.y)) / (Math.max(...chartData.y) - Math.min(...chartData.y))) * 200} 
              x2="280" 
              y2={200 - ((0 - Math.min(...chartData.y)) / (Math.max(...chartData.y) - Math.min(...chartData.y))) * 200} 
              stroke="#6b7280" 
              strokeWidth="1" 
              strokeDasharray="3,3" 
              opacity="0.6" 
            />
          </svg>
          
          {/* Price Labels */}
          <div className="absolute bottom-2 left-2 text-xs text-gray-400 font-mono">
            ${Math.min(...chartData.x).toFixed(0)}
          </div>
          <div className="absolute bottom-2 right-2 text-xs text-gray-400 font-mono">
            ${Math.max(...chartData.x).toFixed(0)}
          </div>
          {showCurrentPrice && stockPrice && (
            <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs text-orange-400 font-semibold bg-gray-800 px-1 rounded">
              ${stockPrice.toFixed(0)}
            </div>
          )}
          
          {/* P&L Labels */}
          <div className="absolute top-2 left-2 text-xs text-green-400 font-semibold bg-gray-800 px-1 rounded">
            ${maxProfit.toFixed(0)}
          </div>
          <div className="absolute top-2 right-2 text-xs text-red-400 font-semibold bg-gray-800 px-1 rounded">
            ${Math.abs(maxLoss).toFixed(0)}
          </div>
        </div>
        
        {/* Chart Legend */}
        <div className="mt-3 flex items-center justify-center space-x-6 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-blue-500"></div>
            <span className="text-gray-400">P&L Curve</span>
          </div>
          {breakevenPoints.length > 0 && (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-0.5 bg-yellow-500 opacity-80" style={{borderTop: '1px dashed'}}></div>
              <span className="text-gray-400">Breakeven: ${breakevenPoints[0].toFixed(2)}</span>
            </div>
          )}
          {showCurrentPrice && stockPrice && (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-0.5 bg-orange-500 opacity-80" style={{borderTop: '1px dotted'}}></div>
              <span className="text-gray-400">Current Price</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InteractiveOptionsChart;
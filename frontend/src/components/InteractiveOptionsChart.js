import React from 'react';
import Plot from 'react-plotly.js';

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

  // Plotly data
  const plotData = [
    {
      x: chartData.x,
      y: chartData.y,
      type: 'scatter',
      mode: 'lines',
      name: `${strategyName} P&L`,
      line: {
        color: '#3b82f6',
        width: 3
      },
      fill: 'tozeroy',
      fillcolor: 'rgba(59, 130, 246, 0.1)',
      hovertemplate: 'Price: $%{x:.2f}<br>P&L: $%{y:.2f}<extra></extra>'
    }
  ];

  // Add breakeven lines
  if (showBreakeven && breakevenPoints.length > 0) {
    breakevenPoints.forEach((breakeven, index) => {
      plotData.push({
        x: [breakeven, breakeven],
        y: [maxLoss * 1.2, maxProfit * 1.2],
        type: 'scatter',
        mode: 'lines',
        name: `Breakeven ${index + 1}`,
        line: {
          color: '#fbbf24',
          width: 2,
          dash: 'dash'
        },
        showlegend: index === 0,
        hovertemplate: `Breakeven: $${breakeven.toFixed(2)}<extra></extra>`
      });
    });
  }

  // Add current price line
  if (showCurrentPrice && stockPrice) {
    plotData.push({
      x: [stockPrice, stockPrice],
      y: [maxLoss * 1.2, maxProfit * 1.2],
      type: 'scatter',
      mode: 'lines',
      name: 'Current Price',
      line: {
        color: '#f97316',
        width: 2,
        dash: 'dot'
      },
      hovertemplate: `Current: $${stockPrice.toFixed(2)}<extra></extra>`
    });
  }

  // Add zero line
  plotData.push({
    x: [Math.min(...chartData.x), Math.max(...chartData.x)],
    y: [0, 0],
    type: 'scatter',
    mode: 'lines',
    name: 'Zero Line',
    line: {
      color: '#6b7280',
      width: 1,
      dash: 'dot'
    },
    showlegend: false,
    hoverinfo: 'skip'
  });

  const layout = {
    title: {
      text: `${strategyName} - Profit & Loss at Expiration`,
      font: { color: '#ffffff', size: 16 }
    },
    xaxis: {
      title: { text: 'Stock Price ($)', font: { color: '#9ca3af' } },
      color: '#9ca3af',
      gridcolor: '#374151',
      zeroline: false
    },
    yaxis: {
      title: { text: 'Profit / Loss ($)', font: { color: '#9ca3af' } },
      color: '#9ca3af',
      gridcolor: '#374151',
      zeroline: false
    },
    plot_bgcolor: '#1f2937',
    paper_bgcolor: '#1f2937',
    font: { color: '#ffffff' },
    showlegend: true,
    legend: {
      x: 0,
      y: 1,
      bgcolor: 'rgba(31, 41, 55, 0.8)',
      bordercolor: '#4b5563',
      borderwidth: 1,
      font: { color: '#ffffff', size: 12 }
    },
    margin: { t: 50, r: 30, b: 60, l: 60 },
    height: height,
    hovermode: 'x unified'
  };

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: [
      'pan2d', 'lasso2d', 'select2d', 'autoScale2d', 'resetScale2d'
    ],
    displaylogo: false,
    responsive: true
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-600 overflow-hidden">
      <Plot
        data={plotData}
        layout={layout}
        config={config}
        useResizeHandler={true}
        style={{ width: '100%', height: `${height}px` }}
        className="plotly-chart"
      />
    </div>
  );
};

export default InteractiveOptionsChart;
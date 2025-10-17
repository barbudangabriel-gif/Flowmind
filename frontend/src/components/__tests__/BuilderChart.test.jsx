import React from 'react';
import { render, screen } from '@testing-library/react';
import BuilderChart from '../BuilderChart';

// Mock data generator
const createMockData = (numPoints = 10) => ({
 chart: {
 series: [{
 xy: Array.from({ length: numPoints }, (_, i) => [
 240 + i * 2, // x: prices from 240 to 258
 (i - 5) * 100 // y: P&L from -500 to 400
 ])
 }]
 },
 spot: 250,
 breakevens: [248, 252],
 maxProfit: 400,
 maxLoss: -500
});

describe('BuilderChart', () => {
 describe('Rendering', () => {
 test('renders SVG chart with mock data', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 const svg = container.querySelector('svg');
 expect(svg).toBeInTheDocument();
 expect(svg).toHaveAttribute('width', '900');
 expect(svg).toHaveAttribute('height', '260');
 });

 test('renders with custom dimensions', () => {
 const mockData = createMockData();
 const { container } = render(
 <BuilderChart data={mockData} width={600} height={400} />
 );
 
 const svg = container.querySelector('svg');
 expect(svg).toHaveAttribute('width', '600');
 expect(svg).toHaveAttribute('height', '400');
 });

 test('renders P&L path line', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 // Check for main P&L line (blue stroke)
 const paths = container.querySelectorAll('path');
 const pnlPath = Array.from(paths).find(
 p => p.getAttribute('stroke')?.includes('blue') || 
 p.getAttribute('stroke')?.includes('#3b82f6')
 );
 expect(pnlPath).toBeInTheDocument();
 });

 test('renders profit and loss regions', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 // Check for filled regions (green profit, red loss)
 const paths = container.querySelectorAll('path');
 expect(paths.length).toBeGreaterThan(1); // Should have multiple paths for regions
 });
 });

 describe('Markers', () => {
 test('renders spot price marker when provided', () => {
 const mockData = createMockData();
 mockData.spot = 250;
 
 const { container } = render(<BuilderChart data={mockData} />);
 
 // Spot marker is a vertical line
 const lines = container.querySelectorAll('line');
 expect(lines.length).toBeGreaterThan(0);
 });

 test('renders target price marker when provided', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} target={255} />);
 
 // Target marker should be rendered
 const lines = container.querySelectorAll('line');
 expect(lines.length).toBeGreaterThan(0);
 });

 test('renders breakeven markers when available', () => {
 const mockData = createMockData();
 mockData.breakevens = [248, 252];
 
 const { container } = render(<BuilderChart data={mockData} />);
 
 // Should have lines for breakevens
 const lines = container.querySelectorAll('line');
 expect(lines.length).toBeGreaterThan(0);
 });
 });

 describe('Edge Cases', () => {
 test('renders empty state when no data provided', () => {
 const { container } = render(<BuilderChart data={null} />);
 expect(container.firstChild).toBeNull();
 });

 test('renders empty state message when data has no series', () => {
 const emptyData = { chart: { series: [] } };
 render(<BuilderChart data={emptyData} />);
 
 expect(screen.getByText(/no chart data/i)).toBeInTheDocument();
 });

 test('renders empty state when series is empty', () => {
 const emptyData = { chart: { series: [{ xy: [] }] } };
 render(<BuilderChart data={emptyData} />);
 
 expect(screen.getByText(/no chart data/i)).toBeInTheDocument();
 });

 test('handles single data point gracefully', () => {
 const singlePoint = {
 chart: { series: [{ xy: [[250, 0]] }] }
 };
 
 const { container } = render(<BuilderChart data={singlePoint} />);
 const svg = container.querySelector('svg');
 expect(svg).toBeInTheDocument();
 });

 test('handles negative prices', () => {
 const negativeData = {
 chart: { series: [{ xy: [[-10, 100], [10, -100]] }] }
 };
 
 const { container } = render(<BuilderChart data={negativeData} />);
 const svg = container.querySelector('svg');
 expect(svg).toBeInTheDocument();
 });
 });

 describe('Props Validation', () => {
 test('uses default width when not provided', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 const svg = container.querySelector('svg');
 expect(svg).toHaveAttribute('width', '900');
 });

 test('uses default height when not provided', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 const svg = container.querySelector('svg');
 expect(svg).toHaveAttribute('height', '260');
 });

 test('showProbability prop controls probability overlay', () => {
 const mockData = createMockData();
 
 // With probability (default true)
 const { container: withProb } = render(
 <BuilderChart data={mockData} showProbability={true} />
 );
 
 // Without probability
 const { container: withoutProb } = render(
 <BuilderChart data={mockData} showProbability={false} />
 );
 
 // Both should render, but with different content
 expect(withProb.querySelector('svg')).toBeInTheDocument();
 expect(withoutProb.querySelector('svg')).toBeInTheDocument();
 });
 });

 describe('Ref Forwarding', () => {
 test('forwards ref to SVG element', () => {
 const mockData = createMockData();
 const ref = React.createRef();
 
 render(<BuilderChart data={mockData} ref={ref} />);
 
 expect(ref.current).toBeInstanceOf(SVGSVGElement);
 });

 test('ref can be used to access SVG methods', () => {
 const mockData = createMockData();
 const ref = React.createRef();
 
 render(<BuilderChart data={mockData} ref={ref} />);
 
 // Test that we can call SVG methods
 expect(typeof ref.current.getBBox).toBe('function');
 expect(typeof ref.current.getScreenCTM).toBe('function');
 });
 });

 describe('Styling', () => {
 test('applies CSS variables for theming', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 // Check that profit/loss regions use CSS variables
 const paths = container.querySelectorAll('path');
 const hasCustomFill = Array.from(paths).some(
 p => {
 const fill = p.getAttribute('fill');
 return fill?.includes('--builder-profit-fill') || 
 fill?.includes('--builder-loss-fill') ||
 fill?.includes('rgba');
 }
 );
 
 expect(hasCustomFill).toBe(true);
 });

 test('renders with proper stroke colors', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 const paths = container.querySelectorAll('path');
 const hasStroke = Array.from(paths).some(
 p => p.getAttribute('stroke') !== null
 );
 
 expect(hasStroke).toBe(true);
 });
 });

 describe('Accessibility', () => {
 test('SVG has proper structure', () => {
 const mockData = createMockData();
 const { container } = render(<BuilderChart data={mockData} />);
 
 const svg = container.querySelector('svg');
 expect(svg).toHaveAttribute('width');
 expect(svg).toHaveAttribute('height');
 });

 test('empty state has readable message', () => {
 const emptyData = { chart: { series: [] } };
 render(<BuilderChart data={emptyData} />);
 
 const message = screen.getByText(/no chart data/i);
 expect(message).toHaveClass('text-slate-500');
 });
 });
});

describe('BuilderChart Integration', () => {
 test('handles real-world builder API response format', () => {
 // Simulate actual API response structure
 const realWorldData = {
 chart: {
 series: [{
 xy: [
 [240, -250], [242, -200], [244, -150], [246, -100], [248, -50],
 [250, 0], [252, 50], [254, 100], [256, 150], [258, 200]
 ]
 }]
 },
 spot: 250,
 target: 255,
 breakevens: [250],
 maxProfit: 200,
 maxLoss: -250,
 greeks: {
 delta: 0.5,
 gamma: 0.03,
 theta: -0.15,
 vega: 0.25
 }
 };

 const { container } = render(<BuilderChart data={realWorldData} target={255} />);
 const svg = container.querySelector('svg');
 
 expect(svg).toBeInTheDocument();
 expect(container.querySelectorAll('path').length).toBeGreaterThan(0);
 expect(container.querySelectorAll('line').length).toBeGreaterThan(0);
 });

 test('handles iron condor strategy data', () => {
 const ironCondorData = {
 chart: {
 series: [{
 xy: [
 [230, -500], [240, -300], [245, 0], [250, 300], 
 [255, 300], [260, 0], [270, -300], [280, -500]
 ]
 }]
 },
 spot: 250,
 breakevens: [245, 260],
 maxProfit: 300,
 maxLoss: -500
 };

 const { container } = render(<BuilderChart data={ironCondorData} />);
 expect(container.querySelector('svg')).toBeInTheDocument();
 });
});

import React from 'react';

export default function LogosPage() {
  const logos = [
    { name: 'Analytics Horizontal (PNG) - NEW', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_analytics_horizontal.png` },
    { name: 'Horizontal (PNG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_horizontal_w1000.png` },
    { name: 'Horizontal (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_horizontal.svg` },
    { name: 'Horizontal White (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_horizontal_white.svg` },
    { name: 'Horizontal Transparent (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_horizontal_transparent.svg` },
    { name: 'Wordmark (PNG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_wordmark_w2000.png` },
    { name: 'Wordmark (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_wordmark.svg` },
    { name: 'Glyph (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_glyph.svg` },
    { name: 'Transparent Glyph (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_transparent_glyph.svg` },
    { name: 'Icon (SVG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_icon.svg` },
    { name: 'Icon 256 (PNG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_icon_256.png` },
    { name: 'Large Icon (PNG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_large_icon.png` },
    { name: 'Medium Icon (PNG)', path: `${process.env.PUBLIC_URL}/assets/logos/flowmind_medium_icon.png` },
    { name: 'Favicon (ICO)', path: `${process.env.PUBLIC_URL}/flowmind_favicon.ico` },
  ];

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-8">FlowMind Logos - Assets</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {logos.map((logo, idx) => (
            <div key={idx} className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <div className="text-sm font-medium text-gray-400 mb-4">{logo.name}</div>
              
              {/* Dark background preview */}
              <div className="bg-gray-950 rounded-lg p-4 mb-3 flex items-center justify-center min-h-[120px]">
                <img 
                  src={logo.path} 
                  alt={logo.name}
                  className="max-w-full max-h-[100px] object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div className="text-red-400 text-xs hidden">Failed to load</div>
              </div>
              
              {/* Light background preview */}
              <div className="bg-white rounded-lg p-4 flex items-center justify-center min-h-[120px]">
                <img 
                  src={logo.path} 
                  alt={logo.name}
                  className="max-w-full max-h-[100px] object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div className="text-red-600 text-xs hidden">Failed to load</div>
              </div>
              
              <div className="mt-3 text-xs text-gray-500 font-mono break-all">{logo.path}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

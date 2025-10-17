import React from 'react';
import PerfectOptionCard from './PerfectOptionCard';

const CardTest = () => {
 return (
 <div className="min-h-screen bg-gray-900 p-8">
 <div className="max-w-4xl mx-auto">
 <h1 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-8 text-center">
 Perfect OptionStrat Card Test
 </h1>
 
 <div className="flex justify-center items-center">
 <div className="p-8 bg-gray-800 rounded-lg">
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4 text-center">
 Single Perfect Card - EXACT OptionStrat.com Style
 </h2>
 
 <PerfectOptionCard 
 strategyName="Long Call"
 strikes="18C"
 returnOnRisk="113%"
 chance="43%"
 profit="$1,016.22"
 risk="$900"
 currentPrice={27.30}
 breakeven={27.30}
 />
 </div>
 </div>
 </div>
 </div>
 );
};

export default CardTest;
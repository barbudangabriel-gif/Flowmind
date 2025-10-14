// Minimal App.js for testing
import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          FlowMind 🚀
        </h1>
        <p className="text-slate-300 text-lg">
          Minimal test page - Webpack is working!
        </p>
        <div className="mt-8 p-6 bg-slate-800 rounded-lg inline-block">
          <p className="text-emerald-400 font-semibold">
            ✅ React rendering
          </p>
          <p className="text-blue-400 font-semibold">
            ✅ Tailwind CSS working
          </p>
          <p className="text-purple-400 font-semibold">
            ✅ Ready to add components
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;

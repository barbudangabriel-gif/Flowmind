import React from 'react';
import { Link } from 'react-router-dom';

export default function OptionsModule() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <h1 className="text-2xl font-bold mb-4">Options Module</h1>
      <div className="space-y-2">
        <Link to="/options/selling" className="inline-block bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">Go to Option Selling</Link>
      </div>
    </div>
  );
}
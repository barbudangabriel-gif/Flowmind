import React from "react";
import { Link } from "react-router-dom";

export default function QuickActionButton({ icon, label, href, gradient }) {
  return (
    <Link to={href} className={`flex flex-col items-center justify-center p-4 rounded-lg shadow-lg bg-slate-800/60 border border-slate-700 hover:border-blue-500 transition-all hover:scale-105 ${gradient ? `bg-gradient-to-br ${gradient}` : ''}`}>
      <span className="text-3xl mb-2">{icon}</span>
      <span className="text-white font-semibold text-lg">{label}</span>
    </Link>
  );
}

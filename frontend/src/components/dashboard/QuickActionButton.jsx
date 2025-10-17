import React from "react";
import { Link } from "react-router-dom";

export default function QuickActionButton({ icon, label, href, gradient }) {
 return (
 <Link to={href} className={`flex flex-col items-center justify-center p-4 rounded-lg shadow-lg bg-[#0a0e1a] border border-[#1a1f26] hover:border-blue-500 transition-all hover:scale-105 ${gradient ? `bg-gradient-to-br ${gradient}` : ''}`}>
 <span className="text-xl mb-2">{icon}</span>
 <span className="text-[rgb(252, 251, 255)] text-base">{label}</span>
 </Link>
 );
}

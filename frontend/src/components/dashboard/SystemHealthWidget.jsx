import React from "react";

export default function SystemHealthWidget({ services = [] }) {
 const getStatusColor = (status) => {
 if (status === "connected") return "text-green-400";
 if (status === "fallback") return "text-yellow-400";
 return "text-red-400";
 };

 const getStatusIcon = (status) => {
 if (status === "connected") return "";
 if (status === "fallback") return "";
 return "";
 };

 return (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4">
 <h3 className="text-[20px] text-[rgb(252, 251, 255)] mb-4"> System Health</h3>
 <div className="space-y-3">
 {services.map((service, idx) => (
 <div key={idx} className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-2 flex justify-between items-center">
 <div className="flex items-center gap-3">
 <span className="text-xl">{getStatusIcon(service.status)}</span>
 <div>
 <div className="text-[rgb(252, 251, 255)]">{service.name}</div>
 {service.mode && <div className="text-lg text-gray-400">Mode: {service.mode}</div>}
 {service.fallback && <div className="text-lg text-yellow-400">Using in-memory fallback</div>}
 </div>
 </div>
 <div className={`font-medium ${getStatusColor(service.status)}`}>
 {service.status.toUpperCase()}
 </div>
 </div>
 ))}
 </div>
 </div>
 );
}

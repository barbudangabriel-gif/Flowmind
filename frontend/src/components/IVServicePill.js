import { useEffect, useState } from "react";
import { ivClient } from "../services/ivClient";

export default function IVServicePill() {
 const [ok, setOk] = useState(null);
 const [impl, setImpl] = useState("—");
 const [lat, setLat] = useState(0);

 useEffect(() => {
 let mounted = true;
 const t0 = performance.now();
 
 ivClient.status()
 .then(d => { 
 if (!mounted) return; 
 setOk(!!d.ok); 
 setImpl(d.impl || ""); 
 setLat(performance.now() - t0); 
 })
 .catch(() => { 
 if (!mounted) return; 
 setOk(false); 
 setImpl("n/a"); 
 setLat(0); 
 });
 
 return () => { mounted = false; };
 }, []);

 const color = ok === null ? "bg-gray-400" : ok ? "bg-green-500" : "bg-red-500";
 const title = ok ? `IV: ${impl} • ${lat.toFixed(0)}ms` : "IV: offline";

 return (
 <span 
 className={`inline-flex items-center gap-2 px-2 py-1 rounded-full text-lg font-medium ${
 ok ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
 }`} 
 title={title}
 >
 <span className={`w-2 h-2 rounded-full ${color}`} />
 {ok ? `IV ${impl}` : "IV offline"}
 </span>
 );
}
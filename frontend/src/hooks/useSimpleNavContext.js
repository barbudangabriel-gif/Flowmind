// Simple Nav Context Hook
import { useState, useEffect } from 'react';

export function useSimpleNavContext() {
 const [ctx, setCtx] = useState({
 role: "user",
 flags: { TS_LIVE: false, ORDERS_LIVE: false },
 metrics: { ivOnline: true, verifiedRatio: 0.31 },
 mindfolios: [
 { id: "ts-main", name: "TS Main", nav: 969473 },
 { id: "long-term", name: "Long Term", nav: 45000 },
 { id: "medium-term", name: "Medium Term", nav: 23000 },
 ]
 });

 const [loading, setLoading] = useState(true);

 useEffect(() => {
 // Simulate context loading with safe defaults
 const timer = setTimeout(() => {
 // Check admin role
 const isAdmin = window.location.hostname.includes('localhost') || 
 window.location.search.includes('admin=1');
 
 // Orders live flag
 const ordersLive = process.env.NODE_ENV === 'development' || 
 window.location.search.includes('orders_live=1');

 setCtx(prev => ({
 ...prev,
 role: isAdmin ? 'admin' : 'user',
 flags: {
 ...prev.flags,
 ORDERS_LIVE: ordersLive
 }
 }));
 
 setLoading(false);
 }, 1000);

 return () => clearTimeout(timer);
 }, []);

 return { ctx, loading };
}
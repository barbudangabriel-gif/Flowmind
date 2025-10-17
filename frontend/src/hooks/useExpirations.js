// hooks/useExpirations.js
import { useEffect, useState } from "react";

export function useExpirations(symbol) {
 const [list, setList] = useState([]);
 const [loading, setLoading] = useState(true);

 useEffect(() => {
 let alive = true;
 (async () => {
 setLoading(true);
 try {
 const API = process.env.REACT_APP_BACKEND_URL || "";
 const r = await fetch(`${API}/api/options/expirations?symbol=${encodeURIComponent(symbol)}`);
 const js = r.ok ? await r.json() : { expirations: [] };
 const arr = (js.expirations ?? []).map((d) => d.slice(0, 10)).sort();
 
 // fallback: 12 "third Friday" monthly starting from current month
 setList(arr.length ? arr : fallbackExpirations());
 } catch {
 setList(fallbackExpirations());
 } finally { 
 if (alive) setLoading(false); 
 }
 })();
 return () => { alive = false; };
 }, [symbol]);

 return { list, loading };
}

function fallbackExpirations() {
 const out = []; 
 const now = new Date();
 
 // Generate expiration dates for next 12 months
 for (let i = 0; i < 12; i++) {
 const year = now.getFullYear();
 const month = now.getMonth() + i;
 const targetYear = year + Math.floor(month / 12);
 const targetMonth = month % 12;
 
 // Third Friday (Monthly OPEX)
 const monthlyOpex = thirdFriday(new Date(targetYear, targetMonth, 1));
 out.push(monthlyOpex.toISOString().slice(0, 10));
 
 // Add weekly expirations for first 3 months (more realistic)
 if (i < 3) {
 // First Friday
 const firstFriday = firstFridayOfMonth(new Date(targetYear, targetMonth, 1));
 if (firstFriday.getTime() !== monthlyOpex.getTime()) {
 out.push(firstFriday.toISOString().slice(0, 10));
 }
 
 // Second Friday
 const secondFriday = new Date(firstFriday);
 secondFriday.setDate(firstFriday.getDate() + 7);
 if (secondFriday.getTime() !== monthlyOpex.getTime()) {
 out.push(secondFriday.toISOString().slice(0, 10));
 }
 
 // Fourth Friday (if exists)
 const fourthFriday = new Date(monthlyOpex);
 fourthFriday.setDate(monthlyOpex.getDate() + 7);
 if (fourthFriday.getMonth() === targetMonth) {
 out.push(fourthFriday.toISOString().slice(0, 10));
 }
 }
 }
 
 return out.sort();
}

function firstFridayOfMonth(d) {
 const first = new Date(d.getFullYear(), d.getMonth(), 1);
 const day = first.getDay(); // 0=Sun
 const offsetToFri = (5 - day + 7) % 7;
 const firstFri = 1 + offsetToFri;
 return new Date(d.getFullYear(), d.getMonth(), firstFri, 21, 0, 0);
}

function thirdFriday(d) {
 const first = new Date(d.getFullYear(), d.getMonth(), 1);
 const day = first.getDay(); // 0=Sun
 const offsetToFri = (5 - day + 7) % 7;
 const third = 1 + offsetToFri + 14;
 return new Date(d.getFullYear(), d.getMonth(), third, 21, 0, 0); // 21:00 UTC on close
}
import { useCallback, useLayoutEffect, useRef, useState } from "react";

export default function useHardGate(timeoutMs = 1800) {
 const [ready, setReady] = useState(false);
 const raf1Ref = useRef(0);
 const raf2Ref = useRef(0);
 const timerRef = useRef(0);
 const armedRef = useRef(false); // idempotent guard

 const ensureReady = useCallback(() => {
 if (armedRef.current) return; // deja s-a setat
 armedRef.current = true;
 setReady(true);
 // cleanup dacă vine înainte de unmount
 if (raf1Ref.current) cancelAnimationFrame(raf1Ref.current);
 if (raf2Ref.current) cancelAnimationFrame(raf2Ref.current);
 if (timerRef.current) clearTimeout(timerRef.current);
 }, []);

 useLayoutEffect(() => {
 // 2x RAF ca să așteptăm primul paint
 raf1Ref.current = requestAnimationFrame(() => {
 raf2Ref.current = requestAnimationFrame(() => ensureReady());
 });
 // backstop hard dacă ceva blochează RAF
 timerRef.current = window.setTimeout(() => ensureReady(), timeoutMs);

 return () => {
 if (raf1Ref.current) cancelAnimationFrame(raf1Ref.current);
 if (raf2Ref.current) cancelAnimationFrame(raf2Ref.current);
 if (timerRef.current) clearTimeout(timerRef.current);
 };
 // eslint-disable-next-line react-hooks/exhaustive-deps
 }, [timeoutMs]); // ensureReady e stabil prin useCallback

 return [ready, ensureReady];
}
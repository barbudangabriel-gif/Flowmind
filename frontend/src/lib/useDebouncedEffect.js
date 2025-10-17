// frontend/src/lib/useDebouncedEffect.js
import { useEffect, useRef } from 'react';

export default function useDebouncedEffect(effect, deps, delay = 300) {
  const t = useRef(null);
  useEffect(() => {
    if (t.current) clearTimeout(t.current);
    t.current = setTimeout(() => effect(), delay);
    return () => t.current && clearTimeout(t.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

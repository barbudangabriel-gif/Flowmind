import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Minimal httpGet for API client
export async function httpGet(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Default source for GEX summary
export const SOURCE_DEFAULT = "real";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
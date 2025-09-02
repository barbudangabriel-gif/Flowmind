const BASE = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || "http://localhost:8001";

async function jget(path) {
  const r = await fetch(`${BASE}${path}`, { credentials: "include" });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export const ivClient = {
  status: () => jget("/_redis/diag"),
  btStatus: (key) => jget(`/_bt/status${key ? `?key=${encodeURIComponent(key)}` : ""}`),
  screener: (q = "") => jget(`/screen/iv-setups${q}`),
};
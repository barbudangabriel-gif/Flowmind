import { useState } from "react";

export default function useOptionsSelling() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const compute = async (payload) => {
    try {
      setLoading(true); setError("");
      const resp = await fetch(`${backendUrl}/api/options/selling/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const json = await resp.json();
      if (!resp.ok || json.status !== 'success') throw new Error(json.detail || 'Compute failed');
      setData(json.data);
      return json.data;
    } catch (e) {
      setError(e.message);
      setData(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, data, compute };
}
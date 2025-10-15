const BASE = process.env.REACT_APP_BACKEND_URL || "";

async function fetchJSON(path) {
  const response = await fetch(`${BASE}${path}`);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const dashboardClient = {
  getSummary: () => fetchJSON("/api/dashboard/summary"),
};

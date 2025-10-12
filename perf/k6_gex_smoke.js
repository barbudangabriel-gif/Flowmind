// k6 run perf/k6_gex_smoke.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s'
};

const BASE = __ENV.FLOWMIND_BASE_URL || 'http://localhost:8000';

export default function () {
  const url = `${BASE}/api/v1/analytics/gex?symbol=TSLA&expiry=2025-11-21&range=ATM10`;
  const res = http.get(url, { headers: { 'Accept': 'application/json' } });
  check(res, {
    'status 200': (r) => r.status === 200,
    'has fields': (r) => r.json('strikes') && r.json('gex') && r.json('walls'),
    'p95 target': (r) => r.timings.duration < 800,
  });
  sleep(1);
}

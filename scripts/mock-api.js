import express from "express";
import cors from "cors";

const app = express();
// For Codespaces: listen on all interfaces
const PORT = process.env.PORT || 5174;
const HOST = "0.0.0.0";

app.use(cors({ origin: true }));
app.use(express.json());

// Helper: random delay (50-350ms)
function withDelay(handler) {
  return (req, res) => {
    const delay = Math.floor(Math.random() * 300) + 50;
    setTimeout(() => handler(req, res), delay);
  };
}

// ---- MOCK ROUTES ----

// FIS Score
app.get("/fis/score", withDelay((req, res) => {
  const { symbol = "TSLA" } = req.query;
  console.log(`[MOCK] /fis/score?symbol=${symbol}`);
  res.json({
    symbol,
    score: Math.floor(Math.random() * 101),
    components: {
      dealer_positioning: (Math.random() * 100).toFixed(1),
      volatility_state: (Math.random() * 100).toFixed(1),
      flow_bias: (Math.random() * 100).toFixed(1),
      fundamentals: (Math.random() * 100).toFixed(1)
    }
  });
}));

// IVX
app.get("/analytics/ivx", withDelay((req, res) => {
  const symbol = req.query.symbol || "TSLA";
  console.log(`[MOCK] /analytics/ivx?symbol=${symbol}`);
  res.json({
    symbol,
    ivx: (Math.random() * 50 + 10).toFixed(2),
    rank: (Math.random() * 100).toFixed(1),
    percentile: (Math.random() * 100).toFixed(1)
  });
}));

// GEX
app.get("/options/gex", withDelay((req, res) => {
  const symbol = req.query.symbol || "TSLA";
  console.log(`[MOCK] /options/gex?symbol=${symbol}`);
  const strikes = Array.from({ length: 10 }, (_, i) => 900 + i * 10);
  const gex = strikes.map(() => Math.random() * 1000 - 500);
  res.json({
    symbol,
    expiry: "2025-10-18",
    walls: { call: 1020, put: 940 },
    strikes,
    gex
  });
}));

// Flow Bias
app.get("/flow/bias", withDelay((req, res) => {
  const symbol = req.query.symbol || "TSLA";
  console.log(`[MOCK] /flow/bias?symbol=${symbol}`);
  res.json({
    symbol,
    sweeps: Math.floor(Math.random() * 300),
    blocks: Math.floor(Math.random() * 200),
    bias: Math.random() > 0.5 ? "bullish" : "bearish"
  });
}));

// ---- START SERVER ----
app.listen(PORT, HOST, () => {
  console.log(`Mock API running on http://${HOST}:${PORT}`);
});

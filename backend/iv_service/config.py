import os

IV_PROVIDER = os.getenv("IV_PROVIDER", "STUB").upper()  # STUB | TS
DEFAULT_FRONT_DTE = int(os.getenv("IV_FRONT_DTE", "3"))
DEFAULT_BACK_DTE = int(os.getenv("IV_BACK_DTE", "35"))
CACHE_TTL_SECONDS = int(os.getenv("IV_CACHE_TTL", "30"))

# TradeStation adapter (schelet — completezi endpoint-urile reale)
TS_BASE_URL = os.getenv("TS_BASE_URL", "").rstrip("/")
TS_TOKEN = os.getenv("TS_TOKEN", "")

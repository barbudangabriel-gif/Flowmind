"""
TradeStation API Configuration
Centralized configuration for TradeStation integration with robust token refresh
"""

import os

# TradeStation API Configuration
TS_BASE_URL = os.getenv("TS_BASE_URL", "https://api.tradestation.com")
TS_CLIENT_ID = os.getenv("TRADESTATION_API_KEY", "")
TS_CLIENT_SECRET = os.getenv("TRADESTATION_API_SECRET", "")
TS_REDIRECT_URI = os.getenv("TRADESTATION_REDIRECT_URI", "http://localhost:8080")

# Token refresh settings
TOKEN_SKEW_SECONDS = int(
    os.getenv("TOKEN_SKEW_SECONDS", "60")
)  # Refresh 60s before expiration
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "8.0"))  # 8 second timeout

# Environment
TS_ENVIRONMENT = os.getenv("TRADESTATION_ENVIRONMENT", "LIVE")

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# MongoDB for token storage
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

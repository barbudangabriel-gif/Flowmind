import os

# Flow settings
UW_LIVE = os.getenv("UW_LIVE", "0") == "1"
UW_MIN_PREMIUM = int(os.getenv("UW_MIN_PREMIUM", "25000"))

# Database
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/flowmind")

# Other settings can go here
DEBUG = os.getenv("DEBUG", "0") == "1"

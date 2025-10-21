import logging
import os
import re
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("watchlist.db")

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
watchlists_collection = db.watchlists

# Symbol validation regex
SYMBOL_REGEX = re.compile(r"^[A-Z0-9.\-]{1,15}$", re.IGNORECASE)


async def init_db():
    """Initialize database indices"""
    await watchlists_collection.create_index("name", unique=True)
    logger.info("Watchlist DB initialized")


def validate_symbol(symbol: str) -> str:
    """Validate și normalize symbol"""
    symbol = symbol.strip().upper()
    if not SYMBOL_REGEX.match(symbol):
        raise ValueError(f"Invalid symbol: {symbol}")
    return symbol


def normalize_symbols(symbols: list) -> list:
    """Normalize și deduplicate symbols"""
    normalized = []
    for sym in symbols:
        try:
            norm = validate_symbol(str(sym))
            if norm not in normalized:
                normalized.append(norm)
        except ValueError:
            continue
    return normalized


async def create_watchlist(name: str, symbols: list, description: str = None) -> dict:
    """Create new watchlist"""
    normalized_symbols = normalize_symbols(symbols)
    doc = {
        "name": name,
        "description": description,
        "symbols": normalized_symbols,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await watchlists_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def get_watchlist(name: str) -> dict:
    """Get watchlist by name"""
    doc = await watchlists_collection.find_one({"name": name})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def update_watchlist(name: str, symbols: list, mode: str = "merge") -> dict:
    """Update watchlist symbols"""
    normalized_symbols = normalize_symbols(symbols)

    if mode == "replace":
        update_symbols = normalized_symbols
    else:  # merge
        existing = await get_watchlist(name)
        if existing:
            existing_symbols = existing.get("symbols", [])
            update_symbols = list(set(existing_symbols + normalized_symbols))
        else:
            update_symbols = normalized_symbols

    doc = {"symbols": update_symbols, "updated_at": datetime.utcnow()}

    await watchlists_collection.update_one({"name": name}, {"$set": doc}, upsert=True)

    return await get_watchlist(name)


async def delete_watchlist(name: str) -> bool:
    """Delete watchlist"""
    result = await watchlists_collection.delete_one({"name": name})
    return result.deleted_count > 0


async def list_watchlists(limit: int = 50) -> list:
    """List watchlists"""
    cursor = watchlists_collection.find({}).limit(limit)
    docs = await cursor.to_list(length=limit)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

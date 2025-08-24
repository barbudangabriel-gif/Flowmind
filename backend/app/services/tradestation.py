"""
TradeStation Token Management Service
Handles token refresh with retry logic, backoff, and observability
"""
from __future__ import annotations
import time
import logging
import requests
import asyncio
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient

try:
    from ..config import (
        TS_BASE_URL, TS_CLIENT_ID, TS_CLIENT_SECRET, TS_REDIRECT_URI, 
        TOKEN_SKEW_SECONDS, HTTP_TIMEOUT, MONGO_URL, DB_NAME
    )
except ImportError:
    # Fallback for direct execution
    import os
    TS_BASE_URL = os.getenv("TS_BASE_URL", "https://api.tradestation.com")
    TS_CLIENT_ID = os.getenv("TRADESTATION_API_KEY", "")
    TS_CLIENT_SECRET = os.getenv("TRADESTATION_API_SECRET", "")
    TS_REDIRECT_URI = os.getenv("TRADESTATION_REDIRECT_URI", "http://localhost:8080")
    TOKEN_SKEW_SECONDS = 60
    HTTP_TIMEOUT = 8.0
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "test_database")

log = logging.getLogger("ts.service")

# MongoDB client for token storage
_mongo_client = None
_db = None

async def init_db():
    """Initialize MongoDB connection for token storage"""
    global _mongo_client, _db
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(MONGO_URL)
        _db = _mongo_client[DB_NAME]
        log.info("MongoDB connection initialized for token storage")

# In-memory store for immediate access (with MongoDB persistence)
_TOKENS: Dict[str, Dict[str, Any]] = {}  # user_id -> {access_token, refresh_token, exp_ts}
_refresh_lock: Dict[str, asyncio.Lock] = {}  # user_id -> lock to prevent concurrent refreshes

def get_refresh_lock(user_id: str) -> asyncio.Lock:
    """Get or create refresh lock for user to prevent concurrent refreshes"""
    if user_id not in _refresh_lock:
        _refresh_lock[user_id] = asyncio.Lock()
    return _refresh_lock[user_id]

async def get_tokens(user_id: str) -> Optional[Dict[str, Any]]:
    """Get tokens from cache or MongoDB"""
    if user_id in _TOKENS:
        return _TOKENS[user_id]
    
    # Try to load from MongoDB
    await init_db()
    if _db:
        try:
            doc = await _db.ts_tokens.find_one({"user_id": user_id})
            if doc:
                token_data = {
                    "access_token": doc["access_token"],
                    "refresh_token": doc["refresh_token"], 
                    "exp_ts": doc["exp_ts"]
                }
                _TOKENS[user_id] = token_data
                log.info(f"Loaded tokens for user {user_id} from MongoDB")
                return token_data
        except Exception as e:
            log.error(f"Error loading tokens from MongoDB: {e}")
    
    return None

async def save_tokens(user_id: str, access: str, refresh: str, expires_in: int) -> Dict[str, Any]:
    """Save tokens to both cache and MongoDB"""
    exp_ts = int(time.time()) + int(expires_in)
    token_data = {
        "access_token": access, 
        "refresh_token": refresh, 
        "exp_ts": exp_ts
    }
    
    # Update cache
    _TOKENS[user_id] = token_data
    
    # Persist to MongoDB
    await init_db()
    if _db:
        try:
            await _db.ts_tokens.replace_one(
                {"user_id": user_id},
                {
                    "user_id": user_id,
                    "access_token": access,
                    "refresh_token": refresh,
                    "exp_ts": exp_ts,
                    "updated_at": time.time()
                },
                upsert=True
            )
            log.info(f"Tokens saved for user {user_id} (expires in {expires_in}s)")
        except Exception as e:
            log.error(f"Error saving tokens to MongoDB: {e}")
    
    return token_data

def is_expiring(token: Dict[str, Any]) -> bool:
    """Check if token is expiring within skew seconds"""
    return int(time.time()) >= int(token.get("exp_ts", 0)) - TOKEN_SKEW_SECONDS

def get_expires_in(token: Dict[str, Any]) -> int:
    """Get seconds until token expiration"""
    return max(0, int(token.get("exp_ts", 0)) - int(time.time()))

def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh access token with retry logic and exponential backoff
    Returns: {access_token, refresh_token, expires_in, ...}
    """
    url = f"{TS_BASE_URL}/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": TS_CLIENT_ID,
        "client_secret": TS_CLIENT_SECRET,
        "redirect_uri": TS_REDIRECT_URI,
    }
    
    log.info(f"Attempting to refresh token using refresh_token ending in ...{refresh_token[-6:] if len(refresh_token) > 6 else 'short'}")
    
    # Retry with exponential backoff
    last_error = None
    for attempt in range(3):
        try:
            start_time = time.time()
            r = requests.post(url, data=payload, timeout=HTTP_TIMEOUT)
            elapsed = time.time() - start_time
            
            log.info(f"Token refresh attempt {attempt + 1}: {r.status_code} ({elapsed:.2f}s)")
            
            if r.status_code == 200:
                data = r.json()
                log.info(f"✅ Token refresh successful: new token expires in {data.get('expires_in', 'unknown')}s")
                return data
            else:
                last_error = (r.status_code, r.text[:500])
                log.warning(f"Token refresh failed: {r.status_code} - {r.text[:200]}")
                
        except requests.RequestException as e:
            last_error = ("EXC", str(e))
            log.error(f"Network error during token refresh: {e}")
        except Exception as e:
            last_error = ("EXC", str(e))
            log.error(f"Unexpected error during token refresh: {e}")
        
        # Exponential backoff: 0.5s, 1s, 2s
        if attempt < 2:
            sleep_time = 0.5 * (2 ** attempt)
            log.info(f"Retrying token refresh in {sleep_time}s...")
            time.sleep(sleep_time)
    
    error_msg = f"Token refresh failed after 3 attempts: {last_error}"
    log.error(error_msg)
    raise RuntimeError(error_msg)

async def ensure_valid_token(user_id: str) -> str:
    """
    Ensure user has a valid access token, refreshing if necessary.
    Thread-safe to prevent concurrent refresh attempts.
    Returns: access_token
    """
    # Use lock to prevent concurrent refreshes for same user
    async with get_refresh_lock(user_id):
        token = await get_tokens(user_id)
        if not token:
            raise RuntimeError("not_authenticated")
        
        # Check if token needs refresh
        if is_expiring(token):
            log.info(f"Token expiring for user {user_id} (expires in {get_expires_in(token)}s), refreshing...")
            
            try:
                # Perform synchronous refresh (could be made async in production)
                refresh_data = refresh_access_token(token["refresh_token"])
                
                # Save new tokens
                new_token = await save_tokens(
                    user_id, 
                    refresh_data["access_token"], 
                    refresh_data.get("refresh_token", token["refresh_token"]), 
                    refresh_data.get("expires_in", 900)
                )
                
                log.info(f"✅ Token refreshed successfully for user {user_id}")
                return new_token["access_token"]
                
            except Exception as e:
                log.error(f"❌ Failed to refresh token for user {user_id}: {e}")
                raise RuntimeError(f"refresh_failed: {e}")
        
        else:
            log.debug(f"Token still valid for user {user_id} (expires in {get_expires_in(token)}s)")
            return token["access_token"]

# Health check function
async def health_check() -> Dict[str, Any]:
    """Check service health"""
    try:
        await init_db()
        
        # Check if we can connect to MongoDB
        mongo_ok = False
        if _mongo_client:
            try:
                await _mongo_client.admin.command('ping')
                mongo_ok = True
            except Exception:
                pass
        
        # Check if TradeStation config is available
        config_ok = bool(TS_CLIENT_ID and TS_CLIENT_SECRET)
        
        return {
            "status": "healthy" if (mongo_ok and config_ok) else "degraded",
            "mongodb": "connected" if mongo_ok else "disconnected", 
            "tradestation_config": "configured" if config_ok else "missing",
            "active_sessions": len(_TOKENS),
            "timestamp": time.time()
        }
        
    except Exception as e:
        log.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
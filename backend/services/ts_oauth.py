import logging
import os
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

TS_TOKEN_URL = os.getenv("TS_TOKEN_URL", "https://signin.tradestation.com/oauth/token")
TS_CLIENT_ID = os.getenv("TS_CLIENT_ID", os.getenv("TRADESTATION_API_KEY"))
TS_CLIENT_SECRET = os.getenv("TS_CLIENT_SECRET", os.getenv("TRADESTATION_API_SECRET"))

MARGIN = int(
    os.getenv("TS_TOKEN_MARGIN_SEC", "120")
)  # reîmprospătare cu ~2min înainte de expirare


def get_token(db) -> Optional[dict]:
    """Get TS token from database (Redis/MongoDB)"""
    try:
        # Pentru Redis (current setup)
        if hasattr(db, "get"):
            token_data = db.get("ts_oauth_token")
            if token_data:
                import json

                return json.loads(token_data)
        # Pentru MongoDB sau altele
        elif hasattr(db, "find_one"):
            doc = db.oauth_tokens.find_one({"provider": "TS"})
            if doc:
                return {
                    "access_token": doc.get("access_token"),
                    "refresh_token": doc.get("refresh_token"),
                    "expires_at": doc.get("expires_at"),
                }
    except Exception as e:
        logger.error(f"Error getting token: {e}")
    return None


def save_token(db, t: dict):
    """Save TS token to database"""
    try:
        # Pentru Redis (current setup)
        if hasattr(db, "set"):
            import json

            db.set("ts_oauth_token", json.dumps(t), ex=86400 * 7)  # 7 days
        # Pentru MongoDB sau altele
        elif hasattr(db, "update_one"):
            db.oauth_tokens.update_one(
                {"provider": "TS"},
                {
                    "$set": {
                        "provider": "TS",
                        "access_token": t["access_token"],
                        "refresh_token": t.get("refresh_token"),
                        "expires_at": t["expires_at"],
                        "updated_at": time.time(),
                    }
                },
                upsert=True,
            )
    except Exception as e:
        logger.error(f"Error saving token: {e}")


def refresh(db, refresh_token: str) -> dict:
    """Refresh TS access token"""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": TS_CLIENT_ID,
        "client_secret": TS_CLIENT_SECRET,
    }
    r = requests.post(TS_TOKEN_URL, data=data, timeout=15)
    r.raise_for_status()
    j = r.json()
    expires_at = int(time.time()) + int(j.get("expires_in", 3600)) - 30
    out = {
        "access_token": j["access_token"],
        "refresh_token": j.get("refresh_token", refresh_token),
        "expires_at": expires_at,
    }
    save_token(db, out)
    logger.info("TS token refreshed successfully")
    return out


def ensure_access_token(db) -> str:
    """Ensure we have a valid access token, refresh if needed"""
    t = get_token(db)
    if not t:
        raise RuntimeError("TS token missing - please authenticate first")
    if t["expires_at"] - time.time() <= MARGIN:
        logger.info("TS token expiring soon, refreshing...")
        t = refresh(db, t["refresh_token"])
    return t["access_token"]


def authorized_get(db, url: str, params: dict | None = None) -> requests.Response:
    """Make authorized GET request with automatic token refresh on 401"""
    token = ensure_access_token(db)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, params=params, timeout=15)
    if r.status_code == 401:
        # retry o singură dată după refresh
        logger.info("Got 401, refreshing token and retrying...")
        t = refresh(db, get_token(db)["refresh_token"])
        headers["Authorization"] = f"Bearer {t['access_token']}"
        r = requests.get(url, headers=headers, params=params, timeout=15)
    return r


def authorized_post(
    db, url: str, json_data: dict | None = None, params: dict | None = None
) -> requests.Response:
    """Make authorized POST request with automatic token refresh on 401"""
    token = ensure_access_token(db)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(url, headers=headers, json=json_data, params=params, timeout=15)
    if r.status_code == 401:
        # retry o singură dată după refresh
        logger.info("Got 401, refreshing token and retrying...")
        t = refresh(db, get_token(db)["refresh_token"])
        headers["Authorization"] = f"Bearer {t['access_token']}"
        r = requests.post(
            url, headers=headers, json=json_data, params=params, timeout=15
        )
    return r

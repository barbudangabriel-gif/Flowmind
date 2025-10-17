"""TradeStation authentication dependencies."""

import logging
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, Request

from ..services.tradestation import get_valid_token, get_cached_token

log = logging.getLogger("ts.deps")


def get_user_id(request: Request) -> str:
    """Get user ID from request headers or return default."""
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    return "demo"


async def get_bearer_token(user_id: str = Depends(get_user_id)) -> str:
    """Get valid bearer token, auto-refresh if needed."""
    token = await get_valid_token(user_id)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token.get("access_token", "")


async def get_user_token_info(user_id: str = Depends(get_user_id)) -> Dict[str, Any]:
    """Get token info without refreshing."""
    token = get_cached_token(user_id)
    if not token:
        return {"authenticated": False, "expires_in": 0}
    
    import time
    expires_in = max(0, token.get("expires_at", 0) - int(time.time()))
    
    return {
        "authenticated": True,
        "expires_in": expires_in,
        "expires_at": token.get("expires_at", 0),
        "needs_refresh": expires_in <= 60,
    }

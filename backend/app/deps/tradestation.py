"""TradeStation authentication dependencies."""

import logging
from typing import Dict, Any
from fastapi import Depends, HTTPException, Request

from ..services.tradestation import ensure_valid_token, get_tokens, get_expires_in

log = logging.getLogger("ts.deps")


def get_user_id(request: Request) -> str:
    """Get user ID from request headers or return default."""
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    return "demo-user"


async def get_bearer_token(user_id: str = Depends(get_user_id)) -> str:
    """Get valid bearer token, auto-refresh if needed."""
    try:
        access_token = await ensure_valid_token(user_id)
        return access_token
    except RuntimeError as e:
        error_msg = str(e)
        if "not_authenticated" in error_msg:
            raise HTTPException(status_code=401, detail="Not authenticated")
        elif "refresh_failed" in error_msg:
            raise HTTPException(status_code=401, detail="Token refresh failed")
        else:
            raise HTTPException(status_code=500, detail="Auth error")
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


async def get_user_token_info(user_id: str = Depends(get_user_id)) -> Dict[str, Any]:
    """Get token info without refreshing."""
    token = await get_tokens(user_id)
    if not token:
        return {"authenticated": False, "expires_in": 0}
    expires_in = get_expires_in(token)
    return {
        "authenticated": True,
        "expires_in": expires_in,
        "expires_at": token.get("exp_ts", 0),
        "needs_refresh": expires_in <= 60,
    }

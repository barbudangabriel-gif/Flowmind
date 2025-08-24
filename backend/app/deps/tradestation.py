"""
TradeStation Dependency Provider
Provides auto-refreshed bearer tokens for TradeStation API calls
"""
import logging
from fastapi import Depends, HTTPException, Request
from typing import Dict, Any

try:
    from ..services.tradestation import get_tokens, save_tokens, ensure_valid_token, get_expires_in
except ImportError:
    # Fallback - assume we're in the services directory
    from .tradestation import get_tokens, save_tokens, ensure_valid_token, get_expires_in

log = logging.getLogger("ts.deps")

def get_user_id(request: Request) -> str:
    """
    Get user ID from request. In production, this would come from JWT/session.
    For now, we simulate with a default user or header-based identification.
    """
    # Check for user header (for testing)
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    
    # Default demo user for development
    return "demo-user"

async def get_bearer_token(user_id: str = Depends(get_user_id)) -> str:
    """
    Get valid bearer token for TradeStation API.
    Automatically refreshes if token is expiring.
    
    Raises HTTPException(401) if not authenticated or refresh fails.
    """
    try:
        access_token = await ensure_valid_token(user_id)
        log.debug(f"Providing valid access token for user {user_id}")
        return access_token
        
    except RuntimeError as e:
        error_msg = str(e)
        
        if "not_authenticated" in error_msg:
            log.warning(f"User {user_id} not authenticated")
            raise HTTPException(
                status_code=401, 
                detail="Not authenticated. Please login to TradeStation."
            )
        elif "refresh_failed" in error_msg:
            log.error(f"Token refresh failed for user {user_id}: {error_msg}")
            raise HTTPException(
                status_code=401, 
                detail="Token refresh failed. Please re-authenticate with TradeStation."
            )
        else:
            log.error(f"Unexpected error getting token for user {user_id}: {error_msg}")
            raise HTTPException(
                status_code=500, 
                detail="Internal error retrieving authentication token."
            )
    
    except Exception as e:
        log.error(f"Unexpected exception getting token for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Unexpected error retrieving authentication token."
        )

async def get_user_token_info(user_id: str = Depends(get_user_id)) -> Dict[str, Any]:
    """
    Get user token information without refreshing.
    Used for status endpoints.
    """
    token = await get_tokens(user_id)
    if not token:
        return {"authenticated": False, "expires_in": 0}
    
    expires_in = get_expires_in(token)
    return {
        "authenticated": True,
        "expires_in": expires_in,
        "expires_at": token.get("exp_ts", 0),
        "needs_refresh": expires_in <= 60  # TOKEN_SKEW_SECONDS
    }
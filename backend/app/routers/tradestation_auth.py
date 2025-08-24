"""
TradeStation Authentication Router
Robust token management endpoints with observability
"""
import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

try:
    from ..services.tradestation import save_tokens, get_tokens, refresh_access_token, health_check, get_expires_in
    from ..deps.tradestation import get_user_id, get_user_token_info
except ImportError:
    # Fallback imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from services.tradestation import save_tokens, get_tokens, refresh_access_token, health_check, get_expires_in
    from deps.tradestation import get_user_id, get_user_token_info

log = logging.getLogger("ts.router")

router = APIRouter(prefix="/auth/tradestation", tags=["tradestation-auth"])

class TokenInit(BaseModel):
    """Initialize token data"""
    access_token: str
    refresh_token: str
    expires_in: int

class TokenResponse(BaseModel):
    """Token operation response"""
    ok: bool
    message: str = ""
    exp_ts: int = 0
    expires_in: int = 0

@router.post("/init", response_model=TokenResponse)
async def init_tokens(
    body: TokenInit, 
    user_id: str = Depends(get_user_id)
) -> TokenResponse:
    """
    Initialize user tokens (typically called after OAuth flow)
    """
    try:
        log.info(f"Initializing tokens for user {user_id} (expires_in: {body.expires_in}s)")
        
        data = await save_tokens(
            user_id, 
            body.access_token, 
            body.refresh_token, 
            body.expires_in
        )
        
        return TokenResponse(
            ok=True,
            message="Tokens initialized successfully",
            exp_ts=data["exp_ts"],
            expires_in=get_expires_in(data)
        )
        
    except Exception as e:
        log.error(f"Failed to initialize tokens for user {user_id}: {e}")
        raise HTTPException(500, f"Token initialization failed: {str(e)}")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(user_id: str = Depends(get_user_id)) -> TokenResponse:
    """
    Force token refresh (typically called by frontend interceptor)
    """
    try:
        log.info(f"Manual token refresh requested for user {user_id}")
        
        token = await get_tokens(user_id)
        if not token:
            raise HTTPException(401, "Not authenticated - no tokens found")
        
        # Perform refresh
        data = refresh_access_token(token["refresh_token"])
        
        # Save new tokens
        new_token = await save_tokens(
            user_id, 
            data["access_token"], 
            data.get("refresh_token", token["refresh_token"]), 
            data.get("expires_in", 900)
        )
        
        log.info(f"✅ Manual token refresh successful for user {user_id}")
        
        return TokenResponse(
            ok=True,
            message="Token refreshed successfully",
            exp_ts=new_token["exp_ts"],
            expires_in=get_expires_in(new_token)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Manual token refresh failed for user {user_id}: {e}")
        raise HTTPException(401, f"Token refresh failed: {str(e)}")

@router.get("/status")
async def get_auth_status(token_info: Dict[str, Any] = Depends(get_user_token_info)) -> Dict[str, Any]:
    """
    Get authentication status and token expiration info.
    Reports expires_in in seconds for frontend timing.
    """
    response = {
        "authenticated": token_info["authenticated"],
        "expires_in": token_info["expires_in"],  # Seconds until expiration
        "timestamp": int(time.time())
    }
    
    if token_info["authenticated"]:
        response.update({
            "expires_at": token_info["expires_at"],
            "needs_refresh": token_info["needs_refresh"],
            "status": "valid" if not token_info["needs_refresh"] else "expiring_soon"
        })
        
        log.debug(f"Auth status check: expires_in={response['expires_in']}s")
    else:
        response["status"] = "not_authenticated"
        log.debug("Auth status check: not authenticated")
    
    return response

@router.get("/health")
async def health_endpoint() -> Dict[str, Any]:
    """
    Service health check endpoint
    """
    return await health_check()

@router.delete("/logout")
async def logout(user_id: str = Depends(get_user_id)) -> Dict[str, Any]:
    """
    Logout user by clearing tokens
    """
    try:
        # Clear from in-memory cache
        from ..services.tradestation import _TOKENS
        if user_id in _TOKENS:
            del _TOKENS[user_id]
        
        # Clear from MongoDB
        from ..services.tradestation import _db, init_db
        await init_db()
        if _db:
            await _db.ts_tokens.delete_one({"user_id": user_id})
        
        log.info(f"User {user_id} logged out successfully")
        
        return {
            "ok": True,
            "message": "Logged out successfully",
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        log.error(f"Logout failed for user {user_id}: {e}")
        raise HTTPException(500, f"Logout failed: {str(e)}")

# Additional endpoint for testing token validation
@router.get("/validate")
async def validate_token(user_id: str = Depends(get_user_id)) -> Dict[str, Any]:
    """
    Validate current token (triggers auto-refresh if needed)
    """
    try:
        from ..deps.tradestation import get_bearer_token
        
        # This will trigger auto-refresh if needed
        token = await get_bearer_token(user_id)
        
        return {
            "valid": True,
            "message": "Token is valid",
            "token_preview": f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "short_token",
            "timestamp": int(time.time())
        }
        
    except HTTPException as e:
        return {
            "valid": False,
            "error": e.detail,
            "status_code": e.status_code,
            "timestamp": int(time.time())
        }
    except Exception as e:
        log.error(f"Token validation error for user {user_id}: {e}")
        return {
            "valid": False,
            "error": str(e),
            "timestamp": int(time.time())
        }
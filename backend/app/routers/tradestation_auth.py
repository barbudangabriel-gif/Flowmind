"""TradeStation OAuth authentication router."""

import logging
import os
import requests
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from ..services.tradestation import save_tokens
from ..deps.tradestation import get_user_id, get_user_token_info

log = logging.getLogger("ts.auth")
router = APIRouter(tags=["TradeStation Auth"])

# OAuth configuration
TS_CLIENT_ID = os.getenv("TS_CLIENT_ID", "")
TS_CLIENT_SECRET = os.getenv("TS_CLIENT_SECRET", "")
TS_REDIRECT_URI = os.getenv("TS_REDIRECT_URI", "")
TS_MODE = os.getenv("TS_MODE", "SIMULATION")

if TS_MODE == "LIVE":
    TOKEN_URL = "https://signin.tradestation.com/oauth/token"
else:
    TOKEN_URL = "https://sim-signin.tradestation.com/oauth/token"


class TokenInitBody(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


@router.get("/tradestation/auth/callback")
@router.get("/oauth/tradestation/callback")  # Alias pentru .env redirect URI
async def tradestation_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    user_id: str = Depends(get_user_id),
):
    """Handle TradeStation OAuth callback and exchange code for tokens."""
    if error:
        log.error(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    # Exchange code for tokens
    try:
        log.info(f"Exchanging code for tokens (user: {user_id})")

        payload = {
            "grant_type": "authorization_code",
            "client_id": TS_CLIENT_ID,
            "client_secret": TS_CLIENT_SECRET,
            "code": code,
            "redirect_uri": TS_REDIRECT_URI,
        }

        response = requests.post(TOKEN_URL, data=payload, timeout=10)

        if response.status_code == 200:
            token_data = response.json()

            # Save tokens to database
            await save_tokens(
                user_id,
                token_data["access_token"],
                token_data["refresh_token"],
                token_data["expires_in"],
            )

            log.info(f"Successfully authenticated user {user_id}")

            # Redirect to frontend success page
            return {
                "status": "success",
                "message": "Authentication successful!",
                "redirect": "/account/balance",
                "expires_in": token_data["expires_in"],
            }
        else:
            log.error(f"Token exchange failed: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to exchange code: {response.text[:200]}",
            )

    except requests.RequestException as e:
        log.error(f"Network error during token exchange: {e}")
        raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")
    except Exception as e:
        log.error(f"Unexpected error during token exchange: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/tradestation/auth/init")
async def init_tokens(body: TokenInitBody, user_id: str = Depends(get_user_id)):
    """Initialize tokens manually."""
    try:
        token_data = await save_tokens(
            user_id, body.access_token, body.refresh_token, body.expires_in
        )
        return {
            "status": "success",
            "expires_in": body.expires_in,
            "expires_at": token_data["exp_ts"],
        }
    except Exception as e:
        log.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tradestation/auth/status")
async def auth_status(token_info: dict = Depends(get_user_token_info)):
    """Get auth status."""
    return {"status": "success", "data": token_info}


@router.post("/tradestation/auth/logout")
async def logout(user_id: str = Depends(get_user_id)):
    """Logout user."""
    from ..services.tradestation import _TOKENS

    if user_id in _TOKENS:
        del _TOKENS[user_id]
    return {"status": "success"}

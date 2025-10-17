# app/routers/tradestation_auth.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import os
import secrets

from app.services.tradestation import auth_url, exchange_code, set_token, get_cached_token

router = APIRouter(prefix="/ts", tags=["tradestation"])


@router.get("/login")
def ts_login(request: Request):
    """Redirect to TradeStation OAuth login page."""
    redirect_uri = os.getenv("TS_REDIRECT_URI", str(request.url_for("ts_callback")))
    state = secrets.token_urlsafe(16)
    # TODO: salvează 'state' în sesiune/cookie pentru CSRF
    return RedirectResponse(auth_url(redirect_uri, state))


@router.get("/callback", name="ts_callback")
async def ts_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    """Handle TradeStation OAuth callback and exchange code for tokens."""
    if error:
        raise HTTPException(400, f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(400, "missing code")
    
    redirect_uri = os.getenv("TS_REDIRECT_URI", str(request.url_for("ts_callback")))
    
    # TODO: verifică 'state' din sesiune pentru CSRF protection
    tok = await exchange_code(code, redirect_uri)

    # Exemplu: asociază tokenul la user-ul curent.
    # Dacă n-ai auth propriu, folosește un user_id dummy pentru MVP:
    user_id = "demo"
    set_token(user_id, tok)

    return JSONResponse({
        "ok": True,
        "user_id": user_id,
        "expires_at": tok.get("expires_at"),
        "message": "Authentication successful! You can close this window."
    })


@router.get("/status")
async def ts_status(user_id: str = "demo"):
    """Get current authentication status."""
    token = get_cached_token(user_id)
    if not token:
        return JSONResponse({"authenticated": False, "user_id": user_id})
    
    return JSONResponse({
        "authenticated": True,
        "user_id": user_id,
        "expires_at": token.get("expires_at"),
        "has_refresh_token": bool(token.get("refresh_token"))
    })


@router.post("/logout")
async def ts_logout(user_id: str = "demo"):
    """Logout user and clear tokens."""
    from app.services.tradestation import _TOKENS
    
    if user_id in _TOKENS:
        del _TOKENS[user_id]
        return JSONResponse({"ok": True, "message": "Logged out successfully"})
    
    return JSONResponse({"ok": True, "message": "Already logged out"})

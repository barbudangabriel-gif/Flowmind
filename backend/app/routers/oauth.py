"""
OAuth Callback Router
Handles TradeStation OAuth callbacks
"""

import logging
import os
import urllib.parse

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/oauth/tradestation", tags=["oauth"])

log = logging.getLogger("oauth.callback")


@router.get("/login")
async def tradestation_login():
    """
    Simple endpoint: GET /api/oauth/tradestation/login
    Redirects to TradeStation OAuth
    """
    client_id = os.getenv("TS_CLIENT_ID")
    redirect_uri = os.getenv("TS_REDIRECT_URI")
    
    params = {
        "response_type": "code",
        "client_id": client_id,
        "audience": "https://api.tradestation.com",
        "redirect_uri": redirect_uri,
        "scope": "openid offline_access MarketData ReadAccount Trade OptionSpreads Matrix",
        "state": "flowmind_connect"
    }
    
    auth_url = "https://signin.tradestation.com/authorize?" + urllib.parse.urlencode(params)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def tradestation_callback(code: str = None, state: str = None, error: str = None):
    """
    Handle OAuth callback from TradeStation
    """
    try:
        # Log all received parameters for debugging
        log.info(f"OAuth callback received - code: {'present' if code else 'missing'}, state: {state}, error: {error}")
        
        # Import token saving function
        from ..services.tradestation import exchange_code, set_token

        # Check for errors
        if error:
            log.error(f"OAuth error: {error}")
            return HTMLResponse(
                content=f"""
            <html>
            <head><title>Authentication Failed</title></head>
            <body style="background:#0a0e1a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
            <h1 style="color:#ef4444;"> Authentication Failed</h1>
            <p>Error: {error}</p>
            <a href="/account/balance" style="color:#3b82f6;">← Back to Account Balance</a>
            </body>
            </html>
            """,
                status_code=400,
            )

        if not code:
            raise HTTPException(400, "Authorization code missing")

        # Exchange code for token using the service
        redirect_uri = os.getenv("TS_REDIRECT_URI")

        if not redirect_uri:
            raise HTTPException(500, "OAuth redirect URI not configured")

        log.info(f"Exchanging authorization code for access token")

        try:
            # Use the exchange_code function from tradestation service
            token = await exchange_code(code, redirect_uri)

            # Save tokens
            user_id = "default"  # Default user for now
            await set_token(user_id, token)

            log.info(f" OAuth flow completed successfully for user {user_id}")
        except Exception as token_error:
            log.error(f"Token exchange failed: {str(token_error)}")
            return HTMLResponse(
                content=f"""
            <html>
            <head><title>Token Exchange Failed</title></head>
            <body style="background:#0a0e1a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
            <h1 style="color:#ef4444;"> Token Exchange Failed</h1>
            <p>Error: {str(token_error)}</p>
            <a href="/account/balance" style="color:#3b82f6;">← Back to Account Balance</a>
            </body>
            </html>
            """,
                status_code=500,
            )

        # Success page with auto-redirect
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        import_page_url = f"{frontend_url}/mindfolio/import"
        return HTMLResponse(
            content=f"""
        <html>
        <head>
        <title>Authentication Successful</title>
        <style>
        body {{
            background: #0a0e1a;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            background: #1a1f2e;
            border-radius: 12px;
            border: 1px solid #2a3f5f;
            max-width: 500px;
        }}
        .success {{ font-size: 64px; margin-bottom: 20px; }}
        h1 {{ color: #10b981; margin-bottom: 10px; }}
        p {{ color: #9ca3af; margin-bottom: 20px; }}
        .countdown {{ color: #3b82f6; font-weight: bold; }}
        .btn {{
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s;
            margin-top: 10px;
        }}
        .btn:hover {{ background: #2563eb; }}
        </style>
        <script>
        let countdown = 3;
        const countdownEl = document.getElementById('countdown');

        const interval = setInterval(() => {{
            countdown--;
            if (countdownEl) countdownEl.textContent = countdown;

            if (countdown <= 0) {{
                clearInterval(interval);
                window.location.href = '{import_page_url}';
            }}
        }}, 1000);
        </script>
        </head>
        <body>
        <div class="container">
        <div class="success">✅</div>
        <h1>Authentication Successful!</h1>
        <p>Your TradeStation account has been connected.</p>
        <p style="font-size: 14px; color: #6b7280;">
        Redirecting in <span id="countdown" class="countdown">3</span> seconds...
        </p>
        <a href="{import_page_url}" class="btn">Go to Import Page Now →</a>
        </div>
        </body>
        </html>
        """
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"OAuth callback error: {e}", exc_info=True)
        return HTMLResponse(
            content=f"""
        <html>
        <head><title>Callback Error</title></head>
        <body style="background:#0a0e1a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
        <h1 style="color:#ef4444;"> OAuth Callback Error</h1>
        <p>{str(e)}</p>
        <a href="/account/balance" style="color:#3b82f6;">← Back to Account Balance</a>
        </body>
        </html>
        """,
            status_code=500,
        )

"""
OAuth Callback Router
Handles TradeStation OAuth callbacks
"""
import logging
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import requests

router = APIRouter(prefix="/oauth/tradestation", tags=["oauth"])

log = logging.getLogger("oauth.callback")

@router.get("/callback")
async def tradestation_callback(code: str = None, state: str = None, error: str = None):
    """
    Handle OAuth callback from TradeStation
    """
    try:
        # Import token saving function
        from ..services.tradestation import save_tokens
        
        # Check for errors
        if error:
            log.error(f"OAuth error: {error}")
            return HTMLResponse(content=f"""
            <html>
            <head><title>Authentication Failed</title></head>
            <body style="background:#0a0e1a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
            <h1 style="color:#ef4444;"> Authentication Failed</h1>
            <p>Error: {error}</p>
            <a href="/account/balance" style="color:#3b82f6;">← Back to Account Balance</a>
            </body>
            </html>
            """, status_code=400)
        
        if not code:
            raise HTTPException(400, "Authorization code missing")
        
        # Exchange code for token
        client_id = os.getenv("TS_CLIENT_ID")
        client_secret = os.getenv("TS_CLIENT_SECRET")
        redirect_uri = os.getenv("TS_REDIRECT_URI")
        
        if not client_id or not client_secret:
            raise HTTPException(500, "OAuth credentials not configured")
        
        ts_mode = os.getenv("TS_MODE", "SIMULATION")
        if ts_mode == "LIVE":
            token_url = "https://signin.tradestation.com/oauth/token"
        else:
            token_url = "https://sim-signin.tradestation.com/oauth/token"
        
        # Request token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
        
        log.info(f"Exchanging authorization code for access token (mode: {ts_mode})")
        
        response = requests.post(token_url, data=token_data, timeout=10)
        
        if response.status_code != 200:
            log.error(f"Token exchange failed: {response.status_code} - {response.text}")
            return HTMLResponse(content=f"""
            <html>
            <head><title>Token Exchange Failed</title></head>
            <body style="background:#0a0e1a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
            <h1 style="color:#ef4444;"> Token Exchange Failed</h1>
            <p>Status: {response.status_code}</p>
            <pre style="color:#6b7280;font-size:12px;">{response.text[:200]}</pre>
            <a href="/account/balance" style="color:#3b82f6;">← Back to Account Balance</a>
            </body>
            </html>
            """, status_code=500)
        
        token_response = response.json()
        
        # Save tokens
        user_id = "default" # Default user for now
        
        await save_tokens(
            user_id,
            token_response["access_token"],
            token_response.get("refresh_token"),
            token_response.get("expires_in", 1200)
        )
        
        log.info(f" OAuth flow completed successfully for user {user_id}")
        
        # Success page with auto-redirect
        return HTMLResponse(content="""
        <html>
        <head>
        <title>Authentication Successful</title>
        <style>
        body {
            background: #0a0e1a;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: #1a1f2e;
            border-radius: 12px;
            border: 1px solid #2a3f5f;
            max-width: 500px;
        }
        .success { font-size: 64px; margin-bottom: 20px; }
        h1 { color: #10b981; margin-bottom: 10px; }
        p { color: #9ca3af; margin-bottom: 20px; }
        .countdown { color: #3b82f6; font-weight: bold; }
        .btn {
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s;
            margin-top: 10px;
        }
        .btn:hover { background: #2563eb; }
        </style>
        <script>
        let countdown = 3;
        const countdownEl = document.getElementById('countdown');
        
        const interval = setInterval(() => {
            countdown--;
            if (countdownEl) countdownEl.textContent = countdown;
        
            if (countdown <= 0) {
                clearInterval(interval);
                window.location.href = 'http://localhost:3000/';
            }
        }, 1000);
        </script>
        </head>
        <body>
        <div class="container">
        <div class="success"></div>
        <h1>Authentication Successful!</h1>
        <p>Your TradeStation account has been connected.</p>
        <p style="font-size: 14px; color: #6b7280;">
        Redirecting in <span id="countdown" class="countdown">3</span> seconds...
        </p>
        <a href="http://localhost:3000/" class="btn">Go to Dashboard Now →</a>
        </div>
        </body>
        </html>
        """)
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"OAuth callback error: {e}", exc_info=True)
        return HTMLResponse(content=f"""
        <html>
        <head><title>Callback Error</title></head>
        <body style="background:#0a0e1a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
        <h1 style="color:#ef4444;"> OAuth Callback Error</h1>
        <p>{str(e)}</p>
        <a href="/account/balance" style="color:#3b82f6;">← Back to Account Balance</a>
        </body>
        </html>
        """, status_code=500)

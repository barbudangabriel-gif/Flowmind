"""
TradeStation Authentication Service
Complete solution for TradeStation OAuth authentication with automatic token refresh
"""

import asyncio
import httpx
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import json
import secrets
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TradeStationAuthService:
 """Complete TradeStation authentication service with robust error handling"""
 
 def __init__(self):
 # API Configuration
 self.client_id = os.getenv("TRADESTATION_API_KEY")
 self.client_secret = os.getenv("TRADESTATION_API_SECRET")
 self.environment = os.getenv("TRADESTATION_ENVIRONMENT", "LIVE")
 self.redirect_uri = os.getenv("TRADESTATION_REDIRECT_URI", "http://localhost:8001/api/auth/tradestation/callback")
 
 # URLs
 self.auth_url = "https://signin.tradestation.com/authorize"
 self.token_url = "https://signin.tradestation.com/oauth/token"
 self.api_base = "https://api.tradestation.com/v3" if self.environment == "LIVE" else "https://sim-api.tradestation.com/v3"
 
 # Token storage
 self.token_file = Path("/app/backend/tradestation_tokens.json")
 self.access_token: Optional[str] = None
 self.refresh_token: Optional[str] = None
 self.token_expires: Optional[datetime] = None
 self.token_type: str = "Bearer"
 
 # Validation
 if not self.client_id or not self.client_secret:
 raise ValueError("TradeStation API credentials not configured in environment variables")
 
 # Load existing tokens
 self._load_tokens()
 
 logger.info(f"TradeStation Auth Service initialized - Environment: {self.environment}")
 
 def _save_tokens(self) -> None:
 """Save tokens to persistent storage with error handling"""
 try:
 token_data = {
 "access_token": self.access_token,
 "refresh_token": self.refresh_token,
 "token_expires": self.token_expires.isoformat() if self.token_expires else None,
 "token_type": self.token_type,
 "environment": self.environment,
 "saved_at": datetime.utcnow().isoformat()
 }
 
 # Create directory if it doesn't exist
 self.token_file.parent.mkdir(parents=True, exist_ok=True)
 
 # Write tokens with atomic operation
 temp_file = self.token_file.with_suffix('.tmp')
 with open(temp_file, 'w') as f:
 json.dump(token_data, f, indent=2)
 
 # Atomic rename
 temp_file.replace(self.token_file)
 
 logger.info(" TradeStation tokens saved successfully")
 except Exception as e:
 logger.error(f" Failed to save tokens: {e}")
 
 def _load_tokens(self) -> bool:
 """Load tokens from persistent storage"""
 try:
 if not self.token_file.exists():
 logger.info(" No saved TradeStation tokens found")
 return False
 
 with open(self.token_file, 'r') as f:
 token_data = json.load(f)
 
 # Validate and load tokens
 self.access_token = token_data.get("access_token")
 self.refresh_token = token_data.get("refresh_token")
 self.token_type = token_data.get("token_type", "Bearer")
 
 # Parse expiration
 if token_data.get("token_expires"):
 self.token_expires = datetime.fromisoformat(token_data["token_expires"])
 
 # Check if tokens are still valid
 if self.is_authenticated():
 logger.info(" Valid TradeStation tokens loaded from storage")
 return True
 elif self.refresh_token:
 logger.info("🔄 Tokens expired, but refresh token available")
 return True
 else:
 logger.info(" Stored tokens are expired and no refresh token available")
 self._clear_tokens()
 return False
 
 except Exception as e:
 logger.error(f" Error loading tokens: {e}")
 self._clear_tokens()
 return False
 
 def _clear_tokens(self) -> None:
 """Clear all tokens from memory and storage"""
 self.access_token = None
 self.refresh_token = None
 self.token_expires = None
 
 try:
 if self.token_file.exists():
 self.token_file.unlink()
 logger.info("🗑️ Cleared expired token file")
 except Exception as e:
 logger.error(f" Error clearing token file: {e}")
 
 def generate_auth_url(self) -> Dict[str, Any]:
 """Generate complete authentication URL and instructions"""
 state = secrets.token_urlsafe(32)
 
 params = {
 "response_type": "code",
 "client_id": self.client_id,
 "redirect_uri": self.redirect_uri,
 "audience": "https://api.tradestation.com",
 "state": state,
 "scope": "openid offline_access profile MarketData ReadAccount Trade"
 }
 
 # URL encode parameters properly
 from urllib.parse import urlencode
 query_string = urlencode(params)
 auth_url = f"{self.auth_url}?{query_string}"
 
 logger.info(f"🔗 Generated TradeStation auth URL")
 
 return {
 "status": "success",
 "auth_url": auth_url,
 "state": state,
 "instructions": [
 "1. Click the auth_url to log into TradeStation",
 "2. Accept the required permissions (MarketData, ReadAccount, Trade)",
 "3. You will be redirected back automatically",
 "4. Authentication will complete in the background"
 ],
 "permissions": [
 "MarketData - Real-time quotes and market data",
 "ReadAccount - Account information and balances", 
 "Trade - Place and manage orders"
 ]
 }
 
 async def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
 """Exchange authorization code for tokens with comprehensive error handling"""
 try:
 data = {
 "grant_type": "authorization_code",
 "client_id": self.client_id,
 "client_secret": self.client_secret,
 "code": authorization_code,
 "redirect_uri": self.redirect_uri
 }
 
 async with httpx.AsyncClient(timeout=30.0) as client:
 logger.info("🔄 Exchanging authorization code for tokens...")
 
 response = await client.post(
 self.token_url,
 data=data,
 headers={"Content-Type": "application/x-www-form-urlencoded"}
 )
 
 if response.status_code != 200:
 error_text = response.text
 logger.error(f" Token exchange failed: {response.status_code} - {error_text}")
 raise HTTPException(
 status_code=response.status_code,
 detail=f"TradeStation token exchange failed: {error_text}"
 )
 
 token_data = response.json()
 
 # Extract and store tokens
 self.access_token = token_data.get("access_token")
 self.refresh_token = token_data.get("refresh_token")
 self.token_type = token_data.get("token_type", "Bearer")
 
 # Calculate expiration
 expires_in = token_data.get("expires_in", 3600)
 self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
 
 # Save tokens
 self._save_tokens()
 
 logger.info(f" TradeStation authentication successful! Token expires in {expires_in}s")
 
 return {
 "status": "success",
 "message": "TradeStation authentication completed successfully",
 "token_info": {
 "expires_in": expires_in,
 "expires_at": self.token_expires.isoformat(),
 "scope": token_data.get("scope"),
 "token_type": self.token_type
 },
 "timestamp": datetime.now().isoformat()
 }
 
 except httpx.RequestError as e:
 logger.error(f" Network error during token exchange: {e}")
 raise HTTPException(
 status_code=500,
 detail=f"Network error connecting to TradeStation: {str(e)}"
 )
 except Exception as e:
 logger.error(f" Unexpected error during token exchange: {e}")
 raise HTTPException(
 status_code=500,
 detail=f"Unexpected error during TradeStation authentication: {str(e)}"
 )
 
 async def refresh_access_token(self) -> bool:
 """Refresh access token using refresh token"""
 if not self.refresh_token:
 logger.error(" No refresh token available for TradeStation")
 return False
 
 try:
 data = {
 "grant_type": "refresh_token",
 "refresh_token": self.refresh_token,
 "client_id": self.client_id,
 "client_secret": self.client_secret
 }
 
 async with httpx.AsyncClient(timeout=30.0) as client:
 logger.info("🔄 Refreshing TradeStation access token...")
 
 response = await client.post(
 self.token_url,
 data=data,
 headers={"Content-Type": "application/x-www-form-urlencoded"}
 )
 
 if response.status_code == 200:
 token_data = response.json()
 
 # Update tokens
 self.access_token = token_data.get("access_token")
 if "refresh_token" in token_data:
 self.refresh_token = token_data["refresh_token"]
 
 # Update expiration
 expires_in = token_data.get("expires_in", 3600)
 self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
 
 # Save updated tokens
 self._save_tokens()
 
 logger.info(f" TradeStation tokens refreshed successfully - expires in {expires_in}s")
 return True
 else:
 logger.error(f" Token refresh failed: {response.status_code} - {response.text}")
 # Clear invalid tokens
 self._clear_tokens()
 return False
 
 except Exception as e:
 logger.error(f" Error refreshing TradeStation token: {e}")
 return False
 
 async def ensure_valid_token(self) -> bool:
 """Ensure we have a valid token, auto-refresh if needed"""
 # No token at all
 if not self.access_token:
 logger.warning(" No TradeStation access token available")
 return False
 
 # Token needs refresh
 if self.needs_refresh():
 if self.refresh_token:
 logger.info("🔄 TradeStation token needs refresh, attempting automatic refresh...")
 success = await self.refresh_access_token()
 if success:
 return True
 else:
 logger.error(" Automatic token refresh failed")
 return False
 else:
 logger.error(" Token expired and no refresh token available")
 self._clear_tokens()
 return False
 
 return self.is_authenticated()
 
 def needs_refresh(self) -> bool:
 """Check if token needs refresh (5 minutes buffer)"""
 if not self.token_expires:
 return False
 
 buffer_time = timedelta(minutes=5)
 return datetime.utcnow() >= (self.token_expires - buffer_time)
 
 def is_authenticated(self) -> bool:
 """Check if currently authenticated with valid token"""
 if not self.access_token:
 return False
 
 if self.token_expires and datetime.utcnow() >= self.token_expires:
 return False
 
 return True
 
 async def get_auth_headers(self) -> Dict[str, str]:
 """Get authorization headers with auto-refresh"""
 if not await self.ensure_valid_token():
 raise HTTPException(
 status_code=401,
 detail="TradeStation authentication required. Please authenticate first."
 )
 
 return {
 "Authorization": f"{self.token_type} {self.access_token}",
 "Content-Type": "application/json"
 }
 
 def get_status(self) -> Dict[str, Any]:
 """Get comprehensive authentication status"""
 return {
 "authenticated": self.is_authenticated(),
 "has_access_token": bool(self.access_token),
 "has_refresh_token": bool(self.refresh_token),
 "token_expires": self.token_expires.isoformat() if self.token_expires else None,
 "needs_refresh": self.needs_refresh() if self.token_expires else False,
 "environment": self.environment,
 "api_base": self.api_base,
 "redirect_uri": self.redirect_uri
 }

# Global service instance
tradestation_auth_service = TradeStationAuthService()
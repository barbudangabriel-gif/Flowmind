"""
TradeStation OAuth 2.0 Authentication Handler
Handles OAuth flows, token management, and authentication for TradeStation API
"""

import asyncio
import httpx
import secrets
import os
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TradeStationAuth:
    """Handles TradeStation API authentication using OAuth 2.0"""
    
    def __init__(self):
        self.client_id = os.getenv("TRADESTATION_API_KEY")
        self.client_secret = os.getenv("TRADESTATION_API_SECRET")
        self.environment = os.getenv("TRADESTATION_ENVIRONMENT", "LIVE")
        
        # OAuth URLs
        self.auth_url = "https://signin.tradestation.com/authorize"
        self.token_url = "https://signin.tradestation.com/oauth/token"
        
        # API Base URLs
        self.api_base = "https://api.tradestation.com/v3" if self.environment == "LIVE" else "https://sim-api.tradestation.com/v3"
        
        # Token persistence
        self.token_file = Path("/app/backend/tradestation_tokens.json")
        
        # Token storage
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.token_type: str = "Bearer"
        
        # Auto-refresh settings
        self.auto_refresh_enabled = True
        self.refresh_buffer_minutes = 5  # Refresh 5 minutes before expiry
        
        # Load existing tokens on initialization
        self._load_tokens()
        
        # Default redirect URI
        self.redirect_uri = os.getenv("TRADESTATION_REDIRECT_URI", "http://localhost:8001/api/auth/tradestation/callback")
        
        logger.info(f"TradeStation Auth initialized for {self.environment} environment")
    
    def _save_tokens(self) -> None:
        """Save current tokens to persistent storage"""
        try:
            token_data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "token_expires": self.token_expires.isoformat() if self.token_expires else None,
                "token_type": self.token_type,
                "environment": self.environment,
                "saved_at": datetime.utcnow().isoformat()
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            logger.info("TradeStation tokens saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
    
    def _load_tokens(self) -> bool:
        """Load tokens from persistent storage"""
        try:
            if not self.token_file.exists():
                logger.info("No saved tokens found")
                return False
            
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # Validate token data
            if not token_data.get("access_token"):
                logger.info("No access token in saved data")
                return False
            
            # Check if tokens are expired
            if token_data.get("token_expires"):
                expires_at = datetime.fromisoformat(token_data["token_expires"])
                if expires_at <= datetime.utcnow():
                    logger.info("Saved tokens are expired")
                    return False
            
            # Load token data
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            self.token_expires = datetime.fromisoformat(token_data["token_expires"]) if token_data.get("token_expires") else None
            self.token_type = token_data.get("token_type", "Bearer")
            
            logger.info(f"TradeStation tokens loaded successfully. Expires: {self.token_expires}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load tokens: {e}")
            return False
    
    def _clear_tokens(self) -> None:
        """Clear tokens from memory and storage"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        
        try:
            if self.token_file.exists():
                self.token_file.unlink()
                logger.info("Token file deleted")
        except Exception as e:
            logger.error(f"Failed to delete token file: {e}")
    
    async def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                response = await client.post(self.token_url, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    
                    # Update tokens
                    self.access_token = token_data["access_token"]
                    if "refresh_token" in token_data:
                        self.refresh_token = token_data["refresh_token"]
                    
                    # Calculate expiry
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    # Save tokens
                    self._save_tokens()
                    
                    logger.info(f"Tokens refreshed successfully. New expiry: {self.token_expires}")
                    return True
                else:
                    logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    def needs_refresh(self) -> bool:
        """Check if token needs to be refreshed"""
        if not self.token_expires:
            return False
        
        buffer_time = timedelta(minutes=self.refresh_buffer_minutes)
        return datetime.utcnow() >= (self.token_expires - buffer_time)
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid token"""
        if not self.access_token:
            return False
        
        if self.token_expires and datetime.utcnow() >= self.token_expires:
            return False
        
        return True
    
    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid token, refresh if needed"""
        if not self.access_token:
            return False
        
        if self.needs_refresh() and self.refresh_token:
            logger.info("Token needs refresh, attempting automatic refresh...")
            return await self.refresh_access_token()
        
        return self.is_authenticated()
    
    def generate_auth_url(self, state: Optional[str] = None) -> str:
        """Generate TradeStation authorization URL with proper parameters"""
        if not state:
            state = secrets.token_urlsafe(32)
            
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "audience": "https://api.tradestation.com",
            "state": state,
            "scope": "openid offline_access profile MarketData ReadAccount Trade"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.auth_url}?{query_string}"
        
        logger.info(f"Generated auth URL for state: {state[:8]}...")
        return auth_url
    
    async def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=500, 
                detail="TradeStation API credentials not configured"
            )
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"content-type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Token exchange failed: {response.text}"
                    )
                    
                token_data = response.json()
                
                # Store tokens
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                
                # Calculate token expiration
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
                
                # Save tokens to persistent storage
                self._save_tokens()
                
                logger.info(f"Successfully exchanged authorization code for tokens. Expires in {expires_in}s")
                
                return {
                    "access_token": self.access_token,
                    "token_type": token_data.get("token_type"),
                    "expires_in": expires_in,
                    "scope": token_data.get("scope"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except httpx.RequestError as e:
                logger.error(f"Network error during token exchange: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Network error during authentication: {str(e)}"
                )
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests with auto-refresh"""
        # Ensure token is valid (auto-refresh if needed)
        if not await self.ensure_valid_token():
            raise HTTPException(
                status_code=401, 
                detail="No access token available. Please authenticate first."
            )
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return (
            self.access_token is not None and 
            self.token_expires is not None and 
            datetime.now() < self.token_expires
        )
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get current authentication status"""
        if not self.access_token:
            return {
                "authenticated": False,
                "status": "Not authenticated",
                "environment": self.environment
            }
        
        if self.token_expires:
            time_until_expiry = self.token_expires - datetime.now()
            minutes_until_expiry = int(time_until_expiry.total_seconds() / 60)
            
            if minutes_until_expiry <= 0:
                return {
                    "authenticated": False,
                    "status": "Token expired",
                    "environment": self.environment
                }
            
            return {
                "authenticated": True,
                "status": "Authenticated",
                "environment": self.environment,
                "expires_in_minutes": minutes_until_expiry,
                "expires_at": self.token_expires.isoformat()
            }
        
        return {
            "authenticated": True,
            "status": "Authenticated",
            "environment": self.environment,
            "expires_at": "Unknown"
        }

# Global authentication instance
ts_auth = TradeStationAuth()
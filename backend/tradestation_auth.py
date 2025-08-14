"""
TradeStation OAuth 2.0 Authentication Handler
Handles OAuth flows, token management, and authentication for TradeStation API
"""

import asyncio
import httpx
import secrets
import os
import logging
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
        
        # Token storage
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        
        # Default redirect URI
        self.redirect_uri = os.getenv("TRADESTATION_REDIRECT_URI", "http://localhost:8001/api/auth/tradestation/callback")
        
        logger.info(f"TradeStation Auth initialized for {self.environment} environment")
    
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
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                
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
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise HTTPException(
                status_code=401, 
                detail="No refresh token available. Please re-authenticate."
            )
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"content-type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                    # Clear tokens on refresh failure
                    self.access_token = None
                    self.refresh_token = None
                    self.token_expires = None
                    
                    raise HTTPException(
                        status_code=401,
                        detail="Token refresh failed. Please re-authenticate."
                    )
                    
                token_data = response.json()
                
                # Update tokens
                self.access_token = token_data.get("access_token")
                
                # Update expiration time
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(f"Successfully refreshed access token. Expires in {expires_in}s")
                
                return {
                    "access_token": self.access_token,
                    "token_type": token_data.get("token_type"),
                    "expires_in": expires_in,
                    "timestamp": datetime.now().isoformat()
                }
                
            except httpx.RequestError as e:
                logger.error(f"Network error during token refresh: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Network error during token refresh: {str(e)}"
                )
    
    async def ensure_valid_token(self) -> None:
        """Ensure access token is valid, refresh if necessary"""
        if not self.access_token:
            raise HTTPException(
                status_code=401, 
                detail="No access token available. Please authenticate first."
            )
        
        # Check if token is expired or will expire in next 5 minutes
        if self.token_expires and datetime.now() >= (self.token_expires - timedelta(minutes=5)):
            logger.info("Access token expiring soon, refreshing...")
            await self.refresh_access_token()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        if not self.access_token:
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
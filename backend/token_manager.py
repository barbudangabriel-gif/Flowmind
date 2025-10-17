"""
TradeStation Token Manager
Handles automatic token refresh and background monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class TokenManager:
 """Manages automatic token refresh for TradeStation authentication"""
 
 def __init__(self, auth_instance):
 self.auth = auth_instance
 self.refresh_task: Optional[asyncio.Task] = None
 self.running = False
 self.check_interval = 300 # Check every 5 minutes
 
 async def start_monitoring(self):
 """Start the background token monitoring task"""
 if self.running:
 logger.info("Token monitoring already running")
 return
 
 self.running = True
 self.refresh_task = asyncio.create_task(self._monitor_tokens())
 logger.info("Started TradeStation token monitoring")
 
 async def stop_monitoring(self):
 """Stop the background token monitoring task"""
 self.running = False
 
 if self.refresh_task and not self.refresh_task.done():
 self.refresh_task.cancel()
 try:
 await self.refresh_task
 except asyncio.CancelledError:
 logger.info("Token monitoring task cancelled")
 
 logger.info("Stopped TradeStation token monitoring")
 
 async def _monitor_tokens(self):
 """Background task to monitor and refresh tokens"""
 logger.info("Token monitoring task started")
 
 while self.running:
 try:
 # Check if we need to refresh tokens
 if self.auth.is_authenticated() and self.auth.needs_refresh():
 logger.info("Tokens need refresh, attempting automatic refresh...")
 
 success = await self.auth.refresh_access_token()
 if success:
 logger.info(" Tokens refreshed successfully in background")
 else:
 logger.error(" Background token refresh failed")
 
 # Check if tokens are expired
 elif self.auth.access_token and not self.auth.is_authenticated():
 logger.warning("Tokens have expired. Manual re-authentication required.")
 
 # Sleep until next check
 await asyncio.sleep(self.check_interval)
 
 except asyncio.CancelledError:
 logger.info("Token monitoring task cancelled")
 break
 except Exception as e:
 logger.error(f"Error in token monitoring task: {e}")
 # Continue monitoring even if there's an error
 await asyncio.sleep(self.check_interval)
 
 logger.info("Token monitoring task finished")
 
 def get_status(self) -> dict:
 """Get current monitoring status"""
 return {
 "monitoring": self.running,
 "task_status": "running" if self.refresh_task and not self.refresh_task.done() else "stopped",
 "check_interval_seconds": self.check_interval,
 "auth_status": {
 "authenticated": self.auth.is_authenticated(),
 "needs_refresh": self.auth.needs_refresh() if self.auth.is_authenticated() else False,
 "token_expires": self.auth.token_expires.isoformat() if self.auth.token_expires else None,
 "expires_in_minutes": (
 int((self.auth.token_expires - datetime.utcnow()).total_seconds() / 60)
 if self.auth.token_expires and self.auth.token_expires > datetime.utcnow()
 else 0
 )
 }
 }

# Global token manager instance
token_manager = None

def get_token_manager(auth_instance=None):
 """Get or create the global token manager instance"""
 global token_manager
 
 if token_manager is None and auth_instance:
 token_manager = TokenManager(auth_instance)
 
 return token_manager
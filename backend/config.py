import os
from typing import Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class Settings(BaseModel):
 """Application settings with secure defaults and validation"""

 # App configuration
 app_mode: str = Field("dev", alias="APP_MODE")
 allowed_origins: list[str] = Field(
 default_factory=lambda: ["*"], alias="ALLOWED_ORIGINS"
 )
 rate_limit: str = Field("60/minute", alias="RATE_LIMIT")

 # API Keys (fail-fast if critical ones missing in production)
 uw_token: Optional[str] = Field(None, alias="UW_API_TOKEN")
 ts_token: Optional[str] = Field(None, alias="TS_TOKEN")
 ts_api_key: Optional[str] = Field(None, alias="TRADESTATION_API_KEY")
 ts_api_secret: Optional[str] = Field(None, alias="TRADESTATION_API_SECRET")
 ts_client_secret: Optional[str] = Field(None, alias="TS_CLIENT_SECRET")

 # Database & Infrastructure
 mongo_url: str = Field("mongodb://localhost:27017/flowmind", alias="MONGO_URL")

 # TradeStation Config
 ts_base_url: str = Field("https://api.tradestation.com/v3", alias="TS_BASE_URL")
 ts_token_url: str = Field(
 "https://signin.tradestation.com/oauth/token", alias="TS_TOKEN_URL"
 )
 ts_redirect_uri: str = Field("http://localhost:8080", alias="TS_REDIRECT_URI")
 ts_token_margin_sec: int = Field(120, alias="TS_TOKEN_MARGIN_SEC")

def get_settings() -> Settings:
 """Get validated settings with proper error handling"""
 try:
    # Parse allowed origins from comma-separated string
    origins_str = os.environ.get("ALLOWED_ORIGINS", "*")
    if origins_str == "*":
        origins = ["*"]
    else:
        origins = [origin.strip() for origin in origins_str.split(",")]

    # Override environment for processing
    env_override = dict(os.environ)
    if "ALLOWED_ORIGINS" in env_override:
        env_override["ALLOWED_ORIGINS"] = origins

    settings = Settings(**env_override)

    # Warn about missing optional secrets in development
    if settings.app_mode == "dev":
        missing_secrets = []
        if not settings.uw_token:
            missing_secrets.append("UW_API_TOKEN")
        if not settings.ts_api_key:
            missing_secrets.append("TRADESTATION_API_KEY")

        if missing_secrets:
            logger.warning(
                f"Missing optional secrets (demo mode): {', '.join(missing_secrets)}"
            )

    # Fail-fast in production if critical secrets missing
    elif settings.app_mode == "prod":
        required_secrets = []
        if not settings.uw_token:
            required_secrets.append("UW_API_TOKEN")
        if not settings.ts_api_key:
            required_secrets.append("TRADESTATION_API_KEY")
        if not settings.ts_api_secret:
            required_secrets.append("TRADESTATION_API_SECRET")

        if required_secrets:
            raise RuntimeError(
                f"Missing required secrets in production: {', '.join(required_secrets)}"
            )

    return settings

 except Exception as e:
    raise RuntimeError(f"Configuration error: {e}")

# Global settings instance
settings = get_settings()

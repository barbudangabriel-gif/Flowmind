import re
from typing import Any, Dict

# Patterns pentru secret masking
SECRET_PATTERNS = [
    (r'("?(?:client_)?secret"?\s*[:=]\s*"?)([^"\s,}]+)', r"\1***MASKED***"),
    (r'("?(?:api_)?key"?\s*[:=]\s*"?)([^"\s,}]+)', r"\1***MASKED***"),
    (r'("?access_token"?\s*[:=]\s*"?)([^"\s,}]+)', r"\1***MASKED***"),
    (r'("?refresh_token"?\s*[:=]\s*"?)([^"\s,}]+)', r"\1***MASKED***"),
    (r'("?password"?\s*[:=]\s*"?)([^"\s,}]+)', r"\1***MASKED***"),
    (r"(Bearer\s+)([A-Za-z0-9_\-\.]+)", r"\1***MASKED***"),
]


def mask_secrets(text: str) -> str:
    """Mask sensitive information in logs"""
    if not isinstance(text, str):
        text = str(text)

    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def safe_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Return dict with masked sensitive keys"""
    if not isinstance(d, dict):
        return d

    safe = d.copy()
    sensitive_keys = {
        "secret",
        "client_secret",
        "api_secret",
        "password",
        "key",
        "api_key",
        "client_key",
        "access_token",
        "refresh_token",
    }

    for key in safe:
        if any(sens in key.lower() for sens in sensitive_keys):
            safe[key] = "***MASKED***"

    return safe

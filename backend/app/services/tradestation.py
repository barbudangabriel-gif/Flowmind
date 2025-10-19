# app/services/tradestation.py
from __future__ import annotations

import os
import time
import logging
import asyncio
from typing import Dict, Optional, Tuple

import httpx

log = logging.getLogger("tradestation")
if not log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    log.addHandler(handler)
    log.setLevel(logging.INFO)

# === Config din ENV (setează-le în .env) ===
TS_BASE_URL = os.getenv("TS_BASE_URL", "https://api.tradestation.com")
TS_TOKEN_URL = os.getenv("TS_TOKEN_URL", f"{TS_BASE_URL.rstrip('/')}/oauth/token")
TS_AUTH_URL = os.getenv("TS_AUTH_URL", f"{TS_BASE_URL.rstrip('/')}/authorize")
TS_CLIENT_ID = os.getenv("TS_CLIENT_ID", "")
TS_CLIENT_SECRET = os.getenv("TS_CLIENT_SECRET", "")
TS_SCOPE = os.getenv("TS_SCOPE", "openid offline_access")

HTTP_TIMEOUT = float(os.getenv("TS_HTTP_TIMEOUT", "15"))
REFRESH_SKEW = int(os.getenv("TS_REFRESH_SKEW", "60"))  # secunde

# === Mem-cache simplu per user_id ===
_TOKENS: Dict[str, Dict] = (
    {}
)  # user_id -> token dict {access_token, refresh_token, expires_at}
_LOCKS: Dict[str, asyncio.Lock] = {}  # user_id -> lock pt. refresh/obținere


def _now() -> int:
    return int(time.time())


def _ensure_lock(user_id: str) -> asyncio.Lock:
    if user_id not in _LOCKS:
        _LOCKS[user_id] = asyncio.Lock()
    return _LOCKS[user_id]


def auth_url(redirect_uri: str, state: str) -> str:
    """Construiește URL-ul de login (implicit response_type=code)."""
    from urllib.parse import urlencode

    params = {
        "response_type": "code",
        "client_id": TS_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": TS_SCOPE,
        "state": state,
    }
    return f"{TS_AUTH_URL}?{urlencode(params)}"


async def _http_client() -> httpx.AsyncClient:
    # Reutilizabil; îl închizi în apelant dacă îl creezi manual. Aici lăsăm simplu per-call.
    return httpx.AsyncClient(timeout=httpx.Timeout(HTTP_TIMEOUT))


def _calc_expires_at(expires_in: int) -> int:
    return _now() + max(0, int(expires_in)) - REFRESH_SKEW


def _normalize_token(payload: Dict) -> Dict:
    return {
        "access_token": payload.get("access_token", ""),
        "refresh_token": payload.get("refresh_token", ""),
        "token_type": payload.get("token_type", "Bearer"),
        "scope": payload.get("scope", TS_SCOPE),
        "expires_at": _calc_expires_at(int(payload.get("expires_in", 0))),
        # optional: id_token dacă e returnat
        "id_token": payload.get("id_token"),
        "raw": payload,
    }


async def exchange_code(code: str, redirect_uri: str) -> Dict:
    """Schimbă authorization code pentru tokens."""
    async with await _http_client() as client:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": TS_CLIENT_ID,
            "client_secret": TS_CLIENT_SECRET,
        }
        r = await client.post(TS_TOKEN_URL, data=data)
        if r.status_code != 200:
            log.error("TS exchange_code failed [%s]: %s", r.status_code, r.text[:500])
            raise httpx.HTTPStatusError(
                "exchange_code failed", request=r.request, response=r
            )
        payload = r.json()
        tok = _normalize_token(payload)
        log.info("TS exchange_code ok; expires_at=%s", tok["expires_at"])
        return tok


async def refresh_tokens(refresh_token: str) -> Dict:
    """Refreshează access token folosind refresh_token."""
    async with await _http_client() as client:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": TS_CLIENT_ID,
            "client_secret": TS_CLIENT_SECRET,
        }
        r = await client.post(TS_TOKEN_URL, data=data)
        if r.status_code != 200:
            log.warning("TS refresh failed [%s]: %s", r.status_code, r.text[:500])
            raise httpx.HTTPStatusError("refresh failed", request=r.request, response=r)
        payload = r.json()
        tok = _normalize_token(payload)
        log.info("TS refresh ok; expires_at=%s", tok["expires_at"])
        return tok


def set_token(user_id: str, token: Dict) -> None:
    _TOKENS[user_id] = token


def get_cached_token(user_id: str) -> Optional[Dict]:
    tok = _TOKENS.get(user_id)
    if not tok:
        return None
    if tok.get("expires_at", 0) <= _now():
        return None
    return tok


async def get_valid_token(user_id: str) -> Optional[Dict]:
    """
    Dă-ți un access_token valid din cache; dacă e expirat încearcă refresh în mod sigur (cu lock).
    Returnează dict token sau None dacă nu avem nimic.
    """
    tok = get_cached_token(user_id)
    if tok:
        return tok

    # dacă nu avem nimic, încearcă refresh dacă avem măcar refresh_token
    lock = _ensure_lock(user_id)
    async with lock:
        # alt task poate să fi făcut deja refresh
        tok = get_cached_token(user_id)
        if tok:
            return tok

        current = _TOKENS.get(user_id)
        if not current or not current.get("refresh_token"):
            return None

        try:
            new_tok = await refresh_tokens(current["refresh_token"])
            set_token(user_id, new_tok)
            return new_tok
        except Exception as e:
            log.exception("refresh error: %s", e)
            return None


def bearer(auth: Dict) -> str:
    """Header Authorization: Bearer ..."""
    return f'{auth.get("token_type","Bearer")} {auth.get("access_token","")}'


async def call_ts_api(
    user_id: str,
    method: str,
    path: str,
    *,
    params: Dict | None = None,
    json: Dict | None = None,
) -> httpx.Response:
    """
    Utilitar mic pentru a apela API-ul TradeStation cu token valid (face refresh dacă e cazul).
    Aruncă httpx.HTTPStatusError la 401/403/5xx.
    """
    token = await get_valid_token(user_id)
    if not token:
        raise PermissionError("no valid token for user")

    headers = {"Authorization": bearer(token)}
    url = f"{TS_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with await _http_client() as client:
        r = await client.request(
            method.upper(), url, params=params, json=json, headers=headers
        )
        if r.status_code == 401:
            # o singură încercare de refresh apoi retry
            if token.get("refresh_token"):
                try:
                    new_tok = await refresh_tokens(token["refresh_token"])
                    set_token(user_id, new_tok)
                    headers["Authorization"] = bearer(new_tok)
                    r = await client.request(
                        method.upper(), url, params=params, json=json, headers=headers
                    )
                except Exception:
                    pass
        if r.is_error:
            log.error(
                "TS API %s %s failed [%s]: %s",
                method,
                path,
                r.status_code,
                r.text[:500],
            )
            r.raise_for_status()
        return r

"""TradeStation API endpoints for accounts, balances, positions."""

import logging
import os
import requests
from fastapi import APIRouter, HTTPException, Depends

from ..deps.tradestation import get_bearer_token, get_user_id

log = logging.getLogger("ts.api")
router = APIRouter(tags=["TradeStation API"])

TS_MODE = os.getenv("TRADESTATION_MODE", "SIMULATION")
if TS_MODE == "LIVE":
    TS_API_BASE = "https://api.tradestation.com/v3"
else:
    TS_API_BASE = "https://sim-api.tradestation.com/v3"

log.info(f"TradeStation API: {TS_MODE} mode at {TS_API_BASE}")


@router.get("/tradestation/accounts")
async def get_accounts(token: str = Depends(get_bearer_token), user_id: str = Depends(get_user_id)):
    """Get list of TradeStation accounts."""
    try:
        url = f"{TS_API_BASE}/brokerage/accounts"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        log.info(f"Fetching accounts for user {user_id}")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log.info(f"Retrieved {len(data.get('Accounts', []))} accounts")
            return {"status": "success", "data": data}
        else:
            log.error(f"API error: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=response.text[:200])

    except requests.RequestException as e:
        log.error(f"Network error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tradestation/accounts/{account_id}/balances")
async def get_account_balances(
    account_id: str, token: str = Depends(get_bearer_token), user_id: str = Depends(get_user_id)
):
    """Get account balances."""
    try:
        url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/balances"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        log.info(f"Fetching balances for account {account_id}")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log.info(f"Retrieved balances for {account_id}")
            return {"status": "success", "data": data}
        else:
            log.error(f"API error: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=response.text[:200])

    except requests.RequestException as e:
        log.error(f"Network error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tradestation/accounts/{account_id}/positions")
async def get_account_positions(
    account_id: str, token: str = Depends(get_bearer_token), user_id: str = Depends(get_user_id)
):
    """Get account positions."""
    try:
        url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/positions"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        log.info(f"Fetching positions for account {account_id}")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log.info(f"Retrieved positions for {account_id}")
            return {"status": "success", "data": data}
        else:
            log.error(f"API error: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=response.text[:200])

    except requests.RequestException as e:
        log.error(f"Network error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

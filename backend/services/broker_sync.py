"""
Broker Sync Service for Master Mindfolios (NEW - Nov 2, 2025)

Auto-sync master mindfolios with broker APIs:
- Periodic sync (every 5 minutes) or manual trigger
- Fetch positions + balances from broker
- Compare with current mindfolio state
- Create transactions for differences
- Recalculate positions
"""

import logging
import os
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from redis_fallback import get_kv

logger = logging.getLogger(__name__)

# TradeStation API base URL
TS_MODE = os.getenv("TRADESTATION_MODE", "SIMULATION")
if TS_MODE == "LIVE":
    TS_API_BASE = "https://api.tradestation.com/v3"
else:
    TS_API_BASE = "https://sim-api.tradestation.com/v3"


class BrokerSyncService:
    """
    Auto-sync master mindfolios with broker APIs.
    """

    def __init__(self):
        pass

    async def sync_master_mindfolio(
        self, master_id: str, token: str
    ) -> Dict[str, Any]:
        """
        Sync a single master mindfolio with its broker.

        Args:
            master_id: Master mindfolio ID
            token: Broker API access token

        Returns:
            Sync result with status and statistics
        """
        from mindfolio import (
            pf_get,
            pf_put,
            get_mindfolio_positions,
            calculate_positions_fifo,
            key_transaction,
            key_mindfolio_transactions,
            key_mindfolio_positions,
            Transaction,
        )
        import json
        import secrets

        try:
            # Get master mindfolio
            master = await pf_get(master_id)
            if not master or not master.is_master:
                raise ValueError(f"Not a master mindfolio: {master_id}")

            # Update sync status
            master.sync_status = "syncing"
            await pf_put(master)

            # Fetch live data from broker
            live_positions = await self._fetch_broker_positions(
                master.broker, master.account_id, token
            )
            live_cash = await self._fetch_broker_balance(
                master.broker, master.account_id, token
            )

            # Get current mindfolio positions
            current_positions = await get_mindfolio_positions(master_id)

            # Calculate differences
            position_diffs = self._calculate_position_diffs(
                current_positions, live_positions
            )

            # Create transactions for differences
            cli = await get_kv()
            transactions_created = []

            for diff in position_diffs:
                now = datetime.now(timezone.utc).isoformat()

                if diff["type"] == "new_buy":
                    # New position appeared in broker
                    tx = Transaction(
                        id=f"tx_{secrets.token_hex(6)}",
                        mindfolio_id=master_id,
                        account_id=master.account_id,
                        datetime=now,
                        symbol=diff["symbol"],
                        side="BUY",
                        qty=diff["quantity"],
                        price=diff["avg_price"],
                        fee=0.0,
                        notes="Auto-sync from broker",
                        created_at=now,
                    )
                    await cli.set(key_transaction(tx.id), tx.json())

                    # Update transaction list
                    tx_list_raw = (
                        await cli.get(key_mindfolio_transactions(master_id)) or "[]"
                    )
                    tx_ids = json.loads(tx_list_raw)
                    tx_ids.append(tx.id)
                    await cli.set(
                        key_mindfolio_transactions(master_id), json.dumps(tx_ids)
                    )

                    transactions_created.append(
                        {
                            "symbol": diff["symbol"],
                            "side": "BUY",
                            "qty": diff["quantity"],
                        }
                    )

                elif diff["type"] == "partial_sell":
                    # Position reduced in broker
                    tx = Transaction(
                        id=f"tx_{secrets.token_hex(6)}",
                        mindfolio_id=master_id,
                        account_id=master.account_id,
                        datetime=now,
                        symbol=diff["symbol"],
                        side="SELL",
                        qty=diff["quantity"],
                        price=diff["avg_price"],
                        fee=0.0,
                        notes="Auto-sync from broker",
                        created_at=now,
                    )
                    await cli.set(key_transaction(tx.id), tx.json())

                    # Update transaction list
                    tx_list_raw = (
                        await cli.get(key_mindfolio_transactions(master_id)) or "[]"
                    )
                    tx_ids = json.loads(tx_list_raw)
                    tx_ids.append(tx.id)
                    await cli.set(
                        key_mindfolio_transactions(master_id), json.dumps(tx_ids)
                    )

                    transactions_created.append(
                        {
                            "symbol": diff["symbol"],
                            "side": "SELL",
                            "qty": diff["quantity"],
                        }
                    )

                elif diff["type"] == "full_sell":
                    # Position closed in broker
                    tx = Transaction(
                        id=f"tx_{secrets.token_hex(6)}",
                        mindfolio_id=master_id,
                        account_id=master.account_id,
                        datetime=now,
                        symbol=diff["symbol"],
                        side="SELL",
                        qty=diff["quantity"],
                        price=diff["avg_price"],
                        fee=0.0,
                        notes="Auto-sync from broker (position closed)",
                        created_at=now,
                    )
                    await cli.set(key_transaction(tx.id), tx.json())

                    # Update transaction list
                    tx_list_raw = (
                        await cli.get(key_mindfolio_transactions(master_id)) or "[]"
                    )
                    tx_ids = json.loads(tx_list_raw)
                    tx_ids.append(tx.id)
                    await cli.set(
                        key_mindfolio_transactions(master_id), json.dumps(tx_ids)
                    )

                    transactions_created.append(
                        {
                            "symbol": diff["symbol"],
                            "side": "SELL",
                            "qty": diff["quantity"],
                        }
                    )

            # Update cash balance
            master.cash_balance = live_cash

            # Recalculate positions
            calculated_positions = await calculate_positions_fifo(master_id)

            # Save positions
            positions_json = json.dumps([pos.dict() for pos in calculated_positions])
            await cli.set(key_mindfolio_positions(master_id), positions_json)

            # Update sync status
            master.last_sync = datetime.now(timezone.utc).isoformat()
            master.sync_status = "idle"
            await pf_put(master)

            logger.info(
                f"Synced master mindfolio {master_id}: {len(transactions_created)} transactions created"
            )

            return {
                "status": "success",
                "synced_at": master.last_sync,
                "transactions_created": len(transactions_created),
                "positions_updated": len(calculated_positions),
                "cash_balance": live_cash,
            }

        except Exception as e:
            logger.error(f"Sync failed for {master_id}: {e}")
            # Update sync status to error
            try:
                master.sync_status = "error"
                await pf_put(master)
            except:
                pass
            raise e

    async def _fetch_broker_positions(
        self, broker: str, account_id: str, token: str
    ) -> List[Dict[str, Any]]:
        """Fetch positions from broker API"""
        if broker == "TradeStation":
            url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/positions"
            resp = requests.get(
                url, headers={"Authorization": f"Bearer {token}"}, timeout=15
            )
            resp.raise_for_status()
            return resp.json().get("Positions", [])
        elif broker == "Tastytrade":
            # TODO: Implement Tastytrade API
            raise NotImplementedError("Tastytrade integration not yet implemented")
        elif broker == "IBKR":
            # TODO: Implement IBKR API
            raise NotImplementedError("IBKR integration not yet implemented")
        else:
            raise ValueError(f"Unknown broker: {broker}")

    async def _fetch_broker_balance(
        self, broker: str, account_id: str, token: str
    ) -> float:
        """Fetch cash balance from broker API"""
        if broker == "TradeStation":
            url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/balances"
            resp = requests.get(
                url, headers={"Authorization": f"Bearer {token}"}, timeout=15
            )
            resp.raise_for_status()
            balances = resp.json().get("Balances", [])
            if not balances:
                return 0.0
            return float(balances[0].get("CashBalance", 0))
        elif broker == "Tastytrade":
            # TODO: Implement Tastytrade API
            raise NotImplementedError("Tastytrade integration not yet implemented")
        elif broker == "IBKR":
            # TODO: Implement IBKR API
            raise NotImplementedError("IBKR integration not yet implemented")
        else:
            raise ValueError(f"Unknown broker: {broker}")

    def _calculate_position_diffs(
        self, current: List[Any], live: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate differences between current and live positions.

        Returns list of diffs:
        - new_buy: New position appeared in broker
        - partial_sell: Position reduced in broker
        - full_sell: Position closed in broker
        """
        diffs = []
        current_symbols = {p.symbol: p for p in current}
        live_symbols = {p["Symbol"]: p for p in live}

        # New positions
        for symbol in live_symbols:
            if symbol not in current_symbols:
                diffs.append(
                    {
                        "type": "new_buy",
                        "symbol": symbol,
                        "quantity": float(live_symbols[symbol]["Quantity"]),
                        "avg_price": float(live_symbols[symbol]["AveragePrice"]),
                    }
                )

        # Reduced or closed positions
        for symbol in current_symbols:
            if symbol in live_symbols:
                current_qty = current_symbols[symbol].qty
                live_qty = float(live_symbols[symbol]["Quantity"])
                if live_qty < current_qty:
                    # Position reduced
                    diffs.append(
                        {
                            "type": "partial_sell",
                            "symbol": symbol,
                            "quantity": current_qty - live_qty,
                            "avg_price": float(live_symbols[symbol]["AveragePrice"]),
                        }
                    )
            else:
                # Position closed
                diffs.append(
                    {
                        "type": "full_sell",
                        "symbol": symbol,
                        "quantity": current_symbols[symbol].qty,
                        "avg_price": current_symbols[symbol].avg_cost,
                    }
                )

        return diffs

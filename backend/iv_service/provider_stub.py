import random
from .provider_base import IVProvider, tick_step, round_to_tick


class StubProvider(IVProvider):
    async def get_spot(self, symbol: str) -> float:
        base = 180.0 if symbol.upper() == "NVDA" else 100.0
        return round(base + random.uniform(-2, 2), 2)

    async def get_atm_iv(self, symbol: str, dte: int) -> float:
        iv = 0.25 + random.uniform(-0.01, 0.01)
        return max(0.05, min(iv, 1.0))

    async def list_terms(self, symbol: str):
        out = []
        dte = 3
        for i in range(10):
            out.append({"date": f"2025-12-{10+i:02d}", "dte": dte})
            dte += 7
        return out

    async def list_strikes(self, symbol: str, dte: int):
        spot = await self.get_spot(symbol)
        step = tick_step(spot)
        base = round_to_tick(spot, spot)
        return [int(base - 10 * step + i * step) for i in range(21)]

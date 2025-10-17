import aiohttp
from .provider_base import IVProvider
from .config import TS_BASE_URL, TS_TOKEN

HEADERS = {"Authorization": f"Bearer {TS_TOKEN}"} if TS_TOKEN else {}

class TradeStationProvider(IVProvider):
 async def get_spot(self, symbol: str) -> float:
 if not TS_BASE_URL:
 raise RuntimeError("TS_BASE_URL missing")
 url = f"{TS_BASE_URL}/quotes/spot?symbol={symbol}"
 async with aiohttp.ClientSession(headers=HEADERS) as s:
 async with s.get(url, timeout=10) as r:
 r.raise_for_status()
 data = await r.json()
 return float(data["last"]) # adaptează la schema reală

 async def get_atm_iv(self, symbol: str, dte: int) -> float:
 url = f"{TS_BASE_URL}/options/atm_iv?symbol={symbol}&dte={dte}"
 async with aiohttp.ClientSession(headers=HEADERS) as s:
 async with s.get(url, timeout=10) as r:
 r.raise_for_status()
 data = await r.json()
 return float(data["iv"]) # adaptează la schema reală

 async def list_terms(self, symbol: str):
 url = f"{TS_BASE_URL}/options/expirations?symbol={symbol}"
 async with aiohttp.ClientSession(headers=HEADERS) as s:
 async with s.get(url, timeout=10) as r:
 r.raise_for_status()
 return await r.json() # [{"date":"YYYY-MM-DD","dte":N}, ...]

 async def list_strikes(self, symbol: str, dte: int):
 url = f"{TS_BASE_URL}/options/strikes?symbol={symbol}&dte={dte}"
 async with aiohttp.ClientSession(headers=HEADERS) as s:
 async with s.get(url, timeout=10) as r:
 r.raise_for_status()
 data = await r.json()
 return [int(x) for x in data["strikes"]]

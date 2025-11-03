"""
Earnings Calendar Scraper for FlowMind
Scrapes upcoming earnings from Finviz (free, reliable)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EarningsScraper:
    """Singleton scraper for earnings calendar"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        self._initialized = True
        logger.info("EarningsScraper initialized")

    def scrape_finviz_earnings(
        self, date: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """
        Scrape earnings calendar from Finviz.
        
        Args:
            date: Date in format 'YYYY-MM-DD' (None = today)
            limit: Max number of earnings to return
            
        Returns:
            List of earnings with: symbol, company, market_cap, time, date
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Finviz uses format: YYYYMMDD
        finviz_date = date.replace("-", "")

        url = f"https://finviz.com/calendar.ashx?day={finviz_date}"
        logger.info(f"Scraping Finviz earnings for date: {date}")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            earnings = []

            # Find earnings table (class="calendar")
            table = soup.find("table", class_="calendar")
            if not table:
                logger.warning("Earnings table not found on Finviz")
                return []

            # Find all rows with earnings data
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 5:
                    continue

                # Extract time (BMO/AMC)
                time_cell = cells[0].get_text(strip=True)
                if time_cell not in ["b.open", "a.close"]:
                    continue

                # Extract symbol link
                symbol_link = cells[1].find("a")
                if not symbol_link:
                    continue

                symbol = symbol_link.get_text(strip=True)

                # Extract company name
                company = cells[2].get_text(strip=True)

                # Extract market cap
                market_cap = cells[3].get_text(strip=True)

                # Determine earnings time
                earnings_time = "BMO" if time_cell == "b.open" else "AMC"

                earning = {
                    "symbol": symbol,
                    "company": company,
                    "market_cap": market_cap,
                    "time": earnings_time,
                    "date": date,
                    "source": "Finviz",
                }

                earnings.append(earning)

                if len(earnings) >= limit:
                    break

            logger.info(f"✅ Scraped {len(earnings)} earnings for {date}")
            return earnings

        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            return []

    def scrape_earnings_calendar(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """
        Scrape earnings calendar for next N days.
        
        Args:
            days: Number of days to look ahead (default 7)
            limit: Max total earnings to return
            
        Returns:
            Combined list of earnings from all days
        """
        logger.info(f"Scraping earnings calendar for next {days} days")

        all_earnings = []
        today = datetime.now()

        for i in range(days):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            daily_earnings = self.scrape_finviz_earnings(
                date=date_str, limit=limit - len(all_earnings)
            )

            all_earnings.extend(daily_earnings)

            if len(all_earnings) >= limit:
                break

        # Sort by date, then time (BMO before AMC)
        all_earnings.sort(key=lambda x: (x["date"], x["time"]))

        logger.info(f"✅ Total earnings scraped: {len(all_earnings)}")
        return all_earnings

    def filter_by_symbols(
        self, symbols: List[str], days: int = 30
    ) -> Dict[str, Dict]:
        """
        Find earnings for specific symbols.
        
        Args:
            symbols: List of ticker symbols to track
            days: Days to look ahead
            
        Returns:
            Dict mapping symbol to earnings info
        """
        logger.info(f"Finding earnings for {len(symbols)} symbols")

        # Get all earnings for next N days
        all_earnings = self.scrape_earnings_calendar(days=days, limit=500)

        # Filter by symbols
        symbol_map = {}
        for earning in all_earnings:
            if earning["symbol"] in symbols:
                symbol_map[earning["symbol"]] = earning

        logger.info(f"✅ Found earnings for {len(symbol_map)} symbols")
        return symbol_map

    def get_high_profile_earnings(
        self, min_market_cap: str = "50B", days: int = 7
    ) -> List[Dict]:
        """
        Get earnings for high-profile stocks (large market cap).
        
        Args:
            min_market_cap: Minimum market cap (e.g., "50B", "10B")
            days: Days to look ahead
            
        Returns:
            List of high-profile earnings
        """
        logger.info(f"Getting high-profile earnings (min cap: {min_market_cap})")

        # Parse min market cap value
        cap_value = float(min_market_cap[:-1])  # Remove 'B'

        all_earnings = self.scrape_earnings_calendar(days=days, limit=200)

        # Filter by market cap
        high_profile = []
        for earning in all_earnings:
            market_cap = earning["market_cap"]
            if not market_cap or market_cap == "-":
                continue

            # Parse market cap (e.g., "50.2B", "1.5T")
            try:
                if "T" in market_cap:
                    value = float(market_cap.replace("T", "")) * 1000
                elif "B" in market_cap:
                    value = float(market_cap.replace("B", ""))
                elif "M" in market_cap:
                    value = float(market_cap.replace("M", "")) / 1000
                else:
                    continue

                if value >= cap_value:
                    high_profile.append(earning)

            except ValueError:
                continue

        logger.info(f"✅ Found {len(high_profile)} high-profile earnings")
        return high_profile


# Test functionality
if __name__ == "__main__":
    print("=" * 80)
    print("EARNINGS SCRAPER TEST")
    print("=" * 80)

    scraper = EarningsScraper()

    # Test 1: Today's earnings
    print("\n📅 Testing Today's Earnings...")
    today_earnings = scraper.scrape_finviz_earnings(limit=10)
    print(f"Found {len(today_earnings)} earnings today:")
    for e in today_earnings[:5]:
        print(f"  {e['symbol']:6} | {e['time']:3} | {e['market_cap']:8} | {e['company'][:40]}")

    # Test 2: Next 7 days
    print("\n📆 Testing Next 7 Days Calendar...")
    week_earnings = scraper.scrape_earnings_calendar(days=7, limit=20)
    print(f"Found {len(week_earnings)} earnings in next 7 days:")
    current_date = None
    for e in week_earnings[:10]:
        if e["date"] != current_date:
            print(f"\n  {e['date']}:")
            current_date = e["date"]
        print(f"    {e['symbol']:6} | {e['time']:3} | {e['market_cap']:8} | {e['company'][:35]}")

    # Test 3: Specific symbols
    print("\n🔍 Testing Symbol Filter...")
    watchlist = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META"]
    symbol_earnings = scraper.filter_by_symbols(watchlist, days=30)
    print(f"Found earnings for {len(symbol_earnings)} watchlist symbols:")
    for symbol, e in symbol_earnings.items():
        print(f"  {symbol:6} | {e['date']} {e['time']} | {e['market_cap']:8}")

    # Test 4: High-profile earnings
    print("\n⭐ Testing High-Profile Earnings (>$50B)...")
    high_profile = scraper.get_high_profile_earnings(min_market_cap="50B", days=7)
    print(f"Found {len(high_profile)} high-profile earnings:")
    for e in high_profile[:10]:
        print(f"  {e['symbol']:6} | {e['date']} {e['time']} | {e['market_cap']:8} | {e['company'][:35]}")

    print("\n" + "=" * 80)
    print("✅ EARNINGS SCRAPER TEST COMPLETE")
    print("=" * 80)

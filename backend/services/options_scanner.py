"""
Options Scanner - Extrage options data de la Barchart (free, legal)
Folosește requests + BeautifulSoup

Created: November 3, 2025
"""
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class OptionsScanner:
    """
    Scanner pentru options data din surse publice free.
    Focus: High IV, unusual volume, upcoming expirations.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scan_high_iv_stocks(self, min_iv: int = 50, limit: int = 20) -> List[Dict]:
        """
        Extrage stocks cu IV Rank ridicat de pe Barchart.
        
        Args:
            min_iv: Minimum IV Rank (0-100)
            limit: Max results
            
        Returns:
            List of high IV stocks
        """
        stocks = []
        
        try:
            # Barchart options overview page
            url = "https://www.barchart.com/options/highest-implied-volatility/stocks"
            logger.info(f"Scanning Barchart for high IV stocks (min_iv={min_iv})")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main data table
            table = soup.find('table', {'class': 'bc-table'})
            if not table:
                logger.warning("No data table found on Barchart")
                return stocks
            
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
            
            for row in rows[:limit]:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 5:
                        continue
                    
                    # Extract data
                    symbol_elem = cells[0].find('a')
                    symbol = symbol_elem.text.strip() if symbol_elem else cells[0].text.strip()
                    
                    # Try to find IV value
                    iv_text = None
                    for cell in cells[1:]:
                        text = cell.text.strip()
                        if '%' in text and text.replace('%', '').replace('.', '').isdigit():
                            iv_text = text
                            break
                    
                    if not iv_text:
                        continue
                    
                    iv_value = float(iv_text.replace('%', ''))
                    
                    if iv_value >= min_iv:
                        stocks.append({
                            "symbol": symbol,
                            "iv": iv_value,
                            "source": "Barchart",
                            "scanned_at": datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Barchart row: {e}")
                    continue
            
            logger.info(f"Found {len(stocks)} high IV stocks (min_iv={min_iv})")
            
        except requests.RequestException as e:
            logger.error(f"Request error scanning Barchart: {e}")
        except Exception as e:
            logger.error(f"Error scanning Barchart: {e}")
        
        return stocks
    
    def get_options_chain(self, symbol: str, days_to_expiry: int = 30) -> Dict:
        """
        Extrage options chain pentru un simbol de pe Barchart.
        
        Args:
            symbol: Ticker symbol
            days_to_expiry: Target DTE (closest match)
            
        Returns:
            Options chain data with calls and puts
        """
        try:
            url = f"https://www.barchart.com/stocks/quotes/{symbol}/options"
            logger.info(f"Getting options chain for {symbol}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find spot price
            spot_elem = soup.find('span', {'class': 'last-change'})
            spot_price = 0.0
            if spot_elem:
                spot_text = spot_elem.text.strip().replace('$', '').replace(',', '')
                try:
                    spot_price = float(spot_text)
                except:
                    pass
            
            # Find IV
            iv_elem = soup.find('span', text='IV')
            iv_value = 0.0
            if iv_elem:
                iv_parent = iv_elem.find_parent()
                if iv_parent:
                    iv_text = iv_parent.text.replace('IV', '').replace('%', '').strip()
                    try:
                        iv_value = float(iv_text)
                    except:
                        pass
            
            return {
                "symbol": symbol.upper(),
                "spot_price": spot_price,
                "iv": iv_value,
                "days_to_expiry": days_to_expiry,
                "calls": [],  # TODO: Parse call options
                "puts": [],   # TODO: Parse put options
                "scraped_at": datetime.now().isoformat(),
                "source": "Barchart"
            }
            
        except requests.RequestException as e:
            logger.error(f"Request error getting options chain: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error getting options chain: {e}")
            return {"error": str(e)}
    
    def scan_unusual_volume(self, min_volume: int = 1000, limit: int = 20) -> List[Dict]:
        """
        Extrage options cu volum neobișnuit de mare.
        
        Args:
            min_volume: Minimum volume threshold
            limit: Max results
            
        Returns:
            List of options with unusual volume
        """
        options = []
        
        try:
            url = "https://www.barchart.com/options/unusual-activity/stocks"
            logger.info(f"Scanning unusual options volume (min={min_volume})")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find data table
            table = soup.find('table', {'class': 'bc-table'})
            if not table:
                logger.warning("No unusual activity table found")
                return options
            
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
            
            for row in rows[:limit]:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue
                    
                    # Extract symbol
                    symbol_elem = cells[0].find('a')
                    symbol = symbol_elem.text.strip() if symbol_elem else cells[0].text.strip()
                    
                    # Extract volume
                    volume_text = cells[1].text.strip().replace(',', '')
                    try:
                        volume = int(volume_text)
                    except:
                        continue
                    
                    if volume >= min_volume:
                        options.append({
                            "symbol": symbol,
                            "volume": volume,
                            "source": "Barchart",
                            "scanned_at": datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse unusual volume row: {e}")
                    continue
            
            logger.info(f"Found {len(options)} options with unusual volume")
            
        except requests.RequestException as e:
            logger.error(f"Request error scanning unusual volume: {e}")
        except Exception as e:
            logger.error(f"Error scanning unusual volume: {e}")
        
        return options
    
    def get_earnings_calendar(self, days_ahead: int = 7) -> List[Dict]:
        """
        Extrage earnings calendar pentru următoarele zile.
        
        Args:
            days_ahead: Câte zile înainte
            
        Returns:
            List of upcoming earnings
        """
        earnings = []
        
        try:
            url = "https://www.barchart.com/stocks/earnings-calendar"
            logger.info(f"Getting earnings calendar (next {days_ahead} days)")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find earnings table
            table = soup.find('table', {'class': 'bc-table'})
            if not table:
                logger.warning("No earnings calendar found")
                return earnings
            
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue
                    
                    # Symbol
                    symbol_elem = cells[0].find('a')
                    symbol = symbol_elem.text.strip() if symbol_elem else cells[0].text.strip()
                    
                    # Date
                    date_text = cells[1].text.strip()
                    
                    earnings.append({
                        "symbol": symbol,
                        "date": date_text,
                        "source": "Barchart",
                        "scraped_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse earnings row: {e}")
                    continue
            
            logger.info(f"Found {len(earnings)} upcoming earnings")
            
        except requests.RequestException as e:
            logger.error(f"Request error getting earnings: {e}")
        except Exception as e:
            logger.error(f"Error getting earnings: {e}")
        
        return earnings


# Singleton
_scanner = None


def get_options_scanner() -> OptionsScanner:
    """Get or create scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = OptionsScanner()
    return _scanner


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scanner = OptionsScanner()
    
    # Test 1: High IV stocks
    print("\n📊 Testing High IV Scanner...")
    high_iv = scanner.scan_high_iv_stocks(min_iv=50, limit=10)
    print(f"Found {len(high_iv)} high IV stocks")
    for stock in high_iv[:5]:
        print(f"  - {stock['symbol']}: IV {stock['iv']}%")
    
    # Test 2: Unusual volume
    print("\n🔥 Testing Unusual Volume Scanner...")
    unusual = scanner.scan_unusual_volume(min_volume=1000, limit=10)
    print(f"Found {len(unusual)} options with unusual volume")
    for opt in unusual[:5]:
        print(f"  - {opt['symbol']}: Volume {opt['volume']:,}")
    
    # Test 3: Earnings calendar
    print("\n📅 Testing Earnings Calendar...")
    earnings = scanner.get_earnings_calendar(days_ahead=7)
    print(f"Found {len(earnings)} upcoming earnings")
    for earn in earnings[:5]:
        print(f"  - {earn['symbol']}: {earn['date']}")
    
    # Test 4: Options chain
    print("\n⛓️  Testing Options Chain...")
    chain = scanner.get_options_chain("AAPL", days_to_expiry=30)
    if "error" not in chain:
        print(f"  Symbol: {chain['symbol']}")
        print(f"  Spot: ${chain['spot_price']}")
        print(f"  IV: {chain['iv']}%")
    else:
        print(f"  Error: {chain['error']}")

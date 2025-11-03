"""
UI Automation Service for FlowMind (Nov 3, 2025)

Automatizare interacțiuni UI pentru:
- TradeStation login automation
- Broker account scraping
- Options chain extraction
- Screenshot generation
- PDF report creation
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logger = logging.getLogger(__name__)


class UIAutomation:
    """Base class for UI automation tasks"""
    
    def __init__(self, headless: bool = True, slow_mo: int = 0):
        """
        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by N milliseconds
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
        
    async def start(self):
        """Start browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        logger.info("Browser started successfully")
        
    async def stop(self):
        """Stop browser instance"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped")
        
    async def new_page(self) -> Page:
        """Create new page"""
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
        return await self.context.new_page()
        
    async def screenshot(self, page: Page, path: str) -> str:
        """Take screenshot of page"""
        await page.screenshot(path=path, full_page=True)
        logger.info(f"Screenshot saved: {path}")
        return path
        
    async def wait_for_navigation(self, page: Page, timeout: int = 30000):
        """Wait for navigation to complete"""
        await page.wait_for_load_state("networkidle", timeout=timeout)


class TradeStationAutomation(UIAutomation):
    """TradeStation login and data extraction automation"""
    
    BASE_URL = "https://www.tradestation.com"
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Automate TradeStation login with 2FA handling
        
        Args:
            username: TradeStation username
            password: TradeStation password
            
        Returns:
            Login result with status and cookies
        """
        page = await self.new_page()
        
        try:
            logger.info("Navigating to TradeStation login...")
            await page.goto(f"{self.BASE_URL}/login")
            
            # Fill username
            await page.fill('input[name="username"]', username)
            logger.info("Username filled")
            
            # Fill password
            await page.fill('input[name="password"]', password)
            logger.info("Password filled")
            
            # Click login button
            await page.click('button[type="submit"]')
            logger.info("Login button clicked")
            
            # Wait for either 2FA page or dashboard
            await page.wait_for_load_state("networkidle")
            
            # Check if 2FA is required
            if "two-factor" in page.url.lower() or await page.query_selector('input[name="code"]'):
                logger.info("2FA detected - waiting for manual input...")
                
                # Wait for 2FA code input (user must enter manually)
                await page.wait_for_selector('input[name="code"]', timeout=120000)
                
                # Return partial result - user needs to complete 2FA
                return {
                    "status": "2FA_REQUIRED",
                    "message": "Please enter 2FA code in browser",
                    "url": page.url
                }
            
            # Login successful
            cookies = await self.context.cookies()
            
            return {
                "status": "SUCCESS",
                "cookies": cookies,
                "url": page.url
            }
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
        finally:
            await page.close()
            
    async def get_account_balances(self, cookies: List[Dict]) -> Dict[str, Any]:
        """
        Extract account balances from TradeStation dashboard
        
        Args:
            cookies: Session cookies from login
            
        Returns:
            Account balances data
        """
        page = await self.new_page()
        
        try:
            # Set cookies
            await self.context.add_cookies(cookies)
            
            # Navigate to accounts page
            await page.goto(f"{self.BASE_URL}/accounts")
            await self.wait_for_navigation(page)
            
            # Extract account data (adapt selectors to actual TS layout)
            accounts = await page.evaluate("""
                () => {
                    const accounts = [];
                    document.querySelectorAll('.account-card').forEach(card => {
                        accounts.push({
                            id: card.querySelector('.account-id')?.textContent,
                            name: card.querySelector('.account-name')?.textContent,
                            balance: card.querySelector('.balance')?.textContent,
                            buying_power: card.querySelector('.buying-power')?.textContent
                        });
                    });
                    return accounts;
                }
            """)
            
            return {
                "status": "SUCCESS",
                "accounts": accounts
            }
            
        except Exception as e:
            logger.error(f"Failed to get balances: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
        finally:
            await page.close()


class BrokerScraper(UIAutomation):
    """Generic broker account scraper"""
    
    async def scrape_positions(
        self, 
        broker: str, 
        account_url: str,
        cookies: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Scrape positions from broker account page
        
        Args:
            broker: Broker name (TradeStation, Tastytrade, IBKR)
            account_url: URL to account positions page
            cookies: Optional session cookies
            
        Returns:
            Positions data
        """
        page = await self.new_page()
        
        try:
            if cookies:
                await self.context.add_cookies(cookies)
                
            logger.info(f"Scraping {broker} positions from {account_url}")
            await page.goto(account_url)
            await self.wait_for_navigation(page)
            
            # Take screenshot for debugging
            screenshot_path = f"/tmp/{broker}_positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.screenshot(page, screenshot_path)
            
            # Extract positions (generic selector - adapt per broker)
            positions = await page.evaluate("""
                () => {
                    const positions = [];
                    document.querySelectorAll('tr[data-position], .position-row').forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 4) {
                            positions.push({
                                symbol: cells[0]?.textContent?.trim(),
                                quantity: cells[1]?.textContent?.trim(),
                                price: cells[2]?.textContent?.trim(),
                                value: cells[3]?.textContent?.trim()
                            });
                        }
                    });
                    return positions;
                }
            """)
            
            return {
                "status": "SUCCESS",
                "broker": broker,
                "positions": positions,
                "screenshot": screenshot_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape positions: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
        finally:
            await page.close()


class OptionsChainExtractor(UIAutomation):
    """Extract options chain data from web interfaces"""
    
    async def extract_chain(
        self, 
        symbol: str,
        source: str = "yahoo"
    ) -> Dict[str, Any]:
        """
        Extract options chain from public sources
        
        Args:
            symbol: Stock symbol
            source: Data source (yahoo, cboe, etc.)
            
        Returns:
            Options chain data
        """
        page = await self.new_page()
        
        try:
            if source == "yahoo":
                url = f"https://finance.yahoo.com/quote/{symbol}/options"
            else:
                raise ValueError(f"Unknown source: {source}")
                
            logger.info(f"Extracting options chain for {symbol} from {source}")
            await page.goto(url)
            await self.wait_for_navigation(page)
            
            # Extract calls and puts
            options_data = await page.evaluate("""
                () => {
                    const calls = [];
                    const puts = [];
                    
                    // Extract calls
                    document.querySelectorAll('table.calls tbody tr').forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 7) {
                            calls.push({
                                strike: cells[2]?.textContent,
                                last: cells[3]?.textContent,
                                bid: cells[4]?.textContent,
                                ask: cells[5]?.textContent,
                                volume: cells[7]?.textContent,
                                open_interest: cells[8]?.textContent
                            });
                        }
                    });
                    
                    // Extract puts
                    document.querySelectorAll('table.puts tbody tr').forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 7) {
                            puts.push({
                                strike: cells[2]?.textContent,
                                last: cells[3]?.textContent,
                                bid: cells[4]?.textContent,
                                ask: cells[5]?.textContent,
                                volume: cells[7]?.textContent,
                                open_interest: cells[8]?.textContent
                            });
                        }
                    });
                    
                    return { calls, puts };
                }
            """)
            
            return {
                "status": "SUCCESS",
                "symbol": symbol,
                "source": source,
                "data": options_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to extract options chain: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
        finally:
            await page.close()


class PDFReportGenerator(UIAutomation):
    """Generate PDF reports from web pages"""
    
    async def generate_report(
        self, 
        url: str,
        output_path: str,
        wait_for_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate PDF report from URL
        
        Args:
            url: URL to generate PDF from
            output_path: Output PDF file path
            wait_for_selector: Optional CSS selector to wait for
            
        Returns:
            Generation result
        """
        page = await self.new_page()
        
        try:
            logger.info(f"Generating PDF report from {url}")
            await page.goto(url)
            
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector)
            else:
                await self.wait_for_navigation(page)
            
            # Generate PDF
            await page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "20px",
                    "right": "20px",
                    "bottom": "20px",
                    "left": "20px"
                }
            )
            
            logger.info(f"PDF report saved: {output_path}")
            
            return {
                "status": "SUCCESS",
                "output": output_path,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
        finally:
            await page.close()


# Convenience functions for common tasks

async def automate_tradestation_login(username: str, password: str) -> Dict[str, Any]:
    """Quick TradeStation login automation"""
    async with TradeStationAutomation() as automation:
        return await automation.login(username, password)


async def scrape_broker_positions(broker: str, url: str, cookies: List[Dict]) -> Dict[str, Any]:
    """Quick broker positions scraping"""
    async with BrokerScraper() as scraper:
        return await scraper.scrape_positions(broker, url, cookies)


async def extract_options_chain(symbol: str, source: str = "yahoo") -> Dict[str, Any]:
    """Quick options chain extraction"""
    async with OptionsChainExtractor() as extractor:
        return await extractor.extract_chain(symbol, source)


async def generate_pdf_report(url: str, output_path: str) -> Dict[str, Any]:
    """Quick PDF report generation"""
    async with PDFReportGenerator() as generator:
        return await generator.generate_report(url, output_path)


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    async def test_automation():
        """Test automation capabilities"""
        print("🤖 Testing UI Automation\n")
        
        # Test 1: Options chain extraction
        print("1️⃣  Testing options chain extraction...")
        result = await extract_options_chain("AAPL", "yahoo")
        print(f"   Status: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"   Calls: {len(result['data']['calls'])}")
            print(f"   Puts: {len(result['data']['puts'])}")
        
        # Test 2: Screenshot generation
        print("\n2️⃣  Testing screenshot generation...")
        async with UIAutomation() as automation:
            page = await automation.new_page()
            await page.goto("https://finance.yahoo.com")
            screenshot_path = "/tmp/yahoo_finance_test.png"
            await automation.screenshot(page, screenshot_path)
            print(f"   ✅ Screenshot saved: {screenshot_path}")
            await page.close()
        
        print("\n✅ All tests completed!")
    
    asyncio.run(test_automation())

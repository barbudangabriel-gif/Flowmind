"""
News Scraper Service - Yahoo Finance & Benzinga
Folosește Playwright pentru extragere știri financiare (LEGAL)

Created: November 3, 2025
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class NewsScraperService:
    """
    Scraper pentru știri financiare din surse publice.
    Respectă robots.txt și rate limits.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def scrape_yahoo_finance(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Extrage știri pentru un simbol din Yahoo Finance.
        
        Args:
            symbol: Ticker symbol (ex: "AAPL", "TSLA")
            limit: Număr maxim de știri
            
        Returns:
            List of news articles with title, url, source, published_at
        """
        news = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(user_agent=self.user_agent)
                page = context.new_page()
                
                # Navigate to Yahoo Finance news page
                url = f"https://finance.yahoo.com/quote/{symbol}/news"
                logger.info(f"Scraping Yahoo Finance news for {symbol}")
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Try multiple selectors (Yahoo changes them frequently)
                articles = (
                    page.query_selector_all('li[data-test-locator="stream-item"]') or
                    page.query_selector_all('article') or
                    page.query_selector_all('div[data-test="news-stream"] li') or
                    []
                )
                
                for article in articles[:limit]:
                    try:
                        # Title & URL (multiple selector strategies)
                        title_elem = (
                            article.query_selector('h3 a') or
                            article.query_selector('h2 a') or
                            article.query_selector('a[data-test="item-title"]') or
                            article.query_selector('a')
                        )
                        if not title_elem:
                            continue
                        
                        title = title_elem.text_content().strip()
                        href = title_elem.get_attribute('href')
                        full_url = f"https://finance.yahoo.com{href}" if href.startswith('/') else href
                        
                        # Source
                        source_elem = article.query_selector('div[data-test-locator="stream-item-publisher"]')
                        source = source_elem.text_content().strip() if source_elem else "Yahoo Finance"
                        
                        # Time
                        time_elem = article.query_selector('time')
                        published_at = time_elem.get_attribute('datetime') if time_elem else None
                        
                        news.append({
                            "title": title,
                            "url": full_url,
                            "source": source,
                            "published_at": published_at,
                            "symbol": symbol.upper(),
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse article: {e}")
                        continue
                
                browser.close()
                logger.info(f"Scraped {len(news)} articles for {symbol}")
                
        except PlaywrightTimeout:
            logger.error(f"Timeout scraping Yahoo Finance for {symbol}")
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance: {e}")
        
        return news
    
    def scrape_benzinga(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Extrage știri pentru un simbol din Benzinga.
        
        Args:
            symbol: Ticker symbol
            limit: Număr maxim de știri
            
        Returns:
            List of news articles
        """
        news = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(user_agent=self.user_agent)
                page = context.new_page()
                
                # Navigate to Benzinga stock page
                url = f"https://www.benzinga.com/quote/{symbol}/news"
                logger.info(f"Scraping Benzinga news for {symbol}")
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                # Wait for articles
                page.wait_for_selector('article.article-preview', timeout=10000)
                
                # Extract articles
                articles = page.query_selector_all('article.article-preview')
                
                for article in articles[:limit]:
                    try:
                        # Title & URL
                        title_elem = article.query_selector('h2 a, h3 a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.text_content().strip()
                        href = title_elem.get_attribute('href')
                        full_url = f"https://www.benzinga.com{href}" if href.startswith('/') else href
                        
                        # Time
                        time_elem = article.query_selector('time')
                        published_at = time_elem.get_attribute('datetime') if time_elem else None
                        
                        news.append({
                            "title": title,
                            "url": full_url,
                            "source": "Benzinga",
                            "published_at": published_at,
                            "symbol": symbol.upper(),
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse Benzinga article: {e}")
                        continue
                
                browser.close()
                logger.info(f"Scraped {len(news)} Benzinga articles for {symbol}")
                
        except PlaywrightTimeout:
            logger.error(f"Timeout scraping Benzinga for {symbol}")
        except Exception as e:
            logger.error(f"Error scraping Benzinga: {e}")
        
        return news
    
    def aggregate_news(self, symbol: str, limit_per_source: int = 10) -> Dict:
        """
        Agregă știri din toate sursele pentru un simbol.
        
        Args:
            symbol: Ticker symbol
            limit_per_source: Max articole per sursă
            
        Returns:
            Dict with news from all sources + combined list
        """
        yahoo_news = self.scrape_yahoo_finance(symbol, limit_per_source)
        benzinga_news = self.scrape_benzinga(symbol, limit_per_source)
        
        # Combine and sort by published_at
        all_news = yahoo_news + benzinga_news
        all_news.sort(
            key=lambda x: x.get("published_at") or "2000-01-01",
            reverse=True
        )
        
        return {
            "symbol": symbol.upper(),
            "total_articles": len(all_news),
            "sources": {
                "yahoo_finance": len(yahoo_news),
                "benzinga": len(benzinga_news)
            },
            "news": all_news,
            "scraped_at": datetime.utcnow().isoformat()
        }


# Singleton instance
_scraper_instance = None


def get_news_scraper(headless: bool = True) -> NewsScraperService:
    """Get or create news scraper instance"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = NewsScraperService(headless=headless)
    return _scraper_instance


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = NewsScraperService(headless=True)
    
    # Test Yahoo Finance
    print("\n📰 Testing Yahoo Finance scraper...")
    yahoo_news = scraper.scrape_yahoo_finance("TSLA", limit=5)
    print(f"Found {len(yahoo_news)} articles")
    for article in yahoo_news[:3]:
        print(f"  - {article['title'][:60]}...")
    
    # Test Benzinga
    print("\n📰 Testing Benzinga scraper...")
    benzinga_news = scraper.scrape_benzinga("TSLA", limit=5)
    print(f"Found {len(benzinga_news)} articles")
    for article in benzinga_news[:3]:
        print(f"  - {article['title'][:60]}...")
    
    # Test aggregation
    print("\n📊 Testing aggregation...")
    result = scraper.aggregate_news("NVDA", limit_per_source=5)
    print(f"Total: {result['total_articles']} articles")
    print(f"Sources: {result['sources']}")

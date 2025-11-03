"""
Simple News Scraper - Folosește requests + BeautifulSoup (mai rapid, mai simplu)
Nu necesită Playwright/browser

Created: November 3, 2025
"""
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class SimpleNewsScraper:
    """
    Scraper simplu pentru știri financiare.
    Folosește requests + BeautifulSoup (fără browser).
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_finviz_news(self, symbol: str, limit: int = 20) -> List[Dict]:
        """
        Extrage știri din Finviz (cel mai simplu, fără JS).
        
        Args:
            symbol: Ticker symbol
            limit: Max articole
            
        Returns:
            List of news articles
        """
        news = []
        
        try:
            url = f"https://finviz.com/quote.ashx?t={symbol}&p=d"
            logger.info(f"Scraping Finviz news for {symbol}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news table
            news_table = soup.find('table', {'id': 'news-table'})
            if not news_table:
                logger.warning(f"No news table found for {symbol}")
                return news
            
            rows = news_table.find_all('tr')
            
            for row in rows[:limit]:
                try:
                    # Get link
                    link_elem = row.find('a', {'class': 'tab-link-news'})
                    if not link_elem:
                        continue
                    
                    title = link_elem.text.strip()
                    url = link_elem['href']
                    
                    # Get source
                    source_elem = row.find('span', {'class': 'news-source'}) or row.find('div', {'class': 'news-source-name'})
                    source = source_elem.text.strip() if source_elem else "Unknown"
                    
                    # Get time
                    time_elem = row.find('td', {'width': '130', 'align': 'right'})
                    published_at = time_elem.text.strip() if time_elem else None
                    
                    news.append({
                        "title": title,
                        "url": url,
                        "source": source,
                        "published_at": published_at,
                        "symbol": symbol.upper(),
                        "scraped_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Finviz row: {e}")
                    continue
            
            logger.info(f"Scraped {len(news)} articles for {symbol} from Finviz")
            
        except requests.RequestException as e:
            logger.error(f"Request error scraping Finviz: {e}")
        except Exception as e:
            logger.error(f"Error scraping Finviz: {e}")
        
        return news
    
    def scrape_marketwatch_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Extrage știri din MarketWatch.
        
        Args:
            symbol: Ticker symbol
            limit: Max articole
            
        Returns:
            List of news articles
        """
        news = []
        
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            logger.info(f"Scraping MarketWatch news for {symbol}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find articles
            articles = soup.find_all('div', {'class': 'article__content'})
            
            for article in articles[:limit]:
                try:
                    # Title & URL
                    link_elem = article.find('a', {'class': 'link'})
                    if not link_elem:
                        continue
                    
                    title = link_elem.text.strip()
                    href = link_elem['href']
                    full_url = f"https://www.marketwatch.com{href}" if href.startswith('/') else href
                    
                    # Time
                    time_elem = article.find('time')
                    published_at = time_elem['datetime'] if time_elem and 'datetime' in time_elem.attrs else None
                    
                    news.append({
                        "title": title,
                        "url": full_url,
                        "source": "MarketWatch",
                        "published_at": published_at,
                        "symbol": symbol.upper(),
                        "scraped_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse MarketWatch article: {e}")
                    continue
            
            logger.info(f"Scraped {len(news)} articles for {symbol} from MarketWatch")
            
        except requests.RequestException as e:
            logger.error(f"Request error scraping MarketWatch: {e}")
        except Exception as e:
            logger.error(f"Error scraping MarketWatch: {e}")
        
        return news
    
    def aggregate_news(self, symbol: str) -> Dict:
        """
        Agregă știri din toate sursele.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Combined news from all sources
        """
        finviz_news = self.scrape_finviz_news(symbol, limit=15)
        marketwatch_news = self.scrape_marketwatch_news(symbol, limit=10)
        
        all_news = finviz_news + marketwatch_news
        
        # Remove duplicates based on title similarity
        unique_news = []
        seen_titles = set()
        
        for article in all_news:
            # Simple deduplication: first 50 chars of title
            title_key = article['title'][:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(article)
        
        # Sort by scraped_at (most recent first)
        unique_news.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
        
        return {
            "symbol": symbol.upper(),
            "total_articles": len(unique_news),
            "sources": {
                "finviz": len(finviz_news),
                "marketwatch": len(marketwatch_news)
            },
            "news": unique_news[:25],  # Max 25 articles
            "scraped_at": datetime.now().isoformat()
        }


# Singleton
_scraper = None


def get_news_scraper() -> SimpleNewsScraper:
    """Get or create scraper instance"""
    global _scraper
    if _scraper is None:
        _scraper = SimpleNewsScraper()
    return _scraper


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = SimpleNewsScraper()
    
    # Test Finviz
    print("\n📰 Testing Finviz scraper...")
    finviz_news = scraper.scrape_finviz_news("TSLA", limit=5)
    print(f"Found {len(finviz_news)} articles")
    for article in finviz_news[:3]:
        print(f"  - {article['title'][:70]}...")
        print(f"    Source: {article['source']} | {article['published_at']}")
    
    # Test MarketWatch
    print("\n📰 Testing MarketWatch scraper...")
    mw_news = scraper.scrape_marketwatch_news("NVDA", limit=5)
    print(f"Found {len(mw_news)} articles")
    for article in mw_news[:3]:
        print(f"  - {article['title'][:70]}...")
    
    # Test aggregation
    print("\n📊 Testing aggregation...")
    result = scraper.aggregate_news("AAPL")
    print(f"Total: {result['total_articles']} unique articles")
    print(f"Sources: {result['sources']}")

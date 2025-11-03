"""
UI Automation API Router (Nov 3, 2025)

Endpoints pentru automatizare interacțiuni UI
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from services.ui_automation import (
    automate_tradestation_login,
    scrape_broker_positions,
    extract_options_chain,
    generate_pdf_report,
    TradeStationAutomation,
    BrokerScraper,
    OptionsChainExtractor,
    PDFReportGenerator
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/automation", tags=["automation"])


# Request models
class LoginRequest(BaseModel):
    username: str
    password: str
    broker: str = "TradeStation"


class ScrapePositionsRequest(BaseModel):
    broker: str
    account_url: str
    cookies: Optional[List[Dict]] = None


class ExtractOptionsRequest(BaseModel):
    symbol: str
    source: str = "yahoo"


class GeneratePDFRequest(BaseModel):
    url: str
    output_filename: str
    wait_for_selector: Optional[str] = None


# Endpoints

@router.post("/login")
async def login(request: LoginRequest):
    """
    Automate broker login
    
    Supports:
    - TradeStation (with 2FA)
    - Tastytrade (future)
    - IBKR (future)
    """
    try:
        if request.broker.lower() == "tradestation":
            result = await automate_tradestation_login(
                request.username, 
                request.password
            )
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Broker {request.broker} not supported yet"
            )
    except Exception as e:
        logger.error(f"Login automation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/positions")
async def scrape_positions(request: ScrapePositionsRequest):
    """
    Scrape positions from broker account page
    
    Returns:
    - List of positions with symbol, quantity, price, value
    - Screenshot of the page
    - Timestamp
    """
    try:
        result = await scrape_broker_positions(
            request.broker,
            request.account_url,
            request.cookies or []
        )
        return result
    except Exception as e:
        logger.error(f"Position scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options/chain/{symbol}")
async def get_options_chain(symbol: str, source: str = "yahoo"):
    """
    Extract options chain from public sources
    
    Sources:
    - yahoo: Yahoo Finance (free, no auth)
    - cboe: CBOE (future)
    - nasdaq: Nasdaq (future)
    
    Returns:
    - Calls and puts with strikes, prices, volume, OI
    """
    try:
        result = await extract_options_chain(symbol.upper(), source)
        return result
    except Exception as e:
        logger.error(f"Options chain extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/pdf")
async def create_pdf_report(request: GeneratePDFRequest, background_tasks: BackgroundTasks):
    """
    Generate PDF report from URL
    
    Use cases:
    - Portfolio snapshots
    - Options analysis reports
    - Trade confirmations
    """
    try:
        output_path = f"/tmp/{request.output_filename}"
        
        # Run in background if slow
        if request.wait_for_selector:
            background_tasks.add_task(
                generate_pdf_report,
                request.url,
                output_path
            )
            return {
                "status": "PROCESSING",
                "message": "PDF generation started in background",
                "output": output_path
            }
        else:
            result = await generate_pdf_report(request.url, output_path)
            return result
            
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screenshot")
async def take_screenshot(url: str, output_filename: str, full_page: bool = True):
    """
    Take screenshot of URL
    
    Args:
    - url: URL to screenshot
    - output_filename: Output PNG filename
    - full_page: Capture full page (scroll) or viewport only
    """
    try:
        from services.ui_automation import UIAutomation
        
        output_path = f"/tmp/{output_filename}"
        
        async with UIAutomation() as automation:
            page = await automation.new_page()
            await page.goto(url)
            await automation.wait_for_navigation(page)
            
            await page.screenshot(
                path=output_path,
                full_page=full_page
            )
            await page.close()
            
        return {
            "status": "SUCCESS",
            "output": output_path,
            "url": url
        }
        
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check - verify Playwright is available"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
            
        return {
            "status": "healthy",
            "playwright": "available",
            "browsers": ["chromium", "firefox", "webkit"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

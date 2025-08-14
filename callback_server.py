#!/usr/bin/env python3
"""
Simple callback server for TradeStation OAuth
Runs on port 31022 to catch the OAuth callback
"""

import asyncio
from aiohttp import web, ClientSession
import urllib.parse as urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_callback(request):
    """Handle OAuth callback from TradeStation"""
    try:
        # Get authorization code from URL parameters
        code = request.query.get('code')
        state = request.query.get('state')
        error = request.query.get('error')
        
        if error:
            logger.error(f"OAuth error: {error}")
            return web.Response(
                text=f"""
                <html>
                <head><title>Authentication Error</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">❌ Authentication Failed</h1>
                    <p>Error: {error}</p>
                    <p>Please close this window and try again.</p>
                </body>
                </html>
                """,
                content_type='text/html'
            )
        
        if not code:
            logger.error("No authorization code received")
            return web.Response(
                text="""
                <html>
                <head><title>No Code</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: orange;">⚠️ No Authorization Code</h1>
                    <p>No authorization code was received from TradeStation.</p>
                    <p>Please close this window and try again.</p>
                </body>
                </html>
                """,
                content_type='text/html'
            )
        
        logger.info(f"Received authorization code: {code[:10]}...")
        
        # Forward the code to our main backend
        async with ClientSession() as session:
            try:
                async with session.get(
                    f"http://localhost:8001/api/auth/tradestation/callback?code={code}&state={state}"
                ) as response:
                    if response.status == 200:
                        logger.info("Successfully forwarded code to main backend")
                        return web.Response(
                            text="""
                            <html>
                            <head><title>Authentication Successful</title></head>
                            <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                <div style="background: rgba(255,255,255,0.1); padding: 40px; border-radius: 10px; backdrop-filter: blur(10px);">
                                    <div style="font-size: 64px; margin-bottom: 20px;">✅</div>
                                    <h1>Authentication Successful!</h1>
                                    <p>TradeStation connection established.</p>
                                    <p>This window will close automatically...</p>
                                </div>
                                
                                <script>
                                    // Notify parent window
                                    if (window.opener) {
                                        window.opener.postMessage({
                                            type: 'TRADESTATION_AUTH_SUCCESS',
                                            data: { status: 'success' }
                                        }, '*');
                                    }
                                    
                                    // Close window after 3 seconds
                                    setTimeout(() => {
                                        window.close();
                                    }, 3000);
                                </script>
                            </body>
                            </html>
                            """,
                            content_type='text/html'
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Backend error: {response.status} - {error_text}")
                        raise Exception(f"Backend returned {response.status}")
                        
            except Exception as e:
                logger.error(f"Error forwarding to backend: {str(e)}")
                return web.Response(
                    text=f"""
                    <html>
                    <head><title>Backend Error</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: red;">❌ Backend Error</h1>
                        <p>Failed to process authentication: {str(e)}</p>
                        <p><strong>Your authorization code:</strong></p>
                        <p style="background: #f0f0f0; padding: 10px; font-family: monospace; word-break: break-all;">{code}</p>
                        <p>Please copy this code and enter it manually in FlowMind Analytics.</p>
                    </body>
                    </html>
                    """,
                    content_type='text/html'
                )
        
    except Exception as e:
        logger.error(f"Callback handler error: {str(e)}")
        return web.Response(
            text=f"""
            <html>
            <head><title>Server Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Server Error</h1>
                <p>An error occurred: {str(e)}</p>
                <p>Please close this window and try again.</p>
            </body>
            </html>
            """,
            content_type='text/html'
        )

async def init_app():
    """Initialize the web application"""
    app = web.Application()
    app.router.add_get('/', handle_callback)
    app.router.add_get('/callback', handle_callback)
    return app

async def main():
    """Main function to run the callback server"""
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 31022)
    await site.start()
    
    logger.info("TradeStation callback server started on http://localhost:31022")
    logger.info("Waiting for OAuth callbacks...")
    
    try:
        await asyncio.Event().wait()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down callback server...")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
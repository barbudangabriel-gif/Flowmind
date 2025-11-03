"""
FlowMind UI Automation Tests
Browser-based testing for critical user flows
"""

import pytest
from playwright.sync_api import Page, expect
import os

# FlowMind URL
BASE_URL = os.getenv("FLOWMIND_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "FlowMind-Test-Agent/1.0",
    }


class TestHomePage:
    """Test homepage and navigation"""

    def test_homepage_loads(self, page: Page):
        """Verify homepage loads correctly"""
        page.goto(BASE_URL)
        expect(page).to_have_title("FlowMind Analytics")
        
        # Check for main navigation
        expect(page.locator("text=Dashboard")).to_be_visible()
        expect(page.locator("text=Builder")).to_be_visible()
        expect(page.locator("text=Mindfolios")).to_be_visible()

    def test_navigation_to_dashboard(self, page: Page):
        """Test navigation to dashboard"""
        page.goto(BASE_URL)
        page.click("text=Dashboard")
        
        # Wait for dashboard to load
        expect(page.locator("text=Portfolio Overview")).to_be_visible(timeout=5000)

    def test_navigation_to_builder(self, page: Page):
        """Test navigation to builder"""
        page.goto(BASE_URL)
        page.click("text=Builder")
        
        # Wait for builder to load
        expect(page.locator("text=Strategy Builder")).to_be_visible(timeout=5000)


class TestDashboard:
    """Test dashboard functionality"""

    def test_dashboard_stats_display(self, page: Page):
        """Verify dashboard shows key statistics"""
        page.goto(f"{BASE_URL}/dashboard")
        
        # Check for stat cards
        expect(page.locator("text=Total Value")).to_be_visible()
        expect(page.locator("text=P&L")).to_be_visible()
        expect(page.locator("text=Win Rate")).to_be_visible()

    def test_dashboard_chart_renders(self, page: Page):
        """Verify dashboard chart renders"""
        page.goto(f"{BASE_URL}/dashboard")
        
        # Check for chart canvas or SVG
        chart = page.locator("canvas, svg").first
        expect(chart).to_be_visible()


class TestBuilder:
    """Test options strategy builder"""

    def test_builder_tabs_exist(self, page: Page):
        """Verify builder has all tabs"""
        page.goto(f"{BASE_URL}/builder")
        
        expect(page.locator("text=Build")).to_be_visible()
        expect(page.locator("text=Optimize")).to_be_visible()
        expect(page.locator("text=Strategy")).to_be_visible()
        expect(page.locator("text=Flow")).to_be_visible()

    def test_builder_strategy_selection(self, page: Page):
        """Test strategy selection dropdown"""
        page.goto(f"{BASE_URL}/builder")
        
        # Click strategy selector
        page.click("select#strategy-selector, [data-testid='strategy-selector']")
        
        # Verify strategies visible
        expect(page.locator("text=Long Call")).to_be_visible()
        expect(page.locator("text=Bull Put Spread")).to_be_visible()

    def test_builder_chart_updates(self, page: Page):
        """Test chart updates when parameters change"""
        page.goto(f"{BASE_URL}/builder")
        
        # Change strike price
        strike_input = page.locator("input[name='strike'], input[placeholder*='strike']").first
        strike_input.fill("250")
        
        # Wait for chart to update (debounced)
        page.wait_for_timeout(500)
        
        # Verify chart canvas exists
        expect(page.locator("canvas, svg").first).to_be_visible()


class TestMindfolios:
    """Test portfolio management (Mindfolios)"""

    def test_mindfolios_list_loads(self, page: Page):
        """Verify mindfolios list page loads"""
        page.goto(f"{BASE_URL}/mindfolios")
        
        expect(page.locator("text=Mindfolios")).to_be_visible()
        expect(page.locator("text=Create Mindfolio, button:has-text('Create')")).to_be_visible()

    def test_create_mindfolio_modal(self, page: Page):
        """Test create mindfolio modal opens"""
        page.goto(f"{BASE_URL}/mindfolios")
        
        # Click create button
        page.click("button:has-text('Create Mindfolio'), button:has-text('Create')")
        
        # Verify modal appears
        expect(page.locator("text=New Mindfolio, text=Create New")).to_be_visible()
        
        # Check for input fields
        expect(page.locator("input[name='name'], input[placeholder*='name']")).to_be_visible()

    def test_mindfolio_detail_page(self, page: Page):
        """Test mindfolio detail page loads"""
        page.goto(f"{BASE_URL}/mindfolios")
        
        # Click first mindfolio card
        first_mindfolio = page.locator("[data-testid='mindfolio-card'], .mindfolio-card").first
        if first_mindfolio.is_visible():
            first_mindfolio.click()
            
            # Wait for detail page
            expect(page.locator("text=Positions, text=Transactions")).to_be_visible(timeout=5000)


class TestTradeStationIntegration:
    """Test TradeStation broker integration"""

    @pytest.mark.skip(reason="Requires TradeStation authentication")
    def test_tradestation_connect_button(self, page: Page):
        """Test TradeStation connect button exists"""
        page.goto(f"{BASE_URL}/accounts")
        
        expect(page.locator("text=Connect TradeStation, button:has-text('TradeStation')")).to_be_visible()

    @pytest.mark.skip(reason="Requires TradeStation authentication")
    def test_import_positions(self, page: Page):
        """Test import positions from TradeStation"""
        page.goto(f"{BASE_URL}/mindfolios/import")
        
        # This would require OAuth flow completion
        expect(page.locator("text=Import from TradeStation")).to_be_visible()


class TestPerformance:
    """Test performance and loading times"""

    def test_page_load_speed(self, page: Page):
        """Verify pages load within acceptable time"""
        import time
        
        start = time.time()
        page.goto(BASE_URL)
        load_time = time.time() - start
        
        # Should load in under 3 seconds
        assert load_time < 3.0, f"Page loaded in {load_time:.2f}s (threshold: 3s)"

    def test_chart_render_performance(self, page: Page):
        """Verify chart renders quickly"""
        page.goto(f"{BASE_URL}/builder")
        
        # Wait for chart to appear
        chart = page.locator("canvas, svg").first
        expect(chart).to_be_visible(timeout=2000)


class TestResponsiveness:
    """Test responsive design"""

    def test_mobile_viewport(self, page: Page):
        """Test mobile layout"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(BASE_URL)
        
        # Check for mobile menu button
        expect(page.locator("button[aria-label*='menu'], button:has-text('☰')")).to_be_visible()

    def test_tablet_viewport(self, page: Page):
        """Test tablet layout"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(BASE_URL)
        
        # Navigation should be visible
        expect(page.locator("text=Dashboard")).to_be_visible()


class TestErrorHandling:
    """Test error states"""

    def test_404_page(self, page: Page):
        """Test 404 error page"""
        page.goto(f"{BASE_URL}/nonexistent-page")
        
        # Should show 404 or redirect
        expect(page.locator("text=404, text=Not Found")).to_be_visible(timeout=3000)

    def test_api_error_handling(self, page: Page):
        """Test error messages when API fails"""
        # This would require mocking API failures
        pass


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])

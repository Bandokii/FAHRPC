"""
Scraper module for FAHRPC
Handles web scraping of Folding@Home interfaces with caching support
"""

import logging
import re
import time
from typing import Any, Dict, Optional, Tuple

from playwright.async_api import async_playwright

logger = logging.getLogger('FAHRPC')

# Pre-compiled regex patterns
RE_POINTS = re.compile(r'<div class="user-points">([\d,]+) points earned</div>')
RE_WUS = re.compile(r'<div class="user-wus">([\d,]+) WUs completed</div>')
RE_PERCENT = re.compile(r"(\d+\.\d+|\d+)%")
RE_PROJ_ID = re.compile(r'\b\d{5}\b')

class FAHScraper:
    """Manages web scraping of Folding@Home data with caching."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize FAH Scraper.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.browser = None
        self.context = None
        self.control_page = None
        self.stats_page = None

        # Caching
        self._stats_cache: Optional[Tuple[Optional[str], Optional[str]]] = None
        self._cache_timestamp: float = 0
        self._cache_ttl: int = 300  # 5 minutes

    async def initialize(self) -> None:
        """
        Initialize the browser and pages.

        Raises:
            Exception: If browser initialization fails
        """
        p = async_playwright()
        self.playwright = await p.start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.control_page = await self.context.new_page()
        self.stats_page = await self.context.new_page()

    async def get_control_data(self) -> Tuple[list, list, bool]:
        """
        Scrape the local FAH control page.

        Returns:
            Tuple of (percent_complete, project_id, is_running)

        Raises:
            Exception: If scraping fails
        """
        try:
            await self.control_page.goto(
                self.config['foldingathome']['web_url'],
                wait_until="networkidle",
                timeout=8000
            )
            # Extract percent from .progress-text for each project
            percent_elements = await self.control_page.locator('.progress-text').all_text_contents()
            percents = [p.strip().replace('%','') for p in percent_elements if p.strip()] or ["0"]
            proj_ids = RE_PROJ_ID.findall(await self.control_page.content()) or ["Active"]
            is_running = await self.control_page.locator(".state-run").count() > 0
            return percents, proj_ids, is_running
        except Exception as e:
            raise Exception(f"Control page error: {e}")

    async def get_global_stats(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Scrape the FAH stats page for global points and WUs.
        Uses cache to reduce scraper load with 5-minute TTL.

        Returns:
            Tuple of (points, work_units) or (None, None) on error
        """
        # Check cache
        current_time = time.time()
        if self._stats_cache and (current_time - self._cache_timestamp) < self._cache_ttl:
            return self._stats_cache
        try:
            await self.stats_page.goto(
                self.config['foldingathome']['stats_url'],
                wait_until="networkidle",
                timeout=10000
            )
            content = await self.stats_page.content()

            points = RE_POINTS.findall(content)
            wus = RE_WUS.findall(content)

            result = (points[0] if points else None, wus[0] if wus else None)

            # Cache result
            self._stats_cache = result
            self._cache_timestamp = current_time

            return result
        except Exception as e:
            logger.debug(f"Stats scraping failed: {e}")
            return None, None

    async def close(self) -> None:
        """Clean up browser resources."""
        if self.context:
            try:
                await self.context.close()
            except Exception:
                pass
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
        if hasattr(self, 'playwright'):
            try:
                await self.playwright.stop()
            except Exception:
                pass

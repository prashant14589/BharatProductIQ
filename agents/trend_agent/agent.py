"""Trend Detection Agent - Scans TikTok, Amazon US, AliExpress, Reddit, FB Ad Library, Google Trends."""

import os
import sys
from typing import Any

# Add project root for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base import BaseAgent


class TrendAgent(BaseAgent):
    name = "trend"

    def run(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Scan global trend sources and return trending products.
        In production: integrate TikTok API, Amazon Best Sellers, AliExpress, etc.
        """
        # Placeholder: return mock trending products for pipeline testing
        # Replace with real API calls (TikTok, Amazon, AliExpress, pytrends, etc.)
        trends = self._fetch_google_trends(context)
        trends.extend(self._mock_trending_products())
        return trends

    def _fetch_google_trends(self, context: dict) -> list[dict]:
        """Fetch Google Trends data. Uses pytrends in production."""
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl="en-US", tz=360)
            keywords = context.get("keywords", ["dropshipping products", "viral products 2024"])
            pytrends.build_payload(keywords, cat=0, timeframe="now 7-d")
            data = pytrends.interest_over_time()
            if not data.empty:
                # Convert to product-like signals
                return []
        except Exception:
            pass
        return []

    def _mock_trending_products(self) -> list[dict]:
        """Mock trending products for development/demo."""
        return [
            {
                "product_name": "Portable Bladeless Neck Fan",
                "trend_score": 78,
                "trend_sources": ["tiktok", "amazon_us", "aliexpress"],
                "product_images": ["https://via.placeholder.com/400x400?text=Neck+Fan"],
                "video_links": [],
                "category": "Electronics",
            },
            {
                "product_name": "Magnetic Phone Grip Stand",
                "trend_score": 72,
                "trend_sources": ["tiktok", "amazon_us"],
                "product_images": ["https://via.placeholder.com/400x400?text=Phone+Grip"],
                "video_links": [],
                "category": "Accessories",
            },
            {
                "product_name": "Silicone Lip Scrubber",
                "trend_score": 85,
                "trend_sources": ["tiktok", "amazon_us", "reddit"],
                "product_images": ["https://via.placeholder.com/400x400?text=Lip+Scrubber"],
                "video_links": [],
                "category": "Beauty",
            },
            {
                "product_name": "Portable Espresso Maker",
                "trend_score": 68,
                "trend_sources": ["amazon_us", "aliexpress"],
                "product_images": ["https://via.placeholder.com/400x400?text=Espresso"],
                "video_links": [],
                "category": "Kitchen",
            },
            {
                "product_name": "LED Nail Dryer",
                "trend_score": 75,
                "trend_sources": ["tiktok", "aliexpress"],
                "product_images": ["https://via.placeholder.com/400x400?text=Nail+Dryer"],
                "video_links": [],
                "category": "Beauty",
            },
        ]

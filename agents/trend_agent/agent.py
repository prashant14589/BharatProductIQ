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
                "external_id": "trend_portable_bladeless_neck_fan",
                "product_name": "Portable Bladeless Neck Fan",
                "trend_score": 78,
                "trend_sources": ["tiktok", "amazon_us", "aliexpress"],
                "product_images": ["https://picsum.photos/seed/neck-fan/400/400"],
                "video_links": [],
                "category": "Electronics",
            },
            {
                "external_id": "trend_magnetic_phone_grip_stand",
                "product_name": "Magnetic Phone Grip Stand",
                "trend_score": 72,
                "trend_sources": ["tiktok", "amazon_us"],
                "product_images": ["https://picsum.photos/seed/phone-grip/400/400"],
                "video_links": [],
                "category": "Accessories",
            },
            {
                "external_id": "trend_silicone_lip_scrubber",
                "product_name": "Silicone Lip Scrubber",
                "trend_score": 85,
                "trend_sources": ["tiktok", "amazon_us", "reddit"],
                "product_images": ["https://picsum.photos/seed/lip-scrubber/400/400"],
                "video_links": [],
                "category": "Beauty",
            },
            {
                "external_id": "trend_portable_espresso_maker",
                "product_name": "Portable Espresso Maker",
                "trend_score": 68,
                "trend_sources": ["amazon_us", "aliexpress"],
                "product_images": ["https://picsum.photos/seed/espresso-maker/400/400"],
                "video_links": [],
                "category": "Kitchen",
            },
            {
                "external_id": "trend_led_nail_dryer",
                "product_name": "LED Nail Dryer",
                "trend_score": 75,
                "trend_sources": ["tiktok", "aliexpress"],
                "product_images": ["https://picsum.photos/seed/nail-dryer/400/400"],
                "video_links": [],
                "category": "Beauty",
            },
        ]

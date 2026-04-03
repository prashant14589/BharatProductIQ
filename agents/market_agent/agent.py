"""Market Gap Agent - Analyzes Indian ecommerce market saturation."""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base import BaseAgent


class MarketGapAgent(BaseAgent):
    name = "market_gap"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze India market: Amazon IN, Flipkart, Meesho, D2C.
        In production: use search APIs or scraping.
        """
        product_name = context.get("product_name", "")
        category = context.get("category", "")
        # Placeholder: simulate market gap based on product name length and category
        competitor_count = self._estimate_competitors(product_name, category)
        avg_price = self._estimate_avg_price(category)
        # Demo heuristic:
        # The initial placeholder values were too pessimistic and caused every product
        # to be rejected at the scoring stage. We slightly lower the saturation
        # impact so that "real" product candidates can surface in early runs.
        saturation = min(100, int(competitor_count * 1.5))
        opportunity = max(0, 100 - saturation)
        brand_presence = "low" if saturation < 40 else "medium" if saturation < 70 else "high"
        return {
            "india_saturation_score": saturation,
            "competitor_count": competitor_count,
            "average_price_inr": avg_price,
            "brand_presence": brand_presence,
            "opportunity_score": opportunity,
            "top_competitors": [],
        }

    def _estimate_competitors(self, product_name: str, category: str) -> int:
        # Heuristic for demo; replace with real search
        # Lower base values to reflect "findable" market gaps for new product concepts.
        base = {"Electronics": 22, "Beauty": 26, "Kitchen": 18, "Accessories": 20}.get(
            category, 40
        )
        return max(5, base - len(product_name) // 6)

    def _estimate_avg_price(self, category: str) -> int:
        prices = {"Electronics": 1499, "Beauty": 699, "Kitchen": 1299, "Accessories": 899}
        return prices.get(category, 999)

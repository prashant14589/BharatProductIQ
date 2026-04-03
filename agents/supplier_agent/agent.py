"""Supplier Discovery Agent - Alibaba, AliExpress, CJ Dropshipping, 1688."""

import os
import sys
from urllib.parse import quote_plus
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base import BaseAgent

# INR per USD for conversion
USD_TO_INR = 83.0


class SupplierAgent(BaseAgent):
    name = "supplier"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Find suppliers. In production: Alibaba/AliExpress/CJ APIs or scraping.
        """
        product_name = context.get("product_name", "")
        category = context.get("category", "")
        unit_cost_usd, shipping_usd, moq, white_label = self._estimate_supplier(
            product_name, category
        )
        unit_cost_inr = round(unit_cost_usd * USD_TO_INR, 2)
        shipping_inr = round(shipping_usd * USD_TO_INR, 2)
        query = quote_plus(product_name.strip() or category.strip() or "product")

        # Demo "match confidence" based on category preference.
        # In production, this comes from item-level matching / scraping.
        category_norm = (category or "").lower()
        platform_conf = {
            "electronics": 0.86,
            "accessories": 0.78,
            "beauty": 0.82,
            "kitchen": 0.76,
        }
        default_platform_conf = 0.72
        base_conf = platform_conf.get(category_norm, default_platform_conf)

        candidates = [
            {
                "supplier_name": f"AliExpress - {product_name}",
                "platform": "aliexpress",
                "supplier_url": f"https://www.aliexpress.com/wholesale?SearchText={query}",
                "match_confidence": min(0.95, base_conf + 0.04),
            },
            {
                "supplier_name": f"Alibaba - {product_name}",
                "platform": "alibaba",
                "supplier_url": f"https://www.alibaba.com/trade/search?SearchText={query}",
                "match_confidence": min(0.95, base_conf - 0.02),
            },
            {
                "supplier_name": f"CJ Dropshipping - {product_name}",
                "platform": "cj",
                "supplier_url": f"https://app.cjdropshipping.com/search?keywords={query}",
                "match_confidence": min(0.95, base_conf - 0.06),
            },
        ]
        candidates.sort(key=lambda c: float(c.get("match_confidence") or 0), reverse=True)

        return {
            "supplier_links": [candidates[0]["supplier_url"]],
            "supplier_candidates": candidates,
            "unit_cost_usd": unit_cost_usd,
            "unit_cost_inr": unit_cost_inr,
            "shipping_cost_inr": shipping_inr,
            "moq": moq,
            "white_label_available": white_label,
            "lead_time_days": 14,
        }

    def _estimate_supplier(
        self, product_name: str, category: str
    ) -> tuple[float, float, int, bool]:
        # Heuristic; replace with real API
        base_cost = {
            "Electronics": 8.0,
            "Beauty": 3.0,
            "Kitchen": 6.0,
            "Accessories": 4.0,
        }.get(category, 5.0)
        shipping = 2.5
        moq = 10
        white_label = True
        return base_cost, shipping, moq, white_label

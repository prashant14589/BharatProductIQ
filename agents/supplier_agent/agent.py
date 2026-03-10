"""Supplier Discovery Agent - Alibaba, AliExpress, CJ Dropshipping, 1688."""

import os
import sys
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
        return {
            "supplier_links": [
                "https://www.aliexpress.com/item/example.html",
                "https://www.alibaba.com/product-detail/example.html",
            ],
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

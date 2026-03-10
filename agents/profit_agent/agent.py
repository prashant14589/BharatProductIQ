"""Profitability Agent - Total cost, suggested price, margin. Filter margin >= 40%."""

import os
import sys
from decimal import Decimal
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base import BaseAgent


class ProfitAgent(BaseAgent):
    name = "profit"

    MIN_MARGIN_PCT = 40.0
    PRICE_MIN = 799
    PRICE_MAX = 2499
    AD_COST_PER_UNIT = 175  # INR
    PLATFORM_FEE_PCT = 0.05
    GST_PCT = 0.18

    def run(self, context: dict[str, Any]) -> dict[str, Any] | None:
        """
        Calculate profitability. Return None if margin < 40% (product dropped).
        """
        unit_cost = float(context.get("unit_cost_inr", 0))
        shipping_cost = float(context.get("shipping_cost_inr", 0))
        ad_cost = context.get("estimated_ad_cost_per_unit", self.AD_COST_PER_UNIT)
        ad_cost = float(ad_cost)

        total_cost = unit_cost + shipping_cost + ad_cost
        # Add platform fee and GST on selling price
        # suggested_price * (1 - platform_fee - gst) - total_cost = margin * suggested_price
        # suggested_price = total_cost / (1 - platform_fee - gst - target_margin)
        target_margin = self.MIN_MARGIN_PCT / 100
        denominator = 1 - self.PLATFORM_FEE_PCT - self.GST_PCT - target_margin
        if denominator <= 0:
            return None
        suggested_price = total_cost / denominator
        suggested_price = round(suggested_price, 0)
        margin_pct = ((suggested_price - total_cost) / suggested_price) * 100 if suggested_price else 0
        price_in_range = self.PRICE_MIN <= suggested_price <= self.PRICE_MAX

        if margin_pct < self.MIN_MARGIN_PCT:
            return None  # Drop product

        return {
            "unit_cost_inr": unit_cost,
            "shipping_cost_inr": shipping_cost,
            "ad_cost_per_unit_inr": ad_cost,
            "total_cost_inr": round(total_cost, 2),
            "suggested_price_inr": suggested_price,
            "estimated_margin_pct": round(margin_pct, 2),
            "price_in_range": price_in_range,
        }

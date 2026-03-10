"""Product Scoring Agent - Weighted 0-100 score. Filter score < 70."""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base import BaseAgent


class ScoringAgent(BaseAgent):
    name = "scoring"
    MIN_SCORE = 70

    WEIGHTS = {
        "trend_signal": 0.25,
        "india_gap": 0.25,
        "profit_margin": 0.20,
        "visual_demo_potential": 0.20,
        "logistics_feasibility": 0.10,
    }

    def run(self, context: dict[str, Any]) -> dict[str, Any] | None:
        """
        Score 0-100. Return None if score < 70 (product dropped).
        """
        trend = min(100, int(context.get("trend_score", 0)))
        india_gap = min(100, int(context.get("opportunity_score", 0)))
        margin_pct = float(context.get("estimated_margin_pct", 0))
        margin_score = min(100, int(margin_pct))
        visual = min(100, int(context.get("visual_demo_potential", 70)))
        logistics = min(
            100,
            int(
                100
                - (context.get("moq", 100) / 10)
                - (context.get("lead_time_days", 30) / 3)
            ),
        )
        logistics = max(0, logistics)

        breakdown = {
            "trend_signal": trend,
            "india_gap": india_gap,
            "profit_margin": margin_score,
            "visual_demo_potential": visual,
            "logistics_feasibility": logistics,
        }
        total = (
            trend * self.WEIGHTS["trend_signal"]
            + india_gap * self.WEIGHTS["india_gap"]
            + margin_score * self.WEIGHTS["profit_margin"]
            + visual * self.WEIGHTS["visual_demo_potential"]
            + logistics * self.WEIGHTS["logistics_feasibility"]
        )
        total_score = int(round(total))

        if total_score < self.MIN_SCORE:
            return None

        return {
            "total_score": total_score,
            "score_breakdown": breakdown,
        }

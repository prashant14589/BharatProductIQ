"""Agent registry - central place to add/remove agents."""

from agents.trend_agent import TrendAgent
from agents.market_agent import MarketGapAgent
from agents.supplier_agent import SupplierAgent
from agents.profit_agent import ProfitAgent
from agents.scoring_agent import ScoringAgent
from agents.creative_agent import CreativeAgent
from agents.shopify_agent import ShopifyAgent

AGENTS = {
    "trend": TrendAgent(),
    "market_gap": MarketGapAgent(),
    "supplier": SupplierAgent(),
    "profit": ProfitAgent(),
    "scoring": ScoringAgent(),
    "creative": CreativeAgent(),
    "shopify": ShopifyAgent(),
}


def get_agent(name: str):
    return AGENTS.get(name)

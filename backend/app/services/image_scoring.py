"""Heuristics for estimating visual-demo potential.

In production, this should be replaced with:
- image similarity scoring (embeddings)
- category-specific aesthetic/clarity scoring
- ad-creative performance signals
"""

from __future__ import annotations

import re


_BONUS_KEYWORDS = {
    "fan",
    "nail",
    "dryer",
    "magnetic",
    "grip",
    "scrubber",
    "lip",
    "espresso",
    "maker",
    "portable",
    "led",
}


def estimate_visual_demo_potential(
    product_name: str,
    category: str | None,
    product_images: list[str] | None,
) -> int:
    images = product_images or []
    base = 55
    base += min(3, len(images)) * 12  # more images => better for demos

    text = f"{product_name} {category or ''}".lower()
    bonuses = 0
    for kw in _BONUS_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            bonuses += 1
    base += bonuses * 7

    return max(0, min(100, int(round(base))))


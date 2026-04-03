"""Text canonicalization and stable product keys.

Used to de-duplicate product concepts across multiple pipeline runs.
"""

from __future__ import annotations

import re


_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "with",
    "to",
    "of",
    "in",
    "on",
    "and",
    "best",
    "new",
    "portable",
    "wireless",
    "magnetic",
    "led",
    "ultra",
}


def normalize_text(s: str) -> str:
    s = s or ""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def canonical_product_key(product_name: str, category: str | None = None) -> str:
    """
    Create a stable key for a product concept.
    - Removes punctuation
    - Drops a small set of common non-discriminative tokens
    - Includes category to reduce collisions
    """
    name = normalize_text(product_name)
    tokens = [t for t in name.split(" ") if t and t not in _STOPWORDS]
    category_norm = normalize_text(category or "")
    category_token = category_norm.split(" ")[0] if category_norm else ""
    # Keep first N tokens for determinism
    core = "-".join(tokens[:8]) or normalize_text(product_name).replace(" ", "-")[:32]
    return f"{category_token}:{core}" if category_token else core


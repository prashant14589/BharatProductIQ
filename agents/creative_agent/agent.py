"""Creative Intelligence Agent - Ad hooks, scripts, marketing angles, Meta targeting."""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _call_ai(prompt: str, system: str = "") -> str:
    """Call OpenAI or Anthropic. Falls back to template if no API key."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return ""
    try:
        if os.getenv("ANTHROPIC_API_KEY"):
            import anthropic
            client = anthropic.Anthropic()
            m = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                system=system or "You are a marketing copywriter for Indian ecommerce.",
                messages=[{"role": "user", "content": prompt}],
            )
            return m.content[0].text if m.content else ""
        else:
            from openai import OpenAI
            client = OpenAI()
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system or "You are a marketing copywriter for Indian ecommerce."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )
            return r.choices[0].message.content or ""
    except Exception:
        return ""


from agents.base import BaseAgent


class CreativeAgent(BaseAgent):
    name = "creative"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        product_name = context.get("product_name", "")
        category = context.get("category", "")
        benefits = context.get("benefits", [])

        prompt = f"""Generate marketing creatives for this product for the Indian market:
Product: {product_name}
Category: {category}
Benefits: {benefits or 'Not specified'}

Return a JSON object with:
- ad_hooks: 3 short ad hooks (under 10 words each)
- short_form_scripts: 1 script for TikTok/Reels (15 sec, problem-solution-CTA)
- marketing_angles: 2 angles for Indian customers
- meta_targeting: interests, behaviors, age_range [18,45], locations ["India"]

Return ONLY valid JSON, no markdown."""

        raw = _call_ai(prompt)
        if raw:
            import json
            try:
                return json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
            except json.JSONDecodeError:
                pass

        # Fallback template
        return {
            "ad_hooks": [
                f"Stop overpaying for {product_name}!",
                f"This {category} hack went viral",
                f"Indians are obsessed with this {product_name}",
            ],
            "short_form_scripts": [
                {
                    "platform": "tiktok",
                    "script": f"POV: You discover {product_name} and never look back. Perfect for {category} lovers. Link in bio.",
                    "duration_seconds": 15,
                }
            ],
            "marketing_angles": [
                f"Solve [problem] with {product_name}",
                f"Indian customers love the value",
            ],
            "meta_targeting": {
                "interests": [category, "online shopping"],
                "behaviors": ["Engaged shoppers"],
                "age_range": [18, 45],
                "locations": ["India"],
            },
        }

"""Shopify Page Generator Agent - Product title, description, bullets, FAQs, upsells."""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _call_ai(prompt: str, system: str = "") -> str:
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
                system=system or "You are an ecommerce copywriter. Write concise, benefit-focused copy.",
                messages=[{"role": "user", "content": prompt}],
            )
            return m.content[0].text if m.content else ""
        else:
            from openai import OpenAI
            client = OpenAI()
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system or "You are an ecommerce copywriter."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )
            return r.choices[0].message.content or ""
    except Exception:
        return ""


from agents.base import BaseAgent


class ShopifyAgent(BaseAgent):
    name = "shopify"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        product_name = context.get("product_name", "")
        category = context.get("category", "")
        benefits = context.get("benefits", [])

        prompt = f"""Generate Shopify product page content for Indian market:
Product: {product_name}
Category: {category}
Benefits: {benefits or 'Not specified'}

Return a JSON object with:
- product_title: SEO-friendly, under 70 chars
- product_description: 2-3 paragraphs, problem-solution-benefit
- benefit_bullets: 5-7 bullet points
- faqs: 3-5 Q&A pairs
- upsell_suggestions: 2-3 related product ideas
- meta_title: under 60 chars
- meta_description: under 160 chars

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
            "product_title": f"{product_name} | Best {category} for India",
            "product_description": f"Discover {product_name} - the solution you've been looking for. Perfect for Indian customers who value quality and value. Order now and experience the difference.",
            "benefit_bullets": [
                f"Premium {product_name} design",
                f"Perfect for {category} enthusiasts",
                "Fast shipping across India",
                "30-day money-back guarantee",
                "Trusted by thousands of customers",
            ],
            "faqs": [
                {"question": "What is the delivery time?", "answer": "7-14 days across India."},
                {"question": "Is return available?", "answer": "Yes, 30-day returns."},
            ],
            "upsell_suggestions": [
                f"Premium {category} bundle",
                "Care kit for longevity",
            ],
            "meta_title": f"{product_name} | Buy Online India",
            "meta_description": f"Buy {product_name} online. Best price, fast delivery. Shop now!",
        }

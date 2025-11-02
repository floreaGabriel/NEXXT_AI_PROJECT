"""Term Explain Agent

Provides short, user-friendly explanations for selected banking terms based on:
- The selected term and its surrounding context (summary text)
- The user's education level (to adapt complexity)
- The specific product document content (products/*.md) when available

Usage:
    from src.agents.term_explain_agent import explain_term
    text = explain_term(term, summary_text, education_level, product_name, product_markdown)

The function returns a short Romanian explanation (1-2 sentences).
"""

from __future__ import annotations

import asyncio
import threading
from typing import Optional

from pydantic import BaseModel

from agents import Agent, Runner  # from openai-agents SDK
from src.config.settings import build_default_litellm_model, AWS_BEDROCK_API_KEY


class ExplainContext(BaseModel):
    term: str
    education_level: str | None = None
    product_name: str | None = None


def _education_guidance(level: Optional[str]) -> str:
    """Map UI education level to guidance for tone/detail."""
    if not level:
        return "Folosește un limbaj clar și accesibil, evită jargonul în exces."
    level = level.lower()
    if "fără" in level or "fara" in level:
        return "Explică foarte simplu, cu cuvinte uzuale, fără termeni tehnici. 1-2 propoziții maxime."
    if "liceu" in level:
        return "Explică pe scurt (1-2 propoziții), evită jargonul și formulele."
    if "facultate" in level:
        return "Explicație succintă (1-2 propoziții), poți folosi termeni uzuali din domeniul financiar."
    if "master" in level or "doctorat" in level:
        return "Explicație concisă (1-2 propoziții), poți include un termen tehnic dacă adaugă claritate."
    return "Explică pe scurt, clar, fără fraze lungi."


# Create the agent that crafts the short explanation
term_explain_agent = Agent[ExplainContext](
    name="Banking Term Explainer",
    instructions=(
        "Ești un expert în produse bancare. Primești un TERM, un CONTEXT (fragment de text), "
        "numele PRODUSULUI și conținutul documentului produsului (Markdown scurtat). "
        "SCRIE DOAR EXPLICAȚIA în limba română, scurtă (1-2 propoziții). "
        "Adaptează tonul la nivelul de înțelegere indicat. Evită markdown-ul, listele sau explicații lungi.\n\n"
        "Format: DOAR textul explicației. Fără prefixe precum 'Explicație:' și fără alte comentarii."
    ),
    model=build_default_litellm_model(),
)


async def _explain_term_async(
    term: str,
    summary_text: str,
    education_level: Optional[str],
    product_name: Optional[str],
    product_markdown: Optional[str],
) -> str:
    context = ExplainContext(term=term, education_level=education_level, product_name=product_name)
    guidance = _education_guidance(education_level)

    # Keep inputs short to reduce latency and cost
    summary_snippet = (summary_text or "")[:1200]
    product_snippet = (product_markdown or "")[:2000]

    prompt = f"""
TERM: {term}
CONTEXT (din sumar): {summary_snippet}
PRODUS: {product_name or 'n/a'}
DOCUMENT PRODUS (fragment markdown):\n{product_snippet}

CERINȚĂ: {guidance}
"""
    result = await Runner.run(term_explain_agent, prompt, max_turns=1)
    output = getattr(result, "final_output", str(result))
    # Return at most ~300 chars to ensure brevity
    return (output or "").strip()[:300]


def explain_term(
    term: str,
    summary_text: str,
    education_level: Optional[str],
    product_name: Optional[str],
    product_markdown: Optional[str],
) -> str:
    """Thread-safe sync wrapper for Streamlit.

    Always runs the coroutine in a separate thread with its own event loop
    to avoid event loop conflicts inside Streamlit.
    """
    if not AWS_BEDROCK_API_KEY:
        return "Setați AWS_BEARER_TOKEN_BEDROCK în .env pentru a genera explicația."

    result_container: list[str] = []
    exc_container: list[BaseException] = []

    def _runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            text = loop.run_until_complete(
                _explain_term_async(term, summary_text, education_level, product_name, product_markdown)
            )
            result_container.append(text)
        except BaseException as e:  # noqa: BLE001
            exc_container.append(e)
        finally:
            loop.close()

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    t.join(timeout=30)

    if t.is_alive():
        return "Explicația a depășit timpul alocat. Reîncercați."
    if exc_container:
        return f"Nu am putut genera explicația: {str(exc_container[0])[:120]}"
    return result_container[0] if result_container else "Nu am putut genera explicația."

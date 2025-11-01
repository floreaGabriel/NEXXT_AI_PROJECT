"""Bank Term Extractor Agent

Uses the OpenAI Agents SDK (via LiteLLM model) to extract bank-related terms
from arbitrary text. Returns strict JSON with categories and character spans so
UIs can both list tokens and highlight text reliably.

Expected output schema (strict):
{
  "categories": {
    "Products": ["..."],
    "Rates": ["..."],
    "Fees": ["..."]
  },
  "spans": [
    {"start": 10, "end": 22, "category": "Products", "text": "credit card"}
  ]
}

Notes:
- Spans use 0-based indices on the UTF-16/Unicode Python string.
- Spans must be non-overlapping; prefer longer phrases when ambiguous.
- Categories must exist even if empty arrays.
- Each span.text MUST exactly equal one of the items included in the corresponding category list.
"""

from typing import List, Literal

from pydantic import BaseModel
from agents import Agent, ModelSettings
from src.config.settings import build_default_litellm_model


class ExtractionCategories(BaseModel):
  """Unique tokens per category."""
  Products: List[str] = []
  Rates: List[str] = []
  Fees: List[str] = []


class ExtractionSpan(BaseModel):
  start: int
  end: int
  category: Literal["Products", "Rates", "Fees"]
  text: str


class ExtractionResult(BaseModel):
  categories: ExtractionCategories
  spans: List[ExtractionSpan]


bank_term_extractor_agent = Agent(
    name="Bank Term Extractor",
    instructions=(
    "You are a precise information extraction agent for banking text.\n"
    "Task: From the user's text, extract bank-related terms and return ONLY strict JSON.\n\n"
    "Use EXACTLY these categories (no others):\n"
    "- Products: credit card, debit card, mortgage, personal/consumer loan, overdraft, checking/current account, savings account, term/time deposit, investment funds; RO: card de credit, card de debit, credit imobiliar/ipotecar, credit de nevoi personale, descoperit de cont, cont curent, cont de economii, depozit la termen, fonduri de investiții.\n"
    "- Rates: interest rate, fixed rate, variable rate, APR, APY, annual percentage rate/yield, compound interest; RO: dobândă, rata dobânzii, rată fixă/variabilă.\n"
    "- Fees: fee, commission, maintenance fee, late fee, penalty, foreclosure penalty; RO: comision, penalități, taxă.\n\n"
    "Rules:\n"
  "1) Identify exact text spans for each detected term (non-overlapping). Prefer longer matches when overlapping.\n"
  "1a) The span's 'text' MUST be exactly one of the tokens listed in the corresponding 'categories' array (no extra words).\n"
    "2) Normalize duplicates: in 'categories' arrays, list unique terms (case-insensitive) as they appear in text.\n"
    "3) Do NOT add commentary. Do NOT include keys other than 'categories' and 'spans'.\n"
  "4) Spans MUST align to whole words and match only the term itself: do not include partial words, whitespace, punctuation, or adjacent function words (e.g., exclude trailing '.' or ',' and do not include following verbs/prepositions).\n"
    "5) Output MUST be valid JSON (no markdown fences, no trailing text).\n"
    "6) If nothing found, return empty arrays for all categories and an empty spans list.\n"
    "7) Use provided categories exactly (no extra categories).\n\n"
    "Return JSON that validates against this exact schema (examples shown):\n"
    "{\n"
    "  \"categories\": {\n"
    "    \"Products\": [\"credit card\", \"mortgage\"],\n"
    "    \"Rates\": [\"fixed rate\"],\n"
    "    \"Fees\": [\"maintenance fee\"]\n"
    "  },\n"
    "  \"spans\": [\n"
    "    {\"start\": 10, \"end\": 18, \"category\": \"Products\", \"text\": \"mortgage\"},\n"
    "    {\"start\": 28, \"end\": 38, \"category\": \"Rates\", \"text\": \"fixed rate\"}\n"
    "  ]\n"
    "}\n"
    ),
    model=build_default_litellm_model(),
    model_settings=ModelSettings(include_usage=True),
)

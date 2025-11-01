# Developer Prompt: NEXXT AI Hackathon – Raiffeisen Bank AI Solutions

You are contributing to a Streamlit-based, multi-agent banking app. Follow the standards and patterns below to keep the codebase consistent and production-ready.

## Tech Stack and Dependencies

- Python 3.10+
- Streamlit (UI)
- OpenAI Agents SDK (`openai-agents`) for multi-agent orchestration
- scikit-learn (ML utilities for simple scoring/ranking)
- pandas (data frames)
- plotly (visuals, optional)
- python-dotenv (environment configuration)

Refer to `requirements.txt` for exact versions.

## Coding Style and Conventions

- Use type hints everywhere (function params and return types)
- Add descriptive docstrings for modules, classes, and functions
- Prefer modern Python 3.10+ features (e.g., `|` unions)
- Pydantic models for context/state passed across agents
- Keep modules small and single-purpose; avoid large God objects
- Errors should surface clear, actionable messages to users via Streamlit (`st.error`, `st.warning`, etc.)

Example (function + docstring + typing):

```python
from typing import Annotated
from pydantic import BaseModel

class ExampleContext(BaseModel):
    user_id: str | None = None

def helper(value: float) -> str:
    """Return a formatted string for a numeric value."""
    return f"{value:,.2f}"
```

## Architecture and Project Structure

- Streamlit pages live in `pages/` (numbered prefix for order)
- Agents live in `src/agents/` and follow OpenAI Agents SDK patterns
- Shared UI bits in `src/components/ui_components.py`
- App settings and env in `src/config/settings.py` and `.env`
- Utilities in `src/utils/`

Agents pattern:

- Pydantic context class for agent state
- `@function_tool` functions with rich type annotations for tools
- Specialized agents for narrow tasks
- One orchestrator agent that coordinates handoffs between specialized agents

See existing mockups: `financial_analysis_agent.py`, `customer_service_agent.py`, `call_center_agent.py` and pages under `pages/`.

## UI/UX and Branding

- Use Raiffeisen palette and theme from `.streamlit/config.toml`:
  - Primary `#fee600`, text `#2b2d33`, light backgrounds
  - Font: Space Grotesk
- Apply shared styling via `apply_button_styling()` and `render_sidebar_info()`
- Streamlit layout guidelines:
  - `st.divider()` to separate sections
  - `st.container(border=True)` for card-like UI
  - `st.columns()` for responsive layouts
  - Use `type="primary"` and `use_container_width=True` on main CTAs
- Keep the interface bilingual-ready; default to Romanian product names and user-facing copy when relevant

## Core Feature: Display and Tailor Raiffeisen Products

The application must display Raiffeisen products and tailor content based on user profile. Primary product categories include (Romanian naming):

- Carduri de Cumpărături (carduri de credit pentru cumpărături)
- Depozite la Termen
- Conturi de Economii
- Card de Debit (Premium)
- Credit Imobiliar
- Credit de Nevoi Personale
- Fonduri de Investiții
- Pensie Privată (Pilon III)
- Cont Junior (pentru copii)
- Asigurare de Viață

### User Profile Inputs (minimum)

- marital_status (e.g., "necăsătorit/ă", "căsătorit/ă")
- annual_income (RON)
- age
- employment_status (e.g., "angajat", "independent", "șomer", "pensionar", "student")
- has_children (bool)
- risk_tolerance ("scăzută", "medie", "ridicată")
- financial_goals (list[str]) – e.g., economii, investiții, cumpărare casă, educație copii, pensionare

### Behavior and Ordering

- For a given profile, rank products by suitability
- The most suitable product appears first (top of page)
- Provide a short rationale or personalized note per product (why it fits)
- Show key benefits per product (bulleted list)
- Optionally show a match score or progress bar for transparency

Use a placeholder/rule-based ranking initially, but design the flow to be easily replaced by ML (e.g., scikit-learn) or agent reasoning.

## Agent Contract for Product Recommendations

Implement/extend `src/agents/product_recommendation_agent.py` with:

- Pydantic models:
  - `UserProfile` (fields above)
  - `ProductRecommendationContext` (contains `user_profile`)
- Tools (functions) with `@function_tool`:
  - `get_raiffeisen_products() -> str`: return a structured catalog of products
  - `calculate_product_score(product_id: str, user_profile: str) -> float`: return [0..1] suitability score (placeholder logic acceptable)
  - `rank_products_for_user(user_profile_json: str) -> str`: return ordered list of product IDs (CSV or JSON)
  - `generate_personalized_pitch(product_id: str, user_profile_json: str) -> str`: one-paragraph personalized pitch
- Specialized agents:
  - "Product Analyzer" – calculates scores and ranking
  - "Personalization Specialist" – crafts tailored descriptions
- Orchestrator agent:
  - "Product Recommendation Orchestrator" – coordinates the flow and returns structured recommendations

Notes:
- Current agents/pages are mockups; you may ship TODOs where backend integration is pending
- Keep tools deterministic and side-effect free; no external calls unless necessary

## Streamlit Page Pattern for Product Recommendations

Pages should:

1. Apply shared styling and sidebar (`apply_button_styling`, `render_sidebar_info`)
2. Collect user profile inputs (see fields above)
3. Validate presence of `AWS_BEARER_TOKEN_BEDROCK` (Bedrock API key) before invoking agents; otherwise, show error
4. Call the orchestrator (or use placeholder ranking) to compute ordered products
5. Render product cards in ranked order with:
   - Icon/emoji
   - Product name (Romanian)
   - Short description
   - Benefits list (3–5 bullets)
   - Match score (progress bar or percentage)
   - CTA buttons (Details / Apply)
6. Highlight the top recommendation
7. Keep data ephemeral (do not persist PII beyond session state)

See `pages/1_Product_Recommendations_Sabin.py` as a reference mockup.

## Edge Cases and Safeguards

- Missing fields: degrade gracefully with default-safe recommendations
- Extreme values (age, income): clamp or validate inputs; explain any assumptions
- Low information profiles: prefer broad, low-risk products (e.g., cont de economii, depozit la termen)
- No API key: disable agent execution and show an instructive error
- Accessibility: ensure reasonable contrast and semantics; avoid tiny font sizes

## Extending Functionality: New Agents

- New features are implemented by creating new agents in `src/agents/`
- Follow the same pattern: Pydantic context, `@function_tool` tools, specialized agents, orchestrator with handoffs
- Keep files focused (one domain per file) and export a clearly named orchestrator
- Add or update a Streamlit page in `pages/` to use the new agent; follow numbered naming convention

## Quality Gates

- Build: Streamlit app loads without syntax errors – PASS before merging
- Lint/Typecheck: Aim to keep imports resolvable and types consistent
- Tests (when applicable): lightweight tests for core scoring logic
- UX: pages render on small and large screens without layout breakage

## Security and Privacy

- Load secrets from `.env` via `python-dotenv`; never hardcode keys
- Do not log or persist sensitive user data
- Use only anonymized/aggregate data for analytics demos

## Deliverables for Any New Feature

- Agent file in `src/agents/` with context, tools, specialized agents, orchestrator
- Streamlit page in `pages/` following the standard structure and branding
- Minimal README tweak if the feature is user-facing (optional during hackathon)
- Clear TODOs where mock logic stands in for future integrations

---

This prompt serves as the single source of truth for implementation style, architecture, and the product recommendation behavior tailored by user profiles. Keep it concise, consistent, and extendable.
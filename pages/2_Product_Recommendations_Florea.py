"""Product Recommendations page - Personalized banking product recommendations.

Flow:
1. Rank products by relevance (Product Recommendation Agent)
2. Get NLP-generated base summaries (English)
3. Personalize summaries for user profile (Summary Personalization Agent)
4. Display personalized content to user
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components
import html
import unicodedata
import asyncio
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from agents import Runner
import os
from pydantic import ValidationError
import sys
from pathlib import Path
import glob
import difflib

# Make local vendored 'st-annotated-text' importable
_BASE_DIR = Path(__file__).resolve().parent.parent
_ANNOTATED_TEXT_DIR = _BASE_DIR / "st-annotated-text"
if str(_ANNOTATED_TEXT_DIR) not in sys.path:
    sys.path.insert(0, str(_ANNOTATED_TEXT_DIR))

try:
    from annotated_text import annotated_text, annotation  # type: ignore
except Exception:
    annotated_text = None  # Will guard usage later
    annotation = None

from src.config.settings import AWS_BEDROCK_API_KEY

import streamlit as st
import asyncio
import json
from agents import Runner
import nest_asyncio
import concurrent.futures

from src.config.settings import AWS_BEDROCK_API_KEY
from src.components.ui_components import render_sidebar_info, apply_button_styling
from src.agents.product_recommendation_agent import (
    UserProfile,
    rank_products_for_profile,  # Direct function for ranking
    _get_products_catalog_dict,  # Import catalog from agent
)
from src.agents.user_experience_summary_agent import (
    personalization_orchestrator,
    PersonalizationContext,
    personalize_products_batch,  # Direct function for personalization
)
from src.agents.product_title_generation_agent import product_title_agent
from src.agents.email_summary_agent import email_summary_agent
from src.agents.financial_plan_agent import generate_financial_plan, format_plan_for_display
from src.agents.pdf_converter_direct import convert_markdown_to_pdf_direct
from src.utils.db import save_financial_plan
from src.agents.product_summary_agent import product_summary_agent
from src.agents.bank_term_extractor_agent import (
    bank_term_extractor_agent,
    ExtractionResult,
)
from src.agents.term_explain_agent import explain_term
from src.agents.voice_explain_agent import explain_term_voice

"""
Feature flags for LLM-driven enrichments. Disable to avoid extra turns/latency
and rely solely on the Ranking Agent outputs (justification + recommended_action).
"""
USE_PERSONALIZATION_AGENT = True
USE_TITLE_AGENT = False

# Categories and colors for bank term highlighting
ALLOWED_CATEGORIES = ["Products", "Rates", "Fees"]
CATEGORY_COLORS: Dict[str, str] = {
    "Products": "#fcd34d",  # amber-300 (darker yellow)
    "Rates": "#fde68a",     # amber-200 (medium yellow)
    "Fees": "#fef3c7",      # amber-100 (light yellow)
}


async def run_agent_extraction(text: str) -> Optional[ExtractionResult]:
    """Call the Bank Term Extractor agent and return a validated ExtractionResult or None."""
    prompt = (
        "Extract bank-related terms from the following text. Return ONLY strict JSON with\n"
        "keys 'categories' and 'spans' as previously defined. Do not include explanations.\n\n"
        f"Text:\n{text}"
    )
    try:
        result = await Runner.run(bank_term_extractor_agent, prompt)
        raw = result.final_output or ""
        # Some LLMs might return extra text; try to isolate JSON
        try:
            data = json.loads(raw)
        except Exception:
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(raw[start : end + 1])
            else:
                return None
        # Validate into class
        try:
            return ExtractionResult.model_validate(data)
        except ValidationError:
            return None
    except Exception:
        return None
    return None


def highlight_bank_terms_html(text: str, product_id: str) -> str:
    """
    Extract bank terms from text and return HTML with highlighted terms and context menu.
    Uses the exact same logic as Bank_Term_Highlighter page.
    
    Args:
        text: The text to highlight
        product_id: Unique identifier for this product (used for unique component key)
    
    Returns:
        HTML string with highlighted terms and interactive context menu
    """
    if not text or not text.strip():
        return f"<div style='white-space:pre-wrap; line-height:1.8;'>{html.escape(text)}</div>"
    
    # Run extraction synchronously (we're already in async context from Streamlit)
    try:
        validated = asyncio.run(run_agent_extraction(text))
    except Exception:
        # If extraction fails, return plain text
        return f"<div style='white-space:pre-wrap; line-height:1.8;'>{html.escape(text)}</div>"
    
    matches: List[Tuple[int, int, str, str]] = []
    tokens_by_cat: Dict[str, set] = defaultdict(set)
    
    if validated:
        # Collect tokens from typed categories
        for cat in ALLOWED_CATEGORIES:
            for t in getattr(validated.categories, cat):
                tokens_by_cat[cat].add(t.strip())
    
    # Normalize spans to whole words (no punctuation, no partial words)
    def _is_word_char(ch: str) -> bool:
        if not ch:
            return False
        cat = unicodedata.category(ch)
        return cat.startswith("L") or cat.startswith("N") or cat.startswith("M")
    
    def _word_boundary_ok(start: int, end: int) -> bool:
        # start boundary
        if start > 0 and _is_word_char(text[start - 1]):
            return False
        # end boundary
        if end < len(text) and _is_word_char(text[end]):
            return False
        return True
    
    def _find_all_occurrences(hay: str, needle: str) -> List[Tuple[int, int]]:
        """Case-insensitive search for all occurrences with word-boundary checks."""
        res: List[Tuple[int, int]] = []
        if not needle:
            return res
        low_hay = hay.lower()
        low_need = needle.lower()
        i = 0
        while True:
            i = low_hay.find(low_need, i)
            if i == -1:
                break
            j = i + len(needle)
            if _word_boundary_ok(i, j):
                res.append((i, j))
            i = i + 1
        return res
    
    token_spans: List[Tuple[int, int, str, str]] = []
    # Prefer longer tokens to avoid partial overlaps (e.g., 'card' vs 'credit card')
    all_cat_tokens: List[Tuple[str, str]] = []  # (cat, token)
    for cat, toks in tokens_by_cat.items():
        for t in toks:
            all_cat_tokens.append((cat, t))
    all_cat_tokens.sort(key=lambda ct: -len(ct[1]))
    
    used_intervals: List[Tuple[int, int]] = []
    for cat, tok in all_cat_tokens:
        for s, e in _find_all_occurrences(text, tok):
            # Skip if overlaps an already selected interval
            if any(not (e <= us or s >= ue) for us, ue in used_intervals):
                continue
            token_spans.append((s, e, cat, text[s:e]))
            used_intervals.append((s, e))
    
    # Sort by position for rendering
    matches = sorted(token_spans, key=lambda t: t[0])
    
    # Build HTML with highlighted terms
    html_parts: List[str] = []
    term_index = 0
    last = 0
    
    for s, e, cat, seg_text in matches:
        if s > last:
            html_parts.append(html.escape(text[last:s]))
        color = CATEGORY_COLORS.get(cat, "#e5e7eb")
        # Create a clickable span with data attributes for the context menu
        html_parts.append(
            f"<span class='highlighted-term' "
            f"data-term='{html.escape(seg_text)}' "
            f"data-category='{html.escape(cat)}' "
            f"data-index='{term_index}' "
            f"style='background:{color}; padding:0.1rem 0.2rem; border-radius:0.25rem; cursor:pointer;'>"
            f"{html.escape(seg_text)}"
            f"</span>"
        )
        last = e
        term_index += 1
    
    if last < len(text):
        html_parts.append(html.escape(text[last:]))
    
    # Custom HTML with context menu using components.html
    context_menu_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                margin: 0;
                padding: 12px;
                background: #e0f2fe;
                border-radius: 8px;
            }}
            .context-menu {{
                display: none;
                position: fixed;
                background: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                padding: 8px 0;
                min-width: 200px;
            }}
            .context-menu.active {{
                display: block;
            }}
            .context-menu-item {{
                padding: 10px 20px;
                cursor: pointer;
                transition: background 0.2s;
                border-bottom: 1px solid #f0f0f0;
            }}
            .context-menu-item:last-child {{
                border-bottom: none;
            }}
            .context-menu-item:hover {{
                background: #f5f5f5;
            }}
            .context-menu-header {{
                padding: 8px 20px;
                font-weight: bold;
                color: #666;
                border-bottom: 2px solid #e0e0e0;
                margin-bottom: 4px;
                font-size: 0.9em;
            }}
            .highlighted-term {{
                cursor: pointer;
                transition: opacity 0.2s;
            }}
            .highlighted-term:hover {{
                opacity: 0.8;
            }}
            #highlightedText {{
                white-space: pre-wrap;
                line-height: 1.8;
                color: #1e3a8a;
            }}
        </style>
    </head>
    <body>
        <div id="contextMenu" class="context-menu">
            <div class="context-menu-header" id="menuHeader">Term Options</div>
            <div class="context-menu-item" onclick="handleMenuAction('explain')">
                💡 Explain
            </div>
            <div class="context-menu-item" onclick="handleMenuAction('voice')">
                🔊 Voice Explain
            </div>
        </div>
        
        <div id="highlightedText">
            {"".join(html_parts)}
        </div>
        
        <script>
            (function() {{
                const contextMenu = document.getElementById('contextMenu');
                const menuHeader = document.getElementById('menuHeader');
                let currentTerm = null;
                let currentCategory = null;
                
                // Add event listeners to all highlighted terms
                document.querySelectorAll('.highlighted-term').forEach(term => {{
                    term.addEventListener('contextmenu', function(e) {{
                        e.preventDefault();
                        
                        currentTerm = this.getAttribute('data-term');
                        currentCategory = this.getAttribute('data-category');
                        
                        // Update menu header
                        menuHeader.textContent = currentTerm + ' (' + currentCategory + ')';
                        
                        // Position the menu
                        contextMenu.style.left = e.pageX + 'px';
                        contextMenu.style.top = e.pageY + 'px';
                        contextMenu.classList.add('active');
                    }});
                }});
                
                // Close menu when clicking elsewhere
                document.addEventListener('click', function(e) {{
                    if (!contextMenu.contains(e.target)) {{
                        contextMenu.classList.remove('active');
                    }}
                }});
                
                // Handle menu actions
                window.handleMenuAction = function(action) {{
                    if (!currentTerm) return;
                    
                    // Send message to Streamlit parent
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        key: 'bank_term_action_{product_id}',
                        value: {{
                            action: action,
                            term: currentTerm,
                            category: currentCategory,
                            timestamp: Date.now()
                        }}
                    }}, '*');
                    
                    // Close menu
                    contextMenu.classList.remove('active');
                    
                    // Visual feedback
                    alert(action.charAt(0).toUpperCase() + action.slice(1) + ' action for: ' + currentTerm);
                }};
            }})();
        </script>
    </body>
    </html>
    """
    
    return context_menu_html


def _extract_tokens_with_positions(text: str) -> tuple[list[tuple[int, int, str, str]], dict[str, set[str]]]:
    """Use the bank_term_extractor_agent to get tokens and find their spans in text.

    Returns a tuple of (matches, tokens_by_cat)
    - matches: list of (start, end, category, matched_text)
    - tokens_by_cat: mapping category -> set(tokens)
    """
    if not text or not text.strip():
        return [], {}

    # Run extraction synchronously and defensively
    try:
        validated = asyncio.run(run_agent_extraction(text))
    except Exception:
        validated = None

    tokens_by_cat: Dict[str, set] = defaultdict(set)
    if validated:
        for cat in ALLOWED_CATEGORIES:
            for t in getattr(validated.categories, cat):
                tt = (t or "").strip()
                if tt:
                    tokens_by_cat[cat].add(tt)

    def _is_word_char(ch: str) -> bool:
        if not ch:
            return False
        cat = unicodedata.category(ch)
        return cat.startswith("L") or cat.startswith("N") or cat.startswith("M")

    def _word_boundary_ok(start: int, end: int) -> bool:
        if start > 0 and _is_word_char(text[start - 1]):
            return False
        if end < len(text) and _is_word_char(text[end]):
            return False
        return True

    def _find_all_occurrences(hay: str, needle: str) -> list[tuple[int, int]]:
        res: list[tuple[int, int]] = []
        if not needle:
            return res
        low_hay = hay.lower()
        low_need = needle.lower()
        i = 0
        while True:
            i = low_hay.find(low_need, i)
            if i == -1:
                break
            j = i + len(needle)
            if _word_boundary_ok(i, j):
                res.append((i, j))
            i += 1
        return res

    # Build prioritized list of tokens (longer first)
    all_cat_tokens: list[tuple[str, str]] = []
    for cat, toks in tokens_by_cat.items():
        for t in toks:
            all_cat_tokens.append((cat, t))
    all_cat_tokens.sort(key=lambda ct: -len(ct[1]))

    used: list[tuple[int, int]] = []
    matches: list[tuple[int, int, str, str]] = []
    for cat, tok in all_cat_tokens:
        for s, e in _find_all_occurrences(text, tok):
            if any(not (e <= us or s >= ue) for us, ue in used):
                continue
            matches.append((s, e, cat, text[s:e]))
            used.append((s, e))

    matches.sort(key=lambda t: t[0])
    return matches, tokens_by_cat


def render_annotated_summary(text: str) -> list[tuple[str, str]]:
    """Render the summary using st-annotated-text and return list of (term, category).

    If st-annotated-text is not available, fall back to plain text.
    """
    if not text:
        st.write("")
        return []

    matches, _ = _extract_tokens_with_positions(text)

    # Build pieces: plain strings and (body, label, background)
    pieces: list = []
    last = 0
    terms: list[tuple[str, str]] = []
    for s, e, cat, seg in matches:
        if s > last:
            pieces.append(text[last:s])
        bg = CATEGORY_COLORS.get(cat, "#e5e7eb")
        pieces.append((seg, cat, bg))
        terms.append((seg, cat))
        last = e
    if last < len(text):
        pieces.append(text[last:])

    if annotated_text:
        annotated_text(*pieces)
    else:
        # Fallback: simple markdown
        st.markdown(f"<div style='white-space:pre-wrap'>{html.escape(text)}</div>", unsafe_allow_html=True)

    # Deduplicate terms while preserving order
    seen = set()
    uniq_terms: list[tuple[str, str]] = []
    for t, c in terms:
        key = (t.lower(), "")
        if key not in seen:
            seen.add(key)
            uniq_terms.append((t, ""))
    return uniq_terms


def _load_product_markdown(product_name: str) -> str:
    """Best-effort load of product markdown from products/ directory using fuzzy match."""
    try:
        product_dir = (_BASE_DIR / "products").resolve()
        files = list(product_dir.glob("*.md"))
        if not files:
            return ""
        # Score by difflib ratio on stem and full name
        def score(p: Path) -> float:
            stem = p.stem.replace("_", " ")
            return max(
                difflib.SequenceMatcher(None, product_name.lower(), stem.lower()).ratio(),
                difflib.SequenceMatcher(None, product_name.lower(), p.name.lower()).ratio(),
            )
        best = max(files, key=score)
        # Only accept if similarity is decent
        if score(best) < 0.4:
            return ""
        return best.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

apply_button_styling()
render_sidebar_info()

st.title("🎯 Recomandări Personalizate de Produse")

# Top auth nav (from Sabin page)
nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/0_Login.py")
with nav_col2:
    if st.button("Register", use_container_width=True):
        st.switch_page("pages/1_Register.py")
with nav_col3:
    if st.session_state.get("auth", {}).get("logged_in"):
        email = st.session_state["auth"]["email"]
        if st.button("Logout", use_container_width=True):
            st.session_state.pop("auth", None)
            st.session_state.pop("user_profile", None)
            st.rerun()
        st.caption(f"Autentificat ca: {email}")

# Require authentication to proceed further
if not st.session_state.get("auth", {}).get("logged_in"):
    st.warning("Pentru a accesa recomandările personalizate și a primi sumarul pe email, vă rugăm să vă autentificați sau să vă înregistrați.")
    link_col1, link_col2 = st.columns(2)
    with link_col1:
        if st.button("→ Autentificare", use_container_width=True):
            st.switch_page("pages/0_Login.py")
    with link_col2:
        if st.button("→ Înregistrare", use_container_width=True):
            st.switch_page("pages/1_Register.py")
    st.stop()

st.write(
    """
    Primiți recomandări personalizate de produse bancare bazate pe profilul dumneavoastră.
    Produsele sunt ordonate în funcție de relevanță pentru situația dumneavoastră financiară.
    """
)

st.divider()


st.divider()

# User Profile Input Section

# User Profile Input Section
st.subheader("📋 Profilul Dumneavoastră")

# Defaults from session (if logged in)
user_defaults = st.session_state.get("user_profile", {})
def _get_default(opt_list, value, fallback):
    return value if isinstance(value, str) and value in opt_list else fallback

col1, col2 = st.columns(2)

with col1:
    marital_options = ["Necăsătorit/ă", "Căsătorit/ă", "Divorțat/ă", "Văduv/ă"]
    marital_status = st.selectbox(
        "Status Marital",
        marital_options,
        index=marital_options.index(_get_default(marital_options, user_defaults.get("marital_status"), marital_options[0])) if user_defaults.get("marital_status") in marital_options else 0,
        help="Statusul dumneavoastră marital actual"
    )
    
    annual_income = st.number_input(
        "Venit Anual (RON)",
        min_value=0,
        max_value=1000000,
        value=int(user_defaults.get("annual_income", 50000)),
        step=5000,
        help="Venitul anual brut în RON"
    )
    
    age = st.number_input(
        "Vârstă",
        min_value=18,
        max_value=100,
        value=int(user_defaults.get("age", 35)),
        help="Vârsta dumneavoastră în ani"
    )
    
    has_children = st.checkbox(
        "Am copii",
        value=bool(user_defaults.get("has_children", False)),
        help="Bifați dacă aveți copii"
    )
    
    education_options = ["Fără studii superioare", "Liceu", "Facultate", "Master", "Doctorat"]
    education_level = st.selectbox(
        "Nivel Studii",
        education_options,
        index=education_options.index(_get_default(education_options, user_defaults.get("education_level"), education_options[2])) if user_defaults.get("education_level") in education_options else 2,
        help="Cel mai înalt nivel de educație finalizat"
    )
    # Persist selected education level for sidebar explanations
    st.session_state["selected_education_level"] = education_level

with col2:
    employment_options = ["Angajat", "Independent", "Șomer", "Pensionar", "Student"]
    employment_status = st.selectbox(
        "Status Profesional",
        employment_options,
        index=employment_options.index(_get_default(employment_options, user_defaults.get("employment_status"), employment_options[0])) if user_defaults.get("employment_status") in employment_options else 0,
        help="Situația dumneavoastră profesională actuală"
    )
    
    risk_tolerance = st.select_slider(
        "Toleranță la Risc",
        options=["Scăzută", "Medie", "Ridicată"],
        value=_get_default(["Scăzută", "Medie", "Ridicată"], user_defaults.get("risk_tolerance"), "Medie"),
        help="Cât de confortabil sunteți cu riscul financiar"
    )
    
    financial_goals = st.multiselect(
        "Obiective Financiare",
        [
            "Economii pe termen scurt",
            "Economii pe termen lung", 
            "Investiții",
            "Cumpărare casă",
            "Educație copii",
            "Pensionare",
            "Călătorii",
            "Achiziții mari"
        ],
        default=user_defaults.get("financial_goals", ["Economii pe termen lung"]),
        help="Selectați obiectivele dumneavoastră financiare principale"
    )

st.divider()

# Initialize session state variables
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = []
if 'ranked_products' not in st.session_state:
    st.session_state.ranked_products = None
if 'llm_titles' not in st.session_state:
    st.session_state.llm_titles = {}
if 'user_profile_data' not in st.session_state:
    st.session_state.user_profile_data = None
if 'selected_term' not in st.session_state:
    st.session_state.selected_term = None
if 'selected_term_meta' not in st.session_state:
    st.session_state.selected_term_meta = {}
if 'term_explanation' not in st.session_state:
    st.session_state.term_explanation = None
if 'term_explanation_audio' not in st.session_state:
    st.session_state.term_explanation_audio = None

# Get Recommendations Button
if st.button("🔍 Obține Recomandări", type="primary", use_container_width=True):
    if not AWS_BEDROCK_API_KEY:
        st.error("Vă rugăm configurați cheia API Bedrock (AWS_BEARER_TOKEN_BEDROCK) în fișierul .env")
    else:

        with st.spinner("Analizăm profilul și generăm recomandări personalizate prin AI..."):
            try:
                # Create user profile
                # TODO: In production, fetch user data from database based on user_id
                user_profile = UserProfile(
                    marital_status=marital_status.lower(),
                    annual_income=float(annual_income),
                    age=age,
                    employment_status=employment_status.lower(),
                    has_children=has_children,
                    risk_tolerance=risk_tolerance.lower(),
                    financial_goals=[goal.lower() for goal in financial_goals],
                    education_level=education_level.lower(),
                )
                
                # STEP 1: Product Recommendation Agent - Rank products by relevance score
                # Uses deterministic rule-based scoring (TODO: replace with ML model)
                ranked_products = rank_products_for_profile(user_profile.model_dump_json())
                
                # STEP 2: Get product catalog from agent and prepare for personalization
                # Using product description as input (not pre-generated summary)
                product_catalog = _get_products_catalog_dict()
                products_with_descriptions = []
                for product in ranked_products:
                    pid = product["product_id"]
                    base_data = product_catalog.get(pid, {})
                    
                    products_with_descriptions.append({
                        "product_id": pid,
                        "name": base_data.get("name", pid),
                        "description": base_data.get("description", ""),
                        "benefits": base_data.get("benefits", []),
                        "score": product.get("score", 0.5),
                        # carry over AI justification to use as default summary when skipping LLM
                        "justification": product.get("justification", ""),
                        "recommended_action": product.get("recommended_action", ""),
                    })
                
                # Store a minimal base list in session BEFORE any LLM personalization
                # so the UI always renders even if later steps fail
                base_products_for_ui: list[tuple[str, dict]] = []
                for p in products_with_descriptions:
                    base_products_for_ui.append(
                        (
                            p["product_id"],
                            {
                                "name": p.get("name") or p["product_id"],
                                "icon": "🏦",  # default icon; refined later
                                "description": p.get("description", ""),
                                "benefits": p.get("benefits", []),
                                "score": p["score"],
                                "base_summary": p.get("description", ""),
                                "personalized_summary": "",
                            },
                        )
                    )
                st.session_state.ranked_products = base_products_for_ui
                st.session_state.llm_titles = {}
                st.session_state.user_profile_data = {
                    "age": age,
                    "annual_income": annual_income,
                    "marital_status": marital_status,
                }
                
                # STEP 3: Summary Personalization Agent (optional)
                if USE_PERSONALIZATION_AGENT:
                    # Uses Bedrock LLM to adapt base summaries to user's specific situation
                    nest_asyncio.apply()

                    context = PersonalizationContext(user_profile=user_profile)

                    async def run_personalization_agent():
                        # Prepare concise product payload
                        payload = [
                            {
                                "product_id": p["product_id"],
                                "name": p["name"],
                                "description": p["description"],
                                "benefits": p.get("benefits", []),
                                "score": p.get("score", 0.5),
                            }
                            for p in products_with_descriptions
                        ]

                        # One-shot prompt for single-turn agent
                        prompt = (
                            "Context utilizator (JSON): "
                            + user_profile.model_dump_json(ensure_ascii=False)
                            + "\n\nProduse (JSON): "
                            + json.dumps(payload, ensure_ascii=False)
                            + "\n\nSarcină: Pentru fiecare produs, redactează un sumar scurt în română, product-first, cu o adaptare discretă la profil.\n"
                            + "Structură: (1) Prezentare produs, (2) Potrivire pentru profil, (3) Recomandare concretă sau beneficiu principal.\n"
                            + "Lungime: 3–4 propoziții, max 450 caractere, fără emoji-uri.\n\n"
                            + "Returnează STRICT JSON: {\\\"summaries\\\": [{\\\"product_id\\\": \\\"...\\\", \\\"personalized_summary\\\": \\\"...\\\"}]}"
                        )

                        return await Runner.run(product_summary_agent, prompt, max_turns=1)

                    # Execute personalization agent safely so failures don't block UI
                    try:
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, run_personalization_agent())
                            agent_result = future.result()

                        # Parse LLM output
                        agent_output = agent_result.output if hasattr(agent_result, 'output') else str(agent_result)

                        try:
                            import re
                            # Extract JSON array from LLM response
                            json_match = re.search(r'\[.*?\]', agent_output, re.DOTALL)
                            if json_match:
                                personalized_summaries = json.loads(json_match.group())

                                # Merge personalized summaries back into products
                                summary_map = {item["product_id"]: item["personalized_summary"] for item in personalized_summaries}

                                for product in products_with_descriptions:
                                    product["personalized_summary"] = summary_map.get(
                                        product["product_id"],
                                        f"{product['description']}"  # Fallback to description if LLM didn't personalize
                                    )
                            else:
                                st.warning("⚠️ LLM nu a returnat JSON valid. Folosim descrierile standard.")
                                for product in products_with_descriptions:
                                    product["personalized_summary"] = product["description"]

                        except Exception as e:
                            st.warning(f"⚠️ Eroare parsare răspuns LLM: {e}. Folosim descrierile standard.")
                            for product in products_with_descriptions:
                                product["personalized_summary"] = product["description"]
                    except Exception as e:
                        st.warning(f"⚠️ Personalizarea a eșuat: {e}. Folosim descrierile standard.")
                        for product in products_with_descriptions:
                            product["personalized_summary"] = product["description"]
                else:
                    # Build a concise, actionable Romanian summary focused on product presentation
                    def _first_sentence(text: str) -> str:
                        if not isinstance(text, str) or not text:
                            return ""
                        # Split on sentence enders and return first non-empty
                        import re
                        parts = re.split(r"(?<=[\.!?])\s+", text.strip())
                        return parts[0].strip() if parts else text.strip()

                    def _safe_int(x, default=0):
                        try:
                            return int(x)
                        except Exception:
                            return default

                    # Prepare simple profile signals for templating
                    profile_age = _safe_int(age, 0)
                    profile_income = float(annual_income) if isinstance(annual_income, (int, float)) else 0.0
                    profile_risk = (risk_tolerance or "").lower()
                    goals_lower = [g.lower() for g in (financial_goals or [])]

                    def _why_fit_clause():
                        reasons = []
                        if profile_age and profile_age <= 25:
                            reasons.append("vârsta tânără îți permite să construiești pe termen lung")
                        elif profile_age and profile_age >= 45:
                            reasons.append("prioritatea este siguranța și planificarea pe termen mediu-lung")
                        if "investiții" in goals_lower:
                            reasons.append("obiectivul de investiții se potrivește cu structura produsului")
                        if "economii pe termen lung" in goals_lower or "economii pe termen scurt" in goals_lower:
                            reasons.append("sprijină disciplina de economisire")
                        if profile_risk in ("scăzută", "scazuta"):
                            reasons.append("potrivit pentru risc scăzut")
                        elif profile_risk == "medie":
                            reasons.append("echilibru între siguranță și randament")
                        elif profile_risk == "ridicată" or profile_risk == "ridicata":
                            reasons.append("permite potențial de creștere mai mare, cu volatilitate")
                        return ", ".join(reasons) if reasons else "se potrivește profilului tău financiar"

                    def _recommended_amount():
                        # Heuristic: ~10% din venitul lunar, rotunjit la 50 RON
                        if profile_income and profile_income > 0:
                            monthly = profile_income / 12.0
                            base = max(100, min(1000, int((monthly * 0.1) // 50 * 50)))
                            return base
                        return 300

                    for product in products_with_descriptions:
                        name = product.get("name") or product.get("product_id", "Produs bancar")
                        desc_first = _first_sentence(product.get("description", "").strip())
                        just = (product.get("justification") or "").strip()
                        action = (product.get("recommended_action") or "").strip()

                        why = _why_fit_clause()
                        amount = _recommended_amount()

                        # Prefer provided action if present; otherwise craft one
                        if not action:
                            action = f"Începe cu {amount} RON/lună și ajustează după 2-3 luni în funcție de confortul tău."

                        # Final Romanian, product-first summary (max ~4 sentences)
                        summary_ro = (
                            f"Prezentare produs: {name} — {desc_first}. "
                            f"De ce ți se potrivește: {why}. "
                            f"Recomandare concretă: {action} "
                        )

                        product["personalized_summary"] = summary_ro.strip()
                
                enriched_products = products_with_descriptions

                # STEP 3.5: Optional title generation via LLM
                llm_titles: dict[str, str] = {}
                if USE_TITLE_AGENT:
                    # Build payload from enriched products
                    products_payload = [
                        {
                            "product_id": p["product_id"],
                            "name": p.get("name") or p["product_id"],
                            "description": p.get("description", ""),
                            "benefits": p.get("benefits", []),
                        }
                        for p in enriched_products
                    ]

                    try:
                        async def _run_titles():
                            prompt = (
                                "Context utilizator (JSON): "
                                + user_profile.model_dump_json(ensure_ascii=False)
                                + "\n\n"
                                "Produse existente (JSON): "
                                + json.dumps(products_payload, ensure_ascii=False)
                                + "\n\n"
                                "Sarcină: Generează pentru fiecare produs un titlu personalizat, concis și captivant,\n"
                                "în limba română, potrivit profilului de mai sus. Respectă regulile din instrucțiunile agentului\n"
                                "și NU folosi emoji-uri în titluri.\n\n"
                                "Returnează STRICT JSON cu schema: {\n"
                                "  \"titles\": [\n"
                                "    {\"product_id\": \"<id>\", \"title\": \"<titlu personalizat>\"}\n"
                                "  ]\n"
                                "} (fără text suplimentar)."
                            )

                            return await Runner.run(product_title_agent, prompt, max_turns=3)

                        titles_result = asyncio.run(_run_titles())
                        raw = titles_result.final_output or "{}"
                        parsed = {}
                        try:
                            parsed = json.loads(raw)
                        except Exception:
                            start = raw.find("{")
                            end = raw.rfind("}")
                            if start != -1 and end != -1 and end > start:
                                parsed = json.loads(raw[start : end + 1])
                        for item in parsed.get("titles", []) if isinstance(parsed, dict) else []:
                            pid = item.get("product_id")
                            title = item.get("title")
                            if isinstance(pid, str) and isinstance(title, str):
                                llm_titles[pid] = title.strip()
                    except Exception as llm_err:
                        st.warning(f"Nu am putut genera titluri personalizate (LLM): {llm_err}")

                # Prepare UI data: add icons and format for display
                ICONS = {
                    "card_cumparaturi_rate": "💳",
                    "depozite_termen": "🏦",
                    "cont_economii_super_acces": "💰",
                    "card_debit_platinum": "🪪",
                    "credit_ipotecar_casa_ta": "🏠",
                    "credit_nevoi_personale": "🧾",
                    "fonduri_investitii_smartinvest": "📈",
                    "pensie_privata_pilon3": "🎯",
                    "cont_junior_adolescenti": "🧒",
                    "asigurare_viata_economii": "🛡️",
                }

                # Format for UI
                products_for_ui = []
                for enriched_product in enriched_products:
                    pid = enriched_product["product_id"]
                    icon = ICONS.get(pid, "🏦")
                    
                    products_for_ui.append(
                        (
                            pid,
                            {
                                "name": enriched_product.get("name", pid),
                                "icon": icon,
                                "description": enriched_product.get("description", ""),
                                "benefits": enriched_product.get("benefits", []),
                                "score": enriched_product["score"],
                                "base_summary": enriched_product.get("base_summary", ""),
                                "personalized_summary": enriched_product.get("personalized_summary", ""),
                            },
                        )
                    )
                
                # Already sorted by Product Recommendation Agent (no need to re-sort)
                ranked_products = products_for_ui
                
                # Store in session state to persist across reruns
                st.session_state.ranked_products = ranked_products
                st.session_state.llm_titles = llm_titles
                # user_profile_data already stored earlier
                
                # Display results
                st.success("✅ Recomandări generate cu succes!")
                
            except Exception as e:
                st.error(f"A apărut o eroare: {str(e)}")

# Display products (outside the button block so they persist)
if st.session_state.ranked_products is not None:
    st.divider()
    st.subheader("📊 Produsele Recomandate pentru Dumneavoastră")
    
    # Display match score
    profile_data = st.session_state.user_profile_data
    st.info(f"📈 Bazat pe profilul dumneavoastră: {profile_data['age']} ani, venit anual {profile_data['annual_income']:,.0f} RON, {profile_data['marital_status'].lower()}")
    
    ranked_products = st.session_state.ranked_products
    llm_titles = st.session_state.llm_titles

    # Display products in ranked order
    for idx, (product_id, product) in enumerate(ranked_products, 1):
        with st.container(border=True):
            # Product header with selection button
            col_icon, col_title, col_select = st.columns([1, 9, 2])
            with col_icon:
                st.markdown(f"## {product['icon']}")
            with col_title:
                # Prefer personalized Romanian title when available
                display_name = llm_titles.get(product_id, product['name'])
                st.markdown(f"### {idx}. {display_name}")
                # Match percentage
                match_percent = int(product['score'] * 100)
                st.progress(product['score'])
                st.caption(f"Potrivire: {match_percent}%")
            with col_select:
                # Check if product is already selected
                is_selected = product_id in st.session_state.selected_products
                
                # Selection button
                if is_selected:
                    if st.button("✅ Selectat", key=f"select_{product_id}", type="secondary", use_container_width=True):
                        st.session_state.selected_products.remove(product_id)
                        st.rerun()
                else:
                    if st.button("➕ Selectează", key=f"select_{product_id}", type="primary", use_container_width=True):
                        st.session_state.selected_products.append(product_id)
                        st.rerun()
            

            # Personalized Romanian recommendation (AI-generated based on user profile)
            summary_text = product.get("personalized_summary") or product.get("base_summary") or product.get("description", "")
            if summary_text:
                st.markdown("**💡 Recomandare Personalizată:**")
                # Render summary with st-annotated-text and capture candidate terms
                with st.container():
                    terms = render_annotated_summary(summary_text)
                    if terms:
                        # Let user choose a highlighted term to explain
                        term_labels = [f"{t} ({c})" for t, c in terms]
                        default_idx = 0
                        selected_label = st.selectbox(
                            "Selectează un termen pentru explicații",
                            options=["— Niciun termen —"] + term_labels,
                            index=0,
                            key=f"term_select_{product_id}",
                            help="Alege un termen evidențiat din text pentru a vedea explicația în panoul lateral.",
                        )
                        if selected_label != "— Niciun termen —":
                            sel_idx = term_labels.index(selected_label)
                            sel_term, sel_cat = terms[sel_idx]
                            # Persist selection globally for the sidebar actions
                            st.session_state.selected_term = sel_term
                            st.session_state.selected_term_meta = {
                                "category": sel_cat,
                                "product_id": product_id,
                                "product_name": display_name,
                                "summary_text": summary_text,
                            }
                    else:
                        st.caption("Nu au fost identificate termeni bancari de explicat în acest text.")
            
            # Personalized note for top recommendation
            if idx == 1:
                st.success("⭐ **Recomandarea Noastră Principală** - Acest produs se potrivește cel mai bine profilului dumneavoastră!")
    
    # Email Summary Section
    st.divider()
    st.subheader("✉️ Primește sumarul pe email")
    
    st.info("📧 Emailul va fi trimis la adresa ta de autentificare. Verifică și folder-ul Spam dacă nu îl găsești în Inbox.")

    if st.button("Trimite-mi summary-ul pe email", type="primary", use_container_width=True):
        user_email = st.session_state.get("auth", {}).get("email")
        if not user_email:
            st.error("Autentificați-vă pentru a trimite sumarul pe email.")
        elif not AWS_BEDROCK_API_KEY:
            st.error("Configurați cheia Bedrock în .env (AWS_BEARER_TOKEN_BEDROCK).")
        else:
            # Check if SMTP is configured
            import os
            smtp_host = os.getenv("SMTP_HOST")
            if not smtp_host:
                st.error(
                    "⚠️ **SMTP nu este configurat!**\n\n"
                    "Pentru a trimite emailuri, configurează următoarele variabile în fișierul `.env`:\n"
                    "- `SMTP_HOST` (ex: smtp.gmail.com)\n"
                    "- `SMTP_PORT` (ex: 587)\n"
                    "- `SMTP_USER` (emailul tău)\n"
                    "- `SMTP_PASSWORD` (App Password pentru Gmail)\n\n"
                    "📖 Consultă ghidul complet: `EMAIL_SETUP_GUIDE.md`"
                )
            else:
                # Create an expander for detailed logs
                log_expander = st.expander("📋 Detalii Trimitere Email (Click pentru logs)", expanded=False)
                
                with st.spinner("Generăm emailul HTML și îl trimitem..."):
                    try:
                        # Display SMTP configuration (masked password)
                        with log_expander:
                            st.write("**🔧 Configurație SMTP:**")
                            smtp_host = os.getenv("SMTP_HOST", "NU SETAT")
                            smtp_port = os.getenv("SMTP_PORT", "NU SETAT")
                            smtp_user = os.getenv("SMTP_USER", "NU SETAT")
                            smtp_pass = os.getenv("SMTP_PASSWORD", "")
                            from_email = os.getenv("FROM_EMAIL", smtp_user)
                            
                            st.code(f"""
SMTP_HOST: {smtp_host}
SMTP_PORT: {smtp_port}
SMTP_USER: {smtp_user}
SMTP_PASSWORD: {'*' * len(smtp_pass) if smtp_pass else 'NU SETAT'} ({len(smtp_pass)} caractere)
FROM_EMAIL: {from_email}
                            """)
                            
                            st.write(f"**📧 Destinatar:** {user_email}")
                            st.write("**🎨 Generare email HTML profesional Raiffeisen...**")
                        
                        # Build summary content in Markdown format
                        with log_expander:
                            st.write("**📝 Construire conținut recomandări...**")
                        
                        # Get user profile data
                        user_profile_data = st.session_state.get("user_profile_data", {})
                        age = user_profile_data.get("age", 35)
                        annual_income = user_profile_data.get("annual_income", 50000)
                        marital_status = user_profile_data.get("marital_status", "necăsătorit/ă")
                        
                        # Build Markdown content with top products
                        markdown_content = f"""# Recomandările Dumneavoastră Personalizate

**Data:** {asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else '02 Noiembrie 2025'}  
**Consultant:** Raiffeisen Banking & Advisory

---

## Rezumat Profil

Am analizat profilul dumneavoastră financiar și am identificat produsele cele mai potrivite pentru situația și obiectivele dumneavoastră.

**Profilul dumneavoastră:**
- Vârstă: {age} ani
- Venit anual: {annual_income:,.0f} RON ({annual_income/12:,.0f} RON/lună)
- Status: {marital_status}

---

## Produse Recomandate

"""
                        
                        # Add top 5 products
                        top_count = min(5, len(ranked_products))
                        for idx, (pid, prod) in enumerate(ranked_products[:top_count], 1):
                            product_name = llm_titles.get(pid, prod.get("name", pid))
                            summary = prod.get("personalized_summary", "")
                            score = int(prod.get("score", 0) * 100)
                            
                            markdown_content += f"""### {idx}. {product_name}

**Potrivire:** {score}% compatibil cu profilul dumneavoastră

{summary}

---

"""
                        
                        # Add call to action
                        markdown_content += """## Pași Următori

Pentru a accesa aceste produse și a discuta detaliile:

1. Programați o consultanță gratuită cu un specialist Raiffeisen
2. Pregătiți documentele necesare (CI, adeverință venit)
3. Contactați-ne la numărul *2000 (gratuit)

---

*Recomandări generate de NEXXT AI Banking Assistant*  
*Pentru consultanță personalizată, contactați echipa Raiffeisen Banking & Advisory*
"""
                        
                        with log_expander:
                            st.write(f"**✅ Conținut Markdown generat:** {len(markdown_content)} caractere")
                            st.write("**� Conversie Markdown → HTML Raiffeisen...**")
                        
                        # Convert to HTML with Raiffeisen design
                        from src.utils.html_converter import convert_financial_plan_to_html, clean_markdown_for_email
                        
                        # Get user name if available from session
                        user_name = st.session_state.get("auth", {}).get("email", "").split("@")[0].title()
                        
                        cleaned_md = clean_markdown_for_email(markdown_content)
                        html_content = convert_financial_plan_to_html(
                            cleaned_md,
                            client_name=user_name if user_name else None,
                            client_age=age,
                            client_income=annual_income
                        )
                        
                        with log_expander:
                            st.write(f"**✅ HTML generat:** {len(html_content)} caractere")
                            st.write(f"**🎨 Design:** Raiffeisen Bank (Galben #FFED00 & Alb)")
                            st.write("**📤 Trimitere email HTML...**")

                        subject = "Recomandările Dumneavoastră Personalizate - Raiffeisen Bank"

                        async def _send():
                            """Trimite email HTML folosind MCP Email Server."""
                            from agents.mcp import MCPServerStdio
                            from src.utils.mcp_email_client import get_mcp_email_server_config
                            from src.config.settings import build_default_litellm_model
                            from agents import Agent, ModelSettings
                            from src.agents.html_email_agent import html_email_agent
                            
                            # Creează și conectează MCP serverul
                            mcp_server = MCPServerStdio(get_mcp_email_server_config())
                            await mcp_server.connect()
                            
                            # Configurează agentul HTML cu MCP server
                            html_email_agent.mcp_servers = [mcp_server]
                            html_email_agent.model = build_default_litellm_model()
                            html_email_agent.model_settings = ModelSettings(include_usage=True)
                            
                            # Prompt pentru agent
                            prompt = f"""Send an HTML email with the following details:

RECIPIENT: {user_email}
SUBJECT: {subject}

HTML BODY (complete HTML document with Raiffeisen branding):
{html_content}

CRITICAL INSTRUCTIONS:
- Use send_email tool
- Set html parameter to boolean true (not string, actual boolean)
- This enables HTML rendering in the email client
- Send immediately without modifying the HTML

Please send this professional HTML email now."""
                            
                            # Rulează agentul
                            return await Runner.run(html_email_agent, prompt)

                        with log_expander:
                            st.write("**📤 Trimitere email HTML prin MCP Server...**")
                        
                        send_result = asyncio.run(_send())
                        
                        with log_expander:
                            st.write("**✅ Răspuns Agent:**")
                            # Afișează rezultatul corect (nu JSON parse)
                            if hasattr(send_result, 'output'):
                                st.write(send_result.output)
                            elif hasattr(send_result, 'model_dump'):
                                st.code(str(send_result.model_dump()), language="python")
                            else:
                                st.write(str(send_result))
                        
                        st.success(f"✅ **Email HTML trimis cu succes către: {user_email}**\n\n🎨 Design: Raiffeisen Bank (Galben & Alb)\n\nVerifică inbox-ul (și folder-ul Spam)!")
                        
                    except Exception as e:
                        error_msg = str(e)
                        
                        with log_expander:
                            st.write("**❌ EROARE:**")
                            st.code(error_msg)
                            
                            import traceback
                            st.write("**📋 Traceback complet:**")
                            st.code(traceback.format_exc())
                        
                        st.error(
                            f"❌ **Eroare la trimiterea emailului:**\n\n```\n{error_msg}\n```\n\n"
                            "**Verificări:**\n"
                            "- SMTP_PASSWORD are spații? Trebuie să fie 16 caractere fără spații!\n"
                            "- SMTP_HOST, SMTP_USER, SMTP_PASSWORD sunt setate în `.env`?\n"
                            "- Pentru Gmail, folosești App Password (nu parola normală)?\n"
                            "- Conexiunea la internet funcționează?\n\n"
                            "📋 Vezi detalii complete în secțiunea 'Detalii Trimitere Email' de mai sus.\n\n"
                            "📖 Consultă ghidul: `EMAIL_SETUP_GUIDE.md`"
                        )
    
    # Display selected products summary
    if st.session_state.selected_products:
        st.divider()
        st.subheader("📋 Produse Selectate pentru Planul Personalizat")
        
        # Get catalog for product details
        catalog = _get_products_catalog_dict()
        
        # Icon mapping
        ICONS = {
            "card_cumparaturi_rate": "💳",
            "depozite_termen": "🏦",
            "cont_economii_super_acces": "💰",
            "card_debit_platinum": "🪪",
            "credit_ipotecar_casa_ta": "🏠",
            "credit_nevoi_personale": "🧾",
            "fonduri_investitii_smartinvest": "📈",
            "pensie_privata_pilon3": "🎯",
            "cont_junior_adolescenti": "🧒",
            "asigurare_viata_economii": "🛡️",
        }
        
        # Display selected products
        selected_count = len(st.session_state.selected_products)
        st.info(f"**{selected_count} {'produs selectat' if selected_count == 1 else 'produse selectate'}** pentru planul dumneavoastră financiar personalizat")
        
        cols = st.columns(min(selected_count, 3))
        for i, product_id in enumerate(st.session_state.selected_products):
            with cols[i % 3]:
                if product_id in catalog:
                    prod = catalog[product_id]
                    icon = ICONS.get(product_id, "🏦")
                    st.markdown(f"{icon} **{prod['name']}**")
        
        # Action buttons
        col_generate, col_clear = st.columns(2)
        with col_generate:
            if st.button("🎯 Generează Plan Financiar Personalizat", type="primary", use_container_width=True):
                if not AWS_BEDROCK_API_KEY:
                    st.error("⚠️ Configurați cheia Bedrock în .env (AWS_BEARER_TOKEN_BEDROCK) pentru a genera planul financiar.")
                else:
                    # Prepare data for financial plan generation
                    profile_data = st.session_state.get("user_profile_data", {})
                    
                    if not profile_data:
                        st.error("⚠️ Profil utilizator lipsă. Vă rugăm să completați profilul mai sus.")
                    else:
                        with st.spinner("🤖 Generăm planul dumneavoastră financiar personalizat... (poate dura 10-20 secunde)"):
                            try:
                                # Build selected products data with full details
                                selected_products_data = []
                                catalog = _get_products_catalog_dict()
                                ranked_products = st.session_state.get("ranked_products", [])
                                
                                for product_id in st.session_state.selected_products:
                                    # Get product from catalog
                                    if product_id in catalog:
                                        product_info = catalog[product_id].copy()
                                        
                                        # Try to find personalized summary from ranked products
                                        personalized_summary = None
                                        for pid, prod in ranked_products:
                                            if pid == product_id:
                                                personalized_summary = prod.get("personalized_summary")
                                                break
                                        
                                        # Build complete product data
                                        product_data = {
                                            "product_id": product_id,
                                            "name": product_info.get("name", ""),
                                            "name_ro": product_info.get("name_ro", product_info.get("name", "")),
                                            "description": product_info.get("description", ""),
                                            "benefits": product_info.get("benefits", []),
                                            "personalized_summary": personalized_summary or product_info.get("description", ""),
                                        }
                                        selected_products_data.append(product_data)
                                
                                # Generate financial plan
                                plan_text = generate_financial_plan(profile_data, selected_products_data)
                                formatted_plan = format_plan_for_display(plan_text)
                                
                                # Store in session state for download and PDF conversion
                                st.session_state["generated_financial_plan"] = formatted_plan
                                st.session_state["plan_profile_data"] = profile_data  # Save for PDF filename
                                
                                # Save to database if user is logged in
                                user_email = st.session_state.get("auth", {}).get("email")
                                if user_email:
                                    save_success = save_financial_plan(user_email, formatted_plan)
                                    if save_success:
                                        st.success("✅ **Plan financiar generat și salvat în baza de date!**")
                                    else:
                                        st.warning("⚠️ **Plan generat cu succes, dar salvarea în baza de date a eșuat.**")
                                else:
                                    st.success("✅ **Plan financiar generat cu succes!**")
                                    st.info("ℹ️ **Autentificați-vă pentru a salva planul în contul dumneavoastră.**")
                                
                            except ValueError as ve:
                                st.error(f"❌ **Eroare de validare:** {str(ve)}")
                            except RuntimeError as re:
                                st.error(f"❌ **Eroare la generarea planului:** {str(re)}\n\nVerificați că Bedrock API este configurat corect.")
                            except Exception as e:
                                st.error(f"❌ **Eroare neașteptată:** {str(e)}")
                                import traceback
                                with st.expander("🔍 Detalii tehnice"):
                                    st.code(traceback.format_exc())
        
        with col_clear:
            if st.button("🗑️ Șterge Selecția", type="secondary", use_container_width=True):
                st.session_state.selected_products = []
                st.rerun()

# ============================================================================
# SECȚIUNE: AFIȘARE PLAN FINANCIAR GENERAT (PERSISTENT)
# ============================================================================
if "generated_financial_plan" in st.session_state and st.session_state["generated_financial_plan"]:
    st.divider()
    st.header("📋 Plan Financiar Generat")
    
    # Display the financial plan
    with st.expander("📄 Vizualizare Plan Financiar Complet", expanded=True):
        st.markdown(st.session_state["generated_financial_plan"])
    
    # Action buttons
    col_download_md, col_convert_pdf = st.columns(2)
    
    with col_download_md:
        # Download Markdown button
        profile_data = st.session_state.get("plan_profile_data", {})
        st.download_button(
            label="📥 Descarcă Markdown",
            data=st.session_state["generated_financial_plan"],
            file_name=f"plan_financiar_{profile_data.get('first_name', 'client')}_{profile_data.get('last_name', '')}.md",
            mime="text/markdown",
            use_container_width=True,
            type="secondary",
            key="download_md_persistent"
        )
    
    with col_convert_pdf:
        # Convert to PDF button
        if st.button("📄 Generează PDF", use_container_width=True, type="primary", key="generate_pdf_persistent"):
            st.session_state["pdf_conversion_running"] = True
            st.rerun()

# ============================================================================
# SECȚIUNE: PROCESARE CONVERSIE PDF (DACĂ ESTE ACTIVĂ)
# ============================================================================
if st.session_state.get("pdf_conversion_running", False):
    st.divider()
    st.header("🔄 Conversie Markdown → PDF")
    
    # Create containers for logs and results
    log_container = st.container()
    result_container = st.container()
    
    with log_container:
        st.subheader("📋 Log Conversie în Timp Real")
        log_area = st.empty()
    
    with result_container:
        st.subheader("📊 Rezultat Conversie")
        result_area = st.empty()
    
    try:
        # Get data from session state
        formatted_plan = st.session_state["generated_financial_plan"]
        profile_data = st.session_state.get("plan_profile_data", {})
        pdf_filename = f"plan_financiar_{profile_data.get('first_name', 'client')}_{profile_data.get('last_name', '')}.pdf"
        
        # Collect logs in session state for display
        if "pdf_logs" not in st.session_state:
            st.session_state["pdf_logs"] = []
        
        def progress_callback(message):
            """Callback to capture logs in real-time."""
            st.session_state["pdf_logs"].append(message)
            # Display all logs so far
            with log_area.container():
                st.info("🔄 **Conversie în progres...**")
                for log_msg in st.session_state["pdf_logs"]:
                    st.text(log_msg)
        
        with st.spinner("⏳ Convertesc planul în PDF..."):
            # Convert to PDF using direct pypandoc (fast, no timeout issues)
            pdf_path, message, logs = convert_markdown_to_pdf_direct(
                formatted_plan,
                pdf_filename,
                progress_callback=progress_callback
            )
        
        # Conversion successful!
        with log_area.container():
            st.success("✅ **Conversie completă!**")
            with st.expander("📋 Vezi Log Complet Conversie", expanded=False):
                for log in logs:
                    st.code(log, language=None)
        
        with result_area.container():
            st.success(f"✅ **{message}**")
            st.info(f"📁 **Locație fișier:** `{pdf_path}`")
            
            # Get file info
            from pathlib import Path
            file_size = Path(pdf_path).stat().st_size
            st.metric("📊 Dimensiune PDF", f"{file_size/1024:.1f} KB")
            
            # Offer download
            with open(pdf_path, 'rb') as pdf_file:
                st.download_button(
                    label="⬇️ Descarcă PDF Generat",
                    data=pdf_file.read(),
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="download_pdf_final"
                )
            
            st.info("💡 **Tip:** Poți regenera PDF-ul oricând apăsând din nou butonul 'Generează PDF'")
        
        # Reset conversion flag
        st.session_state["pdf_conversion_running"] = False
        st.session_state["pdf_logs"] = []
        
    except RuntimeError as re:
        with log_area.container():
            st.error("❌ **Eroare în timpul conversiei**")
            if st.session_state.get("pdf_logs"):
                with st.expander("📋 Log până la eroare", expanded=True):
                    for log in st.session_state["pdf_logs"]:
                        st.code(log, language=None)
        
        with result_area.container():
            st.error(f"❌ **Eroare la conversia PDF:** {str(re)}")
            st.warning(
                "💡 **Asigurați-vă că sunt instalate:**\n"
                "- `pandoc` (brew install pandoc)\n"
                "- `texlive` (brew install texlive)\n"
                "- `mcp-pandoc` (pip install mcp-pandoc)"
            )
        
        # Reset conversion flag
        st.session_state["pdf_conversion_running"] = False
        st.session_state["pdf_logs"] = []
        
    except Exception as e:
        with log_area.container():
            st.error("❌ **Eroare neașteptată**")
            if st.session_state.get("pdf_logs"):
                with st.expander("📋 Log până la eroare", expanded=True):
                    for log in st.session_state["pdf_logs"]:
                        st.code(log, language=None)
        
        with result_area.container():
            st.error(f"❌ **Eroare neașteptată la conversie:** {str(e)}")
            import traceback
            with st.expander("🔍 Detalii Tehnice Complete", expanded=True):
                st.code(traceback.format_exc())
        
        # Reset conversion flag
        st.session_state["pdf_conversion_running"] = False
        st.session_state["pdf_logs"] = []

# Information sidebar
with st.sidebar:
    st.subheader("💬 Explicații termeni")
    term = st.session_state.get("selected_term")
    meta = st.session_state.get("selected_term_meta", {}) or {}
    edu_level = st.session_state.get("selected_education_level")

    disabled = term is None
    if term:
        st.caption(f"Termen selectat: {term} ({meta.get('category', 'n/a')})")
        st.caption(f"Produs: {meta.get('product_name', 'n/a')}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Explain", disabled=disabled, use_container_width=True):
            # Load product markdown and call the text explanation agent
            product_markdown = _load_product_markdown(meta.get("product_name") or "")
            explanation = explain_term(
                term=term or "",
                summary_text=(meta.get("summary_text") or ""),
                education_level=edu_level,
                product_name=meta.get("product_name"),
                product_markdown=product_markdown,
            )
            st.session_state["term_explanation"] = explanation
            st.session_state["term_explanation_audio"] = None
    with c2:
        if st.button("Voice Explain", disabled=disabled, use_container_width=True):
            product_markdown = _load_product_markdown(meta.get("product_name") or "")
            # Prefer existing text explanation to avoid extra LLM calls
            text = st.session_state.get("term_explanation")
            if not text:
                text, audio_bytes = explain_term_voice(
                    term=term or "",
                    summary_text=(meta.get("summary_text") or ""),
                    education_level=edu_level,
                    product_name=meta.get("product_name"),
                    product_markdown=product_markdown,
                )
            else:
                # Only do TTS if text already computed
                from src.agents.voice_explain_agent import text_to_speech_openai
                audio_bytes = text_to_speech_openai(text)

            st.session_state["term_explanation"] = text
            st.session_state["term_explanation_audio"] = audio_bytes if audio_bytes else None

    if st.session_state.get("term_explanation"):
        st.info(st.session_state["term_explanation"])
    if st.session_state.get("term_explanation_audio"):
        st.audio(st.session_state["term_explanation_audio"], format="audio/mp3")

    st.divider()
    st.subheader("ℹ️ Informații")
    
    with st.expander("Cum funcționează?"):
        st.write(
            """
            Sistemul nostru AI analizează profilul dumneavoastră și recomandă produsele 
            cele mai potrivite bazat pe:
            
            - Situația financiară actuală
            - Obiectivele pe termen scurt și lung
            - Toleranța la risc
            - Etapa de viață actuală
            - Responsabilități familiale
            
            Produsele sunt ordonate de la cel mai relevant la cel mai puțin relevant 
            pentru situația dumneavoastră specifică.
            """
        )
    
    with st.expander("Protecția Datelor"):
        st.write(
            """
            Datele dumneavoastră sunt procesate în siguranță și nu sunt stocate permanent.
            Informațiile sunt folosite doar pentru a genera recomandări personalizate
            în această sesiune.
            """
        )

st.divider()
st.caption("Recomandări generate prin AI | Raiffeisen Bank © 2025")

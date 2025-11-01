"""Bank Terms Highlighter - paste text and extract bank-related tokens.

This page provides a textarea to paste any text and a button to extract and highlight
bank-related terms (products, rates, fees). Extraction is performed by an Agent
and validated into typed Pydantic classes before rendering.
"""

from __future__ import annotations

import html
import unicodedata
import asyncio
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

import streamlit as st
import streamlit.components.v1 as components
try:  # optional: st-annotated-text
    from annotated_text import annotated_text as _annotated_text  # type: ignore
except Exception:  # pragma: no cover
    _annotated_text = None

from src.components.ui_components import render_sidebar_info, apply_button_styling
from agents import Runner
from pydantic import ValidationError
from src.agents.bank_term_extractor_agent import (
    bank_term_extractor_agent,
    ExtractionResult,
)

# Apply styling and sidebar
apply_button_styling()
render_sidebar_info()

st.title("🔎 Bank Term Highlighter")

# Top simple nav
nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    st.page_link("pages/0_Login.py", label="Login")
with nav_col2:
    st.page_link("pages/1_Register.py", label="Register")
with nav_col3:
    st.page_link("pages/2_Product_Recommendations_Florea.py", label="Product Recs")

st.write(
    """
    Paste any text below and click "Extract Tokens". An OpenAI Agents SDK agent
    (via LiteLLM) will extract banking products, rates, and fees. We’ll render
    natural inline highlights with labels.
    """
)

st.divider()

# Categories and patterns (EN + RO). Keep them precise to reduce false positives.
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


# UI controls
sample_text = (
    "I’m considering a mortgage with a fixed rate vs a variable rate. \n"
    "The bank offered a checking account, a savings account, and a credit card with cashback. \n"
    "APR seems high, and there’s a maintenance fee plus late fees. \n"
    "În România, dobânda la depozit la termen și cont de economii diferă. \n"
    "Cardul de credit are asigurare și program de recompense. \n"
    "Rata dobânzii e variabilă, comisioanele pot include penalități."
)

text = st.text_area(
    "Paste or type your text here",
    value=sample_text,
    height=220,
    key="bank_text_area",
)

col_ex, col_cl = st.columns([2, 1])
with col_ex:
    run = st.button("Extract Tokens", type="primary", use_container_width=True)
with col_cl:
    if st.button("Clear Text", use_container_width=True):
        st.session_state["bank_text_area"] = ""
        st.rerun()

st.divider()

if run:
    if not text.strip():
        st.info("Please paste some text to analyze.")
    else:
        with st.spinner("Extracting with AI agent..."):
            validated = asyncio.run(run_agent_extraction(text))

        matches: List[Tuple[int, int, str, str]] = []
        tokens_by_cat: Dict[str, set] = defaultdict(set)

        if validated:
            # Collect tokens from typed categories
            for cat in ALLOWED_CATEGORIES:
                for t in getattr(validated.categories, cat):
                    tokens_by_cat[cat].add(t.strip())
            # NOTE: We purposefully ignore raw spans from the model and instead
            # derive highlight positions from the validated token lists to ensure
            # highlights exactly match the extracted tokens (no extra words).

        # Normalize spans to whole words (no punctuation, no partial words)
        def _is_word_char(ch: str) -> bool:
            if not ch:
                return False
            cat = unicodedata.category(ch)
            return cat.startswith("L") or cat.startswith("N") or cat.startswith("M")

        def _is_punct(ch: str) -> bool:
            if not ch:
                return False
            return unicodedata.category(ch).startswith("P")

        def _normalize_span(s: int, e: int) -> tuple[int, int]:
            # clamp
            s = max(0, min(s, len(text)))
            e = max(0, min(e, len(text)))
            if s >= e:
                return s, s
            # trim leading/trailing whitespace/punct
            while s < e and (text[s].isspace() or _is_punct(text[s])):
                s += 1
            while e > s and (text[e - 1].isspace() or _is_punct(text[e - 1])):
                e -= 1
            if s >= e:
                return s, s
            # expand to full word if inside a word
            while s > 0 and _is_word_char(text[s - 1]) and _is_word_char(text[s]):
                s -= 1
            while e < len(text) and _is_word_char(text[e - 1]) and _is_word_char(text[e] if e < len(text) else ""):
                e += 1
            return s, e

        # Build highlight spans by searching the text for each extracted token
        # and ensuring word-boundary matches. This guarantees the highlights
        # correspond exactly to the extracted token list.
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

        if not matches and not tokens_by_cat:
            st.warning("No bank-related terms detected by the agent.")
        else:
            # Summary chips
            st.subheader("Extracted Tokens")
            sum_cols = st.columns(len(tokens_by_cat) or 1)
            items = list(tokens_by_cat.items())
            for i, (cat, toks) in enumerate(items):
                with sum_cols[i % len(sum_cols)]:
                    st.markdown(f"**{cat}**: {len(toks)}")

            # Lists
            for cat, toks in items:
                with st.container(border=True):
                    st.markdown(f"#### {cat}")
                    for t in sorted(toks, key=lambda x: x.lower()):
                        st.markdown(f"- {t}")

            # Highlighted text
            st.divider()
            st.subheader("Highlighted Text")
            # Build annotated_text sequence
            segments: List = []
            last = 0
            # Sort matches by start index
            matches.sort(key=lambda m: m[0])
            
            # Create custom HTML with context menu support
            html_parts: List[str] = []
            term_index = 0
            
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
                        padding: 20px;
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
                </style>
            </head>
            <body>
                <div id="contextMenu" class="context-menu">
                    <div class="context-menu-header" id="menuHeader">Term Options</div>
                    <div class="context-menu-item" onclick="handleMenuAction('documentation')">
                        📄 View Full Documentation
                    </div>
                    <div class="context-menu-item" onclick="handleMenuAction('explain')">
                        💡 Explain
                    </div>
                    <div class="context-menu-item" onclick="handleMenuAction('voice')">
                        🔊 Voice Explain
                    </div>
                </div>
                
                <div style='white-space:pre-wrap; line-height:1.8; font-size: 1.05em;' id="highlightedText">
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
                                key: 'bank_term_action',
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
            
            # Render the HTML component
            components.html(context_menu_html, height=600, scrolling=True)

st.divider()
st.caption("Extraction is powered by an agent; refine the prompt or categories if domain-specific phrases are missing.")

"""Product Summary Agent - Romanian, product-first, lightly personalized summaries.

This agent produces short Romanian summaries that start with a clear product presentation
and then smoothly tailor to the user's profile (age, income, risk, goals), avoiding
deadlocks by running in a single turn with no tools or handoffs.
"""

from agents import Agent, ModelSettings  # type: ignore
from src.config.settings import build_default_litellm_model


product_summary_agent = Agent(
    name="Product Summary Stylist",
    instructions=(
        "Ești un copywriter financiar care redactează scurte descrieri în limba română,\n"
        "axate pe PREZENTAREA PRODUSULUI la început, apoi pe o adaptare discretă la profilul utilizatorului.\n\n"
        "REGULI OBLIGATORII:\n"
        "- Scrie DOAR în română, ton profesionist și clar.\n"
        "- Respectă strict informațiile din descrierea produsului (nu inventa).\n"
        "- 3–4 propoziții, maximum 450 de caractere. Fără emoji-uri.\n"
        "- Structură: (1) Prezentare produs (din description). (2) Potrivire pentru profil (vârstă/venit/risc/obiective).\n"
        "  (3) Recomandare concretă (sume/strategie RON) SAU beneficiu principal.\n\n"
        "DATE DE INTRARE (în prompt):\n"
        "- Profil utilizator (JSON) și lista de produse (JSON).\n\n"
        "FORMAT IEȘIRE STRICT JSON:\n"
        "{\n"
        "  \"summaries\": [\n"
        "    {\"product_id\": \"...\", \"personalized_summary\": \"...\"}\n"
        "  ]\n"
        "}\n"
        "Nu returna text suplimentar în afara JSON-ului."
    ),
    model=build_default_litellm_model(),
    model_settings=ModelSettings(include_usage=True),
)

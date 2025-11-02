"""Product Recommendations page - Personalized banking product recommendations.

Flow:
1. Rank products by relevance (Product Recommendation Agent)
2. Get NLP-generated base summaries (English)
3. Personalize summaries for user profile (Summary Personalization Agent)
4. Display personalized content to user
"""

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
from src.utils.db import save_financial_plan

"""
Feature flags for LLM-driven enrichments. Disable to avoid extra turns/latency
and rely solely on the Ranking Agent outputs (justification + recommended_action).
"""
USE_PERSONALIZATION_AGENT = False
USE_TITLE_AGENT = False

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
                        # Build hyper-personalized recommendations based on EVERY detail
                        personalization_requests = []
                        for product in products_with_descriptions:
                            personalization_requests.append({
                                "product_id": product["product_id"],
                                "product_name": product["name"],
                                "product_description": product["description"],
                                "benefits": product["benefits"],
                                "relevance_score": product["score"],
                            })

                        # Call LLM for deep personalization
                        prompt = f"""Creează recomandări EXTREM DE PERSONALIZATE pentru fiecare produs bancar bazate pe profilul EXACT al utilizatorului.

PROFIL UTILIZATOR COMPLET:
- Vârstă: {user_profile.age} ani
- Venit Anual: {user_profile.annual_income:,.0f} RON/an ({user_profile.annual_income/12:,.0f} RON/lună)
- Status Angajare: {user_profile.employment_status}
- Nivel Studii: {user_profile.education_level}
- Stare Civilă: {user_profile.marital_status}
- Are Copii: {'Da' if user_profile.has_children else 'Nu'}
- Toleranță Risc: {user_profile.risk_tolerance}
- Obiective Financiare: {', '.join(user_profile.financial_goals)}

PRODUSE:
{json.dumps(personalization_requests, indent=2, ensure_ascii=False)}

INSTRUCȚIUNI CRITICE PENTRU PERSONALIZARE AVANSATĂ:

0. **ADAPTEAZĂ COMPLEXITATEA LIMBAJULUI LA ALFABETIZAREA FINANCIARĂ**:
   
   Estimare nivel cunoștințe financiare bazat pe Vârstă + Studii:
   
   **NIVEL SCĂZUT** (limbaj simplu, fără termeni tehnici):
   - Tânăr (<30 ani) + Fără studii superioare/Liceu → explică termeni de bază
   - Vârstnic (60+ ani) + Fără studii superioare/Liceu → limbaj foarte accesibil
   - Student indiferent de vârstă → educațional, explică concepte
   
   Exemple limbaj simplu:
   - ✅ "bani pe care îi pui deoparte lunar" 
   - ❌ "alocări periodice de capital"
   - ✅ "dobânda = banii în plus pe care îi primești de la bancă"
   - ❌ "rentabilitatea investiției"
   - ✅ "împarte riscul între mai multe locuri"
   - ❌ "diversificare de portofoliu"
   
   **NIVEL MEDIU** (termeni bancari comuni + explicații scurte):
   - 30-50 ani + Facultate/Master
   - 50+ ani + Facultate/Master
   
   Exemple limbaj mediu:
   - ✅ "diversificare (împărțirea investițiilor în mai multe domenii)"
   - ✅ "dobândă fixă garantată"
   - ✅ "capitalizare lunară a dobânzii"
   
   **NIVEL AVANSAT** (termeni tehnici fără explicații):
   - Orice vârstă + Master/Doctorat + venit mare (>100k RON/an)
   - 35-55 ani + Facultate + venit mare + "investiții" în obiective
   
   Exemple limbaj avansat:
   - ✅ "randament anual efectiv"
   - ✅ "optimizare fiscală prin deduceri"
   - ✅ "portofoliu diversificat cu alocare strategică"
   - ✅ "DAE (Dobândă Anuală Efectivă)"

INSTRUCȚIUNI CRITICE PENTRU PERSONALIZARE AVANSATĂ:

1. **SPECIFICĂ SUME CONCRETE ÎN RON** adaptate la venitul și situația utilizatorului:
   - Pentru investiții: recomandă % din venit sau sume lunare concrete
   - Pentru credite: calculează capacitate de plată (max 40% din venit)
   - Pentru economii: sugerează praguri realiste (3-6 luni cheltuieli = rezervă urgență)

2. **ADAPTEAZĂ LA FIECARE DETALIU**:
   - Vârstă 20 ani angajat → "la început de carieră, construiește fundația financiară"
   - Vârstă 20 ani student → "concentrează-te pe educație financiară și economii mici"
   - Vârstă 20 ani șomer dar venit anual → "probabil sprijin familial, învață să gestionezi bani"
   - Vârstă 35 ani cu copii → "responsabilități familiale, prioritate securitate"
   - Vârstă 50 ani fără copii → "maximizează investiții pentru pensionare"

3. **TON ȘI LIMBAJ ADAPTAT**:
   - Tânăr (18-25): ton prietenos, casual, educativ, "Ai", "începi", "construiești"
   - Mediu (26-45): ton profesionist, practic, "Gestionezi", "optimizezi", "planifici"
   - Senior (46+): ton respectuos, orientat securitate, "Asigurați", "protejați", "mențineti"

4. **RECOMANDĂRI SPECIFICE BAZATE PE CONTEXT**:

   Exemple concrete:
   
   - **Plan investiții pentru 20 ani angajat, 3000 RON/lună, risc mediu:**
     "La 20 de ani și cu un venit stabil de 3.000 RON/lună, poți începe cu investiții lunare de 300-500 RON (10-15% din venit) în fonduri mixte. Orizontul lung de timp (40 ani până la pensie) îți permite să beneficiezi de puterea dobânzii compuse."
   
   - **Plan investiții pentru 20 ani șomer, 20.000 RON/an venit (probabil părinți):**
     "Cu un venit anual de 20.000 RON (probabil sprijin familial), focusează-te mai întâi pe educație financiară și economii de urgență (minim 10.000 RON). Apoi, începe investiții mici de 100-200 RON/lună pentru a învăța despre piață fără riscuri mari."
   
   - **Credit ipotecar pentru 35 ani angajat, 8000 RON/lună, căsătorit cu copii:**
     "Cu venitul familiei de 8.000 RON/lună și responsabilități către copii, poți accesa un credit de până la 150.000-200.000 EUR (rată max 3.200 RON/lună = 40% din venit). Prioritizează avansul minim 15% pentru dobândă mai bună."
   
   - **Cont economii pentru 22 ani student, 15.000 RON/an:**
     "Ca student cu venituri limitate de 1.250 RON/lună, creează o rezervă de urgență de 5.000-7.500 RON (4-6 luni). Acest cont cu retrageri gratuite este perfect pentru accesibilitate când ai nevoie rapid de bani pentru taxe sau emergențe."

5. **PĂSTREAZĂ ACURATEȚEA**: 
   - NU inventa beneficii sau termeni care nu sunt în description
   - NU schimba informații despre dobânzi, perioade, comisioane
   - Folosește description ca sursă de adevăr pentru caracteristicile produsului

6. **FORMAT OUTPUT**: 
   - Maxim 3-4 propoziții
   - Include recomandare concretă (sumă RON sau strategie)
   - Explică DE CE această sumă/strategie se potrivește profilului
   - Limbaj accesibil dar profesionist

Returnează DOAR un array JSON:
[
  {{"product_id": "...", "personalized_summary": "..."}},
  ...
]"""

                        result = await Runner.run(
                            personalization_orchestrator,
                            prompt,
                            context=context,
                            max_turns=3,
                        )
                        return result

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
                    # Build a concise, actionable summary from justification + recommended action
                    for product in products_with_descriptions:
                        just = product.get("justification") or ""
                        action = product.get("recommended_action") or ""
                        combined = just.strip()
                        if action:
                            combined = (combined + (" " if combined else "")) + f"Recomandare: {action.strip()}"
                        product["personalized_summary"] = combined or product.get("description", "")
                
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
                st.info(summary_text)
            
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
                
                with st.spinner("Generăm emailul și îl trimitem..."):
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
                            st.write("**📝 Generare conținut email...**")
                        
                        # Build a compact summary payload (top 5)
                        top_items = []
                        for pid, prod in ranked_products[:5]:
                            top_items.append({
                                "product_id": pid,
                                "name_ro": prod.get("name_ro", prod.get("name", "")),
                                "name_en": prod.get("name_en", prod.get("name", "")),
                                "score": prod.get("score", 0),
                                "summary": prod.get("personalized_summary") or prod.get("base_summary", prod.get("description", "")),
                            })

                        subject = "Recomandările dumneavoastră personalizate - Rezumat"
                        
                        # Get user profile from session
                        user_profile_data = st.session_state.get("user_profile_data", {})
                        user_profile_json = json.dumps(user_profile_data, ensure_ascii=False)
                        items_json = json.dumps(top_items, ensure_ascii=False)

                        with log_expander:
                            st.write(f"**📋 Subiect email:** {subject}")
                            st.write(f"**🎯 Produse incluse:** {len(top_items)}")

                        prompt = (
                            f"Recipient: {user_email}\n"
                            f"Subject: {subject}\n\n"
                            "Instrucțiuni: Redactează un email scurt în limba română (fără emoji), politicos, "
                            "cu un rezumat al recomandărilor de mai jos. Menține 120–200 cuvinte, listează 3–5 produse cu câte o propoziție.\n\n"
                            f"Profil utilizator (JSON): {user_profile_json}\n\n"
                            f"Produse (JSON): {items_json}\n\n"
                            "După ce finalizezi textul emailului, apelează tool-ul send_email cu câmpurile: to, subject, body."
                        )

                        with log_expander:
                            st.write("**🤖 Apelare AI Agent pentru generare email...**")

                        async def _send():
                            """Trimite email folosind MCP Email Server cu conexiune explicită."""
                            from agents.mcp import MCPServerStdio
                            from src.utils.mcp_email_client import get_mcp_email_server_config
                            from src.config.settings import build_default_litellm_model
                            from agents import Agent, ModelSettings
                            
                            # Creează și conectează MCP serverul
                            mcp_server = MCPServerStdio(get_mcp_email_server_config())
                            await mcp_server.connect()
                            
                            # Creează agent cu MCP server conectat
                            temp_agent = Agent(
                                name="Email Summary Sender",
                                instructions=email_summary_agent.instructions,
                                mcp_servers=[mcp_server],
                                model=build_default_litellm_model(),
                                model_settings=ModelSettings(include_usage=True),
                            )
                            
                            # Rulează agentul
                            return await Runner.run(temp_agent, prompt)

                        with log_expander:
                            st.write("**📤 Trimitere email prin MCP Server...**")
                        
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
                        
                        st.success(f"✅ **Email trimis cu succes către: {user_email}**\n\nVerifică inbox-ul (și folder-ul Spam)!")
                        
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
                                
                                # Store in session state for download
                                st.session_state["generated_financial_plan"] = formatted_plan
                                
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
                                
                                # Display plan in expandable section
                                with st.expander("📄 Vizualizare Plan Financiar Complet", expanded=True):
                                    st.markdown(formatted_plan)
                                
                                # Download button
                                st.download_button(
                                    label="📥 Descarcă Planul Financiar (Markdown)",
                                    data=formatted_plan,
                                    file_name=f"plan_financiar_{profile_data.get('first_name', 'client')}_{profile_data.get('last_name', '')}.md",
                                    mime="text/markdown",
                                    use_container_width=True,
                                    type="secondary"
                                )
                                
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

# Information sidebar
with st.sidebar:
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

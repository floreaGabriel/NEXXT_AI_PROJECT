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
)
from src.agents.user_experience_summary_agent import (
    personalization_orchestrator,
    PersonalizationContext,
    personalize_products_batch,  # Direct function for personalization
)
from src.agents.product_title_generation_agent import product_title_agent
from src.agents.email_summary_agent import email_summary_agent

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


# --- Product Catalog with Base English Summaries (from NLP stage) ---
# In production, these would come from a database or NLP summarization service
PRODUCT_BASE_SUMMARIES = {
    "carduri_cumparaturi": {
        "name": "Shopping Credit Card",
        "name_ro": "Card de Cumpărături",
        "description": "Card de credit special pentru cumpărături cu rate fixe și fără dobândă",
        "base_summary": "Special credit card offering interest-free installment plans at partner merchants, with cashback rewards up to 5% and comprehensive purchase protection insurance.",
        "benefits": ["Rate fără dobândă la parteneri", "Cashback până la 5%", "Asigurare achizitii"],
    },
    "depozite_termen": {
        "name": "Fixed-Term Deposit",
        "name_ro": "Depozit la Termen",
        "description": "Depozit bancar cu dobândă fixă și garantată",
        "base_summary": "Bank deposit with guaranteed fixed interest rates, offering competitive returns with full capital protection across flexible terms from 1 to 60 months.",
        "benefits": ["Dobânzi competitive", "Sumă garantată", "Diverse perioade (1-60 luni)"],
    },
    "cont_economii": {
        "name": "Savings Account",
        "name_ro": "Cont de Economii",
        "description": "Cont flexibil de economii cu acces rapid la fonduri",
        "base_summary": "Flexible savings account providing variable interest rates with instant access to your funds and no withdrawal penalties or administration fees.",
        "benefits": ["Dobândă variabilă", "Retragere fără penalizări", "Fără comision administrare"],
    },
    "card_debit": {
        "name": "Premium Debit Card",
        "name_ro": "Card de Debit Premium",
        "description": "Card de debit cu beneficii extinse și asigurări incluse",
        "base_summary": "Premium debit card featuring 2% cashback on purchases, comprehensive travel insurance coverage, and exclusive access to airport lounges worldwide.",
        "benefits": ["Cashback 2%", "Asigurare călătorii", "Acces lounge aeroporturi"],
    },
    "credit_imobiliar": {
        "name": "Mortgage Loan",
        "name_ro": "Credit Imobiliar",
        "description": "Împrumut pentru achiziție sau refinanțare locuință",
        "base_summary": "Mortgage financing for home purchase or refinancing with competitive interest rates, terms up to 30 years, and flexible down payment options including 0% advance possibilities.",
        "benefits": ["Dobândă competitivă", "Perioadă până la 30 ani", "Posibilitate avans 0%"],
    },
    "credit_nevoi_personale": {
        "name": "Personal Loan",
        "name_ro": "Credit Nevoi Personale",
        "description": "Împrumut rapid pentru orice scop",
        "base_summary": "Fast-approval personal loan for any purpose, with no collateral required for amounts up to 50,000 RON and flexible repayment schedules.",
        "benefits": ["Aprobare rapidă", "Fără garanții până la 50.000 RON", "Rată flexibilă"],
    },
    "investitii_fonduri": {
        "name": "Investment Funds",
        "name_ro": "Fonduri de Investiții",
        "description": "Portofolii diversificate de investiții gestionate profesional",
        "base_summary": "Professionally managed investment portfolios offering diversified risk exposure across multiple strategies to optimize long-term returns.",
        "benefits": ["Diversificare risc", "Gestiune profesională", "Multiple strategii"],
    },
    "pensie_privata": {
        "name": "Private Pension (Pillar III)",
        "name_ro": "Pensie Privată (Pilon III)",
        "description": "Plan de economii pe termen lung pentru pensie",
        "base_summary": "Long-term retirement savings plan with tax advantages, flexible contribution options, and professionally managed portfolios designed for sustainable long-term growth.",
        "benefits": ["Avantaje fiscale", "Contribuții flexibile", "Randament pe termen lung"],
    },
    "cont_copii": {
        "name": "Junior Account",
        "name_ro": "Cont Junior",
        "description": "Cont de economii special pentru copii",
        "base_summary": "Specialized savings account for children with enhanced interest rates, financial education resources, and optional debit card for teenagers to develop money management skills.",
        "benefits": ["Dobândă bonificată", "Educație financiară", "Card pentru adolescenți"],
    },
    "asigurare_viata": {
        "name": "Life Insurance",
        "name_ro": "Asigurare de Viață",
        "description": "Protecție financiară pentru familie",
        "base_summary": "Comprehensive life insurance providing financial protection for your family with optional investment components and tax-deductible premiums.",
        "benefits": ["Protecție financiară", "Opțiuni investiționale", "Deducere fiscală"],
    }
}

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
                )
                
                # STEP 1: Product Recommendation Agent - Rank products by relevance score
                # Uses deterministic rule-based scoring (TODO: replace with ML model)
                ranked_products = rank_products_for_profile(user_profile.model_dump_json())
                
                # STEP 2: Attach base English summaries from NLP stage
                # In production, these would come from a separate NLP summarization service
                products_with_base_summaries = []
                for product in ranked_products:
                    pid = product["product_id"]
                    base_data = PRODUCT_BASE_SUMMARIES.get(pid, {})
                    
                    products_with_base_summaries.append({
                        "product_id": pid,
                        "name": base_data.get("name", pid),
                        "name_ro": base_data.get("name_ro", pid),
                        "description": base_data.get("description", ""),
                        "base_summary": base_data.get("base_summary", "Banking product with various benefits."),
                        "benefits": base_data.get("benefits", []),
                        "score": product["score"],
                    })
                
                # STEP 3: Summary Personalization Agent - Personalize English summaries for user
                # Uses Bedrock LLM to adapt base summaries to user's specific situation
                nest_asyncio.apply()
                
                context = PersonalizationContext(user_profile=user_profile)
                
                async def run_personalization_agent():
                    # Build detailed prompt for each product
                    personalization_requests = []
                    for product in products_with_base_summaries:
                        user_context_parts = []
                        
                        # Build user context description
                        if user_profile.age is not None:
                            if user_profile.age < 30:
                                user_context_parts.append("young professional starting financial journey")
                            elif user_profile.age < 45:
                                user_context_parts.append("established professional managing responsibilities")
                            else:
                                user_context_parts.append("experienced individual planning long-term security")
                        
                        if user_profile.has_children:
                            user_context_parts.append("parent with family responsibilities")
                        
                        if user_profile.risk_tolerance:
                            rt = user_profile.risk_tolerance.lower()
                            if "low" in rt or "scăzută" in rt or "scazuta" in rt:
                                user_context_parts.append("preferring stable, low-risk solutions")
                            elif "high" in rt or "ridicată" in rt or "ridicata" in rt:
                                user_context_parts.append("comfortable with growth-oriented strategies")
                        
                        user_context = ", ".join(user_context_parts) if user_context_parts else "seeking financial solutions"
                        
                        relevance_tone = "excellent match" if product["score"] >= 0.8 else "strong fit" if product["score"] >= 0.6 else "potential option"
                        
                        personalization_requests.append({
                            "product_id": product["product_id"],
                            "product_name": product["name"],
                            "base_summary": product["base_summary"],
                            "user_context": user_context,
                            "relevance_tone": relevance_tone,
                        })
                    
                    # Call LLM for personalization
                    prompt = f"""Personalize these banking product summaries for the user profile.

User Profile:
- Age: {user_profile.age}
- Income: {user_profile.annual_income} RON/year
- Marital Status: {user_profile.marital_status}
- Has Children: {user_profile.has_children}
- Risk Tolerance: {user_profile.risk_tolerance}
- Financial Goals: {', '.join(user_profile.financial_goals)}

Products to personalize:
{json.dumps(personalization_requests, indent=2)}

CRITICAL INSTRUCTIONS:
1. For each product, create a personalized English summary (2-3 sentences max)
2. PRESERVE all facts from base_summary - do NOT add features or benefits
3. ADJUST language and tone to resonate with user_context
4. Use relevance_tone to modulate enthusiasm
5. Connect product features to user's life situation naturally
6. Maintain professional banking language

Return ONLY a JSON array with this exact structure:
[
  {{"product_id": "...", "personalized_summary": "..."}},
  ...
]"""

                    result = await Runner.run(
                        personalization_orchestrator,
                        prompt,
                        context=context,
                    )
                    return result
                
                # Execute personalization agent
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
                        
                        for product in products_with_base_summaries:
                            product["personalized_summary"] = summary_map.get(
                                product["product_id"],
                                product["base_summary"]  # Fallback to base if LLM didn't personalize
                            )
                    else:
                        st.warning("⚠️ LLM didn't return valid JSON. Using base summaries.")
                        for product in products_with_base_summaries:
                            product["personalized_summary"] = product["base_summary"]
                            
                except Exception as e:
                    st.warning(f"⚠️ Error parsing LLM response: {e}. Using base summaries.")
                    for product in products_with_base_summaries:
                        product["personalized_summary"] = product["base_summary"]
                
                enriched_products = products_with_base_summaries

                # STEP 3.5: Generate personalized Romanian titles (no emojis) using Product Title Agent
                # Build payload from enriched products
                products_payload = [
                    {
                        "product_id": p["product_id"],
                        "name": p.get("name_ro") or p.get("name") or p["product_id"],
                        "description": p.get("description", ""),
                        "benefits": p.get("benefits", []),
                    }
                    for p in enriched_products
                ]

                llm_titles: dict[str, str] = {}
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

                        return await Runner.run(product_title_agent, prompt)

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
                    "carduri_cumparaturi": "💳",
                    "depozite_termen": "🏦",
                    "cont_economii": "💰",
                    "card_debit": "🪪",
                    "credit_imobiliar": "🏠",
                    "credit_nevoi_personale": "🧾",
                    "investitii_fonduri": "📈",
                    "pensie_privata": "🎯",
                    "cont_copii": "🧒",
                    "asigurare_viata": "🛡️",
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
                                "name_en": enriched_product.get("name", pid),
                                "name_ro": enriched_product.get("name_ro", pid),
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
                
                # Display results
                st.success("✅ Recomandări generate cu succes!")
                
                st.divider()
                st.subheader("📊 Produsele Recomandate pentru Dumneavoastră")
                
                # Display match score
                st.info(f"📈 Bazat pe profilul dumneavoastră: {age} ani, venit anual {annual_income:,.0f} RON, {marital_status.lower()}")

                # Display products in ranked order
                for idx, (product_id, product) in enumerate(ranked_products, 1):
                    with st.container(border=True):
                        # Product header
                        col_icon, col_title = st.columns([1, 11])
                        with col_icon:
                            st.markdown(f"## {product['icon']}")
                        with col_title:
                            # Prefer personalized Romanian title when available
                            display_name = llm_titles.get(product_id, product['name_ro'])
                            st.markdown(f"### {idx}. {display_name}")
                            st.caption(f"_{product['name_en']}_")
                            # Match percentage
                            match_percent = int(product['score'] * 100)
                            st.progress(product['score'], text=f"Potrivire: {match_percent}%")
                        

                        # Romanian product description
                        st.write(product['description'])
                        
                        # Personalized English summary (AI-generated based on user profile)
                        if product.get("personalized_summary"):
                            st.markdown("**💡 Personalized for You:**")
                            st.info(product["personalized_summary"])
                            
                            # Show base summary in expander for comparison
                            with st.expander("📄 View base product summary"):
                                st.write(product.get("base_summary", ""))

                        # Benefits (Romanian)
                        st.markdown("**Beneficii principale:**")
                        for benefit in product['benefits']:
                            st.markdown(f"- ✓ {benefit}")
                        
                        # CTA
                        col_learn, col_apply = st.columns(2)
                        with col_learn:
                            st.button(
                                f"📖 Detalii {product['name_ro']}", 
                                key=f"learn_{product_id}",
                                use_container_width=True
                            )
                        with col_apply:
                            st.button(
                                f"✅ Aplică Acum", 
                                key=f"apply_{product_id}",
                                type="primary",
                                use_container_width=True
                            )
                        
                        # Personalized note for top recommendation
                        if idx == 1:
                            st.success("⭐ **Recomandarea Noastră Principală** - Acest produs se potrivește cel mai bine profilului dumneavoastră!")

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
                                    import os
                                    
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
                                            "name_ro": prod.get("name_ro"),
                                            "name_en": prod.get("name_en"),
                                            "score": prod.get("score"),
                                            "summary": prod.get("personalized_summary") or prod.get("base_summary", ""),
                                        })

                                    subject = "Recomandările dumneavoastră personalizate - Rezumat"
                                    user_profile_json = user_profile.model_dump_json(ensure_ascii=False)
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
                                        return await Runner.run(email_summary_agent, prompt)

                                    with log_expander:
                                        st.write("**📤 Trimitere email prin SMTP...**")
                                    
                                    send_result = asyncio.run(_send())
                                    
                                    with log_expander:
                                        st.write("**✅ Răspuns Agent:**")
                                        st.json(send_result.model_dump() if hasattr(send_result, 'model_dump') else str(send_result))
                                    
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
                
            except Exception as e:
                st.error(f"A apărut o eroare: {str(e)}")

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

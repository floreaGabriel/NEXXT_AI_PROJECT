"""Operator Product Recommendations - Banking product recommendations for client lookup.

Flow (Operator Version):
1. Operator enters client email
2. Fetch user profile from database
3. Rank products by relevance (Product Recommendation Agent)
4. Display simplified product cards (no AI summaries)
5. Select products and generate financial plan
6. Send email and convert to PDF
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
from src.agents.email_summary_agent import email_summary_agent
from src.agents.financial_plan_agent import generate_financial_plan, format_plan_for_display
from src.agents.pdf_converter_direct import convert_markdown_to_pdf_direct
from src.utils.db import save_financial_plan, get_user_by_email


USE_PERSONALIZATION_AGENT = False
USE_TITLE_AGENT = False

apply_button_styling()
render_sidebar_info()

st.title("🎯 Recomandări pentru Client - Modul Operator")

st.write(
    """
    Introduceți email-ul clientului pentru a genera recomandări personalizate bazate pe profilul său.
    Produsele vor fi ordonate în funcție de relevanță.
    """
)

st.divider()

# ============================================================================
# CLIENT LOOKUP SECTION
# ============================================================================

st.subheader("📧 Caută Client")

client_email = st.text_input(
    "Introduceți email-ul clientului:",
    placeholder="client@example.com",
    help="Email-ul trebuie să existe în baza de date"
)

# Initialize session state variables
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = []
if 'ranked_products' not in st.session_state:
    st.session_state.ranked_products = None
if 'llm_titles' not in st.session_state:
    st.session_state.llm_titles = {}
if 'user_profile_data' not in st.session_state:
    st.session_state.user_profile_data = None
if 'client_email' not in st.session_state:
    st.session_state.client_email = None

# Search and Generate Recommendations Button
if st.button("🔍 Caută Client și Generează Recomandări", type="primary", use_container_width=True):
    if not client_email:
        st.error("Vă rugăm să introduceți un email valid.")
    elif not AWS_BEDROCK_API_KEY:
        st.error("Vă rugăm configurați cheia API Bedrock (AWS_BEARER_TOKEN_BEDROCK) în fișierul .env")
    else:
        with st.spinner("Căutăm clientul în baza de date..."):
            try:
                # Fetch user from database
                user_data = get_user_by_email(client_email)
                
                if not user_data:
                    st.error(f"❌ Clientul cu email-ul '{client_email}' nu a fost găsit în baza de date.")
                    st.stop()
                
                # Display client profile
                st.success(f"✅ Client găsit: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
                
                # Display client info card
                with st.container(border=True):
                    st.markdown("### 👤 Profil Client")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nume", f"{user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}")
                        st.metric("Email", client_email)
                    with col2:
                        st.metric("Vârstă", f"{user_data.get('age', 'N/A')} ani")
                        st.metric("Status Marital", user_data.get('marital_status', 'N/A'))
                    with col3:
                        extra = user_data.get('extra', {})
                        annual_income = extra.get('annual_income', 0)
                        st.metric("Venit Anual", f"{annual_income:,.0f} RON" if annual_income else "N/A")
                        st.metric("Status Profesional", user_data.get('employment_status', 'N/A'))
                
                st.divider()
                
                # Map database fields to UserProfile
                extra = user_data.get('extra', {})
                
                # Helper function to normalize strings
                def normalize_string(s):
                    if not s:
                        return None
                    s = str(s).lower().strip()
                    # Map Romanian to English if needed
                    mappings = {
                        'necăsătorit/ă': 'single',
                        'căsătorit/ă': 'married',
                        'divorțat/ă': 'divorced',
                        'văduv/ă': 'widowed',
                        'angajat': 'employed',
                        'independent': 'self-employed',
                        'șomer': 'unemployed',
                        'pensionar': 'retired',
                        'student': 'student',
                        'scăzută': 'low',
                        'medie': 'medium',
                        'ridicată': 'high',
                        'fără studii superioare': 'fara_studii_superioare',
                        'liceu': 'liceu',
                        'facultate': 'facultate',
                        'master': 'masterat',
                        'doctorat': 'doctorat',
                    }
                    return mappings.get(s, s)
                
                # Create UserProfile from database data
                user_profile = UserProfile(
                    marital_status=normalize_string(user_data.get('marital_status')),
                    annual_income=float(extra.get('annual_income', 50000)),
                    age=int(user_data.get('age', 35)),
                    employment_status=normalize_string(user_data.get('employment_status')),
                    has_children=bool(user_data.get('has_children', False)),
                    risk_tolerance=normalize_string(extra.get('risk_tolerance', 'medium')),
                    financial_goals=[goal.lower().strip() for goal in extra.get('financial_goals', [])] if isinstance(extra.get('financial_goals'), list) else [],
                    education_level=normalize_string(extra.get('education_level', 'facultate')),
                )
                
                with st.spinner("Analizăm profilul și generăm recomandări personalizate prin AI..."):
                    # STEP 1: Product Recommendation Agent - Rank products by relevance score
                    ranked_products = rank_products_for_profile(user_profile.model_dump_json())
                    
                    # STEP 2: Get product catalog and prepare for UI
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
                            "justification": product.get("justification", ""),
                            "recommended_action": product.get("recommended_action", ""),
                        })
                    
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
                    for enriched_product in products_with_descriptions:
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
                                },
                            )
                        )
                    
                    # Already sorted by Product Recommendation Agent
                    ranked_products = products_for_ui
                    
                    # Store in session state to persist across reruns
                    st.session_state.ranked_products = ranked_products
                    st.session_state.llm_titles = {}
                    st.session_state.user_profile_data = {
                        "age": user_data.get('age'),
                        "annual_income": extra.get('annual_income', 50000),
                        "marital_status": user_data.get('marital_status'),
                        "first_name": user_data.get('first_name'),
                        "last_name": user_data.get('last_name'),
                    }
                    st.session_state.client_email = client_email
                    
                    # Display results
                    st.success("✅ Recomandări generate cu succes!")
                    
            except Exception as e:
                st.error(f"A apărut o eroare: {str(e)}")
                import traceback
                with st.expander("🔍 Detalii tehnice"):
                    st.code(traceback.format_exc())

# ============================================================================
# DISPLAY PRODUCTS SECTION
# ============================================================================

# Display products (outside the button block so they persist)
if st.session_state.ranked_products is not None:
    st.divider()
    st.subheader("📊 Produse Recomandate pentru Client")
    
    # Display match score
    profile_data = st.session_state.user_profile_data
    st.info(f"📈 Bazat pe profil: {profile_data.get('age', 'N/A')} ani, venit anual {profile_data.get('annual_income', 0):,.0f} RON, {profile_data.get('marital_status', 'N/A')}")
    
    ranked_products = st.session_state.ranked_products

    # Display products in ranked order (SIMPLIFIED - NO SUMMARIES)
    for idx, (product_id, product) in enumerate(ranked_products, 1):
        with st.container(border=True):
            # Product header with selection button
            col_icon, col_title, col_select = st.columns([1, 9, 2])
            with col_icon:
                st.markdown(f"## {product['icon']}")
            with col_title:
                display_name = product['name']
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
        st.info(f"**{selected_count} {'produs selectat' if selected_count == 1 else 'produse selectate'}** pentru planul financiar al clientului")
        
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
                        st.error("⚠️ Profil utilizator lipsă. Vă rugăm să căutați din nou clientul.")
                    else:
                        with st.spinner("🤖 Generăm planul financiar personalizat pentru client... (poate dura 10-20 secunde)"):
                            try:
                                # Build selected products data with full details
                                selected_products_data = []
                                catalog = _get_products_catalog_dict()
                                ranked_products = st.session_state.get("ranked_products", [])
                                
                                for product_id in st.session_state.selected_products:
                                    # Get product from catalog
                                    if product_id in catalog:
                                        product_info = catalog[product_id].copy()
                                        
                                        # Build complete product data
                                        product_data = {
                                            "product_id": product_id,
                                            "name": product_info.get("name", ""),
                                            "name_ro": product_info.get("name_ro", product_info.get("name", "")),
                                            "description": product_info.get("description", ""),
                                            "benefits": product_info.get("benefits", []),
                                            "personalized_summary": product_info.get("description", ""),
                                        }
                                        selected_products_data.append(product_data)
                                
                                # Generate financial plan
                                plan_text = generate_financial_plan(profile_data, selected_products_data)
                                formatted_plan = format_plan_for_display(plan_text)
                                
                                # Store in session state for download and PDF conversion
                                st.session_state["generated_financial_plan"] = formatted_plan
                                st.session_state["plan_profile_data"] = profile_data
                                
                                # Save to database if client email is available
                                client_email = st.session_state.get("client_email")
                                if client_email:
                                    save_success = save_financial_plan(client_email, formatted_plan)
                                    if save_success:
                                        st.success("✅ **Plan financiar generat și salvat în baza de date!**")
                                    else:
                                        st.warning("⚠️ **Plan generat cu succes, dar salvarea în baza de date a eșuat.**")
                                else:
                                    st.success("✅ **Plan financiar generat cu succes!**")
                                
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
# FINANCIAL PLAN DISPLAY SECTION (PERSISTENT)
# ============================================================================
if "generated_financial_plan" in st.session_state and st.session_state["generated_financial_plan"]:
    st.divider()
    st.header("📋 Plan Financiar Generat")
    
    # Display the financial plan
    with st.expander("📄 Vizualizare Plan Financiar Complet", expanded=True):
        st.markdown(st.session_state["generated_financial_plan"])
    
    # Action buttons
    col_download_md, col_convert_pdf, col_send_email = st.columns(3)
    
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
    
    with col_send_email:
        # Send email button
        if st.button("✉️ Trimite pe Email", use_container_width=True, type="primary", key="send_email_persistent"):
            st.session_state["email_sending_running"] = True
            st.rerun()

# ============================================================================
# EMAIL SENDING SECTION (IF ACTIVE)
# ============================================================================
if st.session_state.get("email_sending_running", False):
    st.divider()
    st.header("✉️ Trimitere Email")
    
    client_email = st.session_state.get("client_email")
    if not client_email:
        st.error("❌ Email client lipsește. Vă rugăm să căutați din nou clientul.")
        st.session_state["email_sending_running"] = False
    else:
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
            st.session_state["email_sending_running"] = False
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
                        
                        st.write(f"**📧 Destinatar:** {client_email}")
                        st.write("**🎨 Generare email HTML profesional Raiffeisen...**")
                    
                    # Build summary content in Markdown format
                    with log_expander:
                        st.write("**📝 Construire conținut recomandări...**")
                    
                    # Get user profile data
                    user_profile_data = st.session_state.get("user_profile_data", {})
                    age = user_profile_data.get("age", 35)
                    annual_income = user_profile_data.get("annual_income", 50000)
                    marital_status = user_profile_data.get("marital_status", "necăsătorit/ă")
                    
                    # Use the generated financial plan
                    markdown_content = st.session_state["generated_financial_plan"]
                    
                    with log_expander:
                        st.write(f"**✅ Conținut Plan Financiar:** {len(markdown_content)} caractere")
                        st.write("**🎨 Conversie Markdown → HTML Raiffeisen...**")
                    
                    # Convert to HTML with Raiffeisen design
                    from src.utils.html_converter import convert_financial_plan_to_html, clean_markdown_for_email
                    
                    # Get user name if available from session
                    user_name = f"{user_profile_data.get('first_name', '')} {user_profile_data.get('last_name', '')}".strip()
                    
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

                    subject = f"Planul Dumneavoastră Financiar Personalizat - {user_name}"

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

RECIPIENT: {client_email}
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
                    
                    st.success(f"✅ **Email HTML trimis cu succes către: {client_email}**\n\n🎨 Design: Raiffeisen Bank (Galben & Alb)\n\nVerifică inbox-ul clientului (și folder-ul Spam)!")
                    
                    # Reset flag
                    st.session_state["email_sending_running"] = False
                    
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
                    
                    # Reset flag
                    st.session_state["email_sending_running"] = False

# ============================================================================
# PDF CONVERSION SECTION (IF ACTIVE)
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
    st.divider()
    st.subheader("ℹ️ Informații Operator")
    
    with st.expander("Cum funcționează?"):
        st.write(
            """
            **Modul Operator** permite căutarea rapidă a clienților și generarea 
            de recomandări personalizate bazate pe profilul lor din baza de date.
            
            **Pași:**
            1. Introduceți email-ul clientului
            2. Sistemul caută automat în baza de date
            3. Afișează profilul complet al clientului
            4. Generează recomandări AI personalizate
            5. Selectați produsele potrivite
            6. Generați plan financiar complet
            7. Trimiteți pe email sau descărcați PDF
            
            Produsele sunt ordonate automat de la cel mai relevant la cel mai puțin relevant.
            """
        )
    
    with st.expander("Protecția Datelor"):
        st.write(
            """
            Toate datele clienților sunt stocate securizat în baza de date PostgreSQL.
            Accesul la această interfață ar trebui restricționat doar pentru operatori autorizați.
            
            **Recomandări:**
            - Nu partajați emailurile clienților
            - Asigurați-vă că GDPR este respectat
            - Logați toate accesările pentru audit
            """
        )

st.divider()
st.caption("Modul Operator - Recomandări generate prin AI | Raiffeisen Bank © 2025")

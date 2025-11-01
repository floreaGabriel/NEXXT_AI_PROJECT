"""Product Recommendations page - Personalized banking product recommendations."""

import streamlit as st
from src.config.settings import AWS_BEDROCK_API_KEY
from src.components.ui_components import render_sidebar_info, apply_button_styling
from src.agents.product_recommendation_agent import (
    product_recommendation_orchestrator,
    ProductRecommendationContext,
    UserProfile,
)

apply_button_styling()
render_sidebar_info()

st.title("🎯 Recomandări Personalizate de Produse")

st.write(
    """
    Primiți recomandări personalizate de produse bancare bazate pe profilul dumneavoastră.
    Produsele sunt ordonate în funcție de relevanță pentru situația dumneavoastră financiară.
    """
)

st.divider()

# User Profile Input Section
st.subheader("📋 Profilul Dumneavoastră")

col1, col2 = st.columns(2)

with col1:
    marital_status = st.selectbox(
        "Status Marital",
        ["Necăsătorit/ă", "Căsătorit/ă", "Divorțat/ă", "Văduv/ă"],
        help="Statusul dumneavoastră marital actual"
    )
    
    annual_income = st.number_input(
        "Venit Anual (RON)",
        min_value=0,
        max_value=1000000,
        value=50000,
        step=5000,
        help="Venitul anual brut în RON"
    )
    
    age = st.number_input(
        "Vârstă",
        min_value=18,
        max_value=100,
        value=35,
        help="Vârsta dumneavoastră în ani"
    )
    
    has_children = st.checkbox(
        "Am copii",
        help="Bifați dacă aveți copii"
    )

with col2:
    employment_status = st.selectbox(
        "Status Profesional",
        ["Angajat", "Independent", "Șomer", "Pensionar", "Student"],
        help="Situația dumneavoastră profesională actuală"
    )
    
    risk_tolerance = st.select_slider(
        "Toleranță la Risc",
        options=["Scăzută", "Medie", "Ridicată"],
        value="Medie",
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
        default=["Economii pe termen lung"],
        help="Selectați obiectivele dumneavoastră financiare principale"
    )

st.divider()

# Get Recommendations Button
if st.button("🔍 Obține Recomandări", type="primary", use_container_width=True):
    if not AWS_BEDROCK_API_KEY:
        st.error("Vă rugăm configurați cheia API Bedrock (AWS_BEARER_TOKEN_BEDROCK) în fișierul .env")
    else:
        with st.spinner("Analizăm profilul și generăm recomandări personalizate..."):
            try:
                # Create user profile
                user_profile = UserProfile(
                    marital_status=marital_status.lower(),
                    annual_income=float(annual_income),
                    age=age,
                    employment_status=employment_status.lower(),
                    has_children=has_children,
                    risk_tolerance=risk_tolerance.lower(),
                    financial_goals=[goal.lower() for goal in financial_goals],
                )
                
                # TODO: Implement actual agent execution
                # context = ProductRecommendationContext(user_profile=user_profile)
                # result = await Runner.run(
                #     product_recommendation_orchestrator,
                #     f"Recommend products for this user profile: {user_profile.model_dump_json()}",
                #     context=context,
                # )
                
                # Placeholder: Mock ranking based on simple rules
                products_data = {
                    "cont_economii": {
                        "name": "Cont de Economii",
                        "icon": "💰",
                        "description": "Cont flexibil de economii cu acces rapid la fonduri",
                        "benefits": ["Dobândă variabilă", "Retragere fără penalizări", "Fără comision administrare"],
                        "score": 0.95
                    },
                    "depozite_termen": {
                        "name": "Depozit la Termen",
                        "icon": "🏦",
                        "description": "Depozit bancar cu dobândă fixă și garantată",
                        "benefits": ["Dobânzi competitive", "Sumă garantată", "Diverse perioade (1-60 luni)"],
                        "score": 0.90
                    },
                    "carduri_cumparaturi": {
                        "name": "Card de Cumpărături",
                        "icon": "💳",
                        "description": "Card de credit special pentru cumpărături cu rate fixe și fără dobândă",
                        "benefits": ["Rate fără dobândă la parteneri", "Cashback până la 5%", "Asigurare achiziții"],
                        "score": 0.85
                    },
                    "pensie_privata": {
                        "name": "Pensie Privată (Pilon III)",
                        "icon": "🎯",
                        "description": "Plan de economii pe termen lung pentru pensie",
                        "benefits": ["Avantaje fiscale", "Contribuții flexibile", "Randament pe termen lung"],
                        "score": 0.80
                    },
                    "credit_imobiliar": {
                        "name": "Credit Imobiliar",
                        "icon": "🏠",
                        "description": "Împrumut pentru achiziție sau refinanțare locuință",
                        "benefits": ["Dobândă competitivă", "Perioadă până la 30 ani", "Posibilitate avans 0%"],
                        "score": 0.75
                    },
                }
                
                # Simple rule-based ranking (to be replaced with ML model)
                ranked_products = list(products_data.items())
                
                # Adjust scores based on profile
                for product_id, product in ranked_products:
                    if product_id == "cont_copii" and has_children:
                        product["score"] += 0.15
                    if product_id == "pensie_privata" and age > 40:
                        product["score"] += 0.10
                    if product_id == "credit_imobiliar" and "cumpărare casă" in [g.lower() for g in financial_goals]:
                        product["score"] += 0.20
                    if product_id == "investitii_fonduri" and risk_tolerance == "Ridicată":
                        product["score"] += 0.15
                    if product_id == "depozite_termen" and risk_tolerance == "Scăzută":
                        product["score"] += 0.10
                
                # Sort by score
                ranked_products.sort(key=lambda x: x[1]["score"], reverse=True)
                
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
                            st.markdown(f"### {idx}. {product['name']}")
                            # Match percentage
                            match_percent = int(product['score'] * 100)
                            st.progress(product['score'], text=f"Potrivire: {match_percent}%")
                        
                        # Product description
                        st.write(product['description'])
                        
                        # Benefits
                        st.markdown("**Beneficii principale:**")
                        for benefit in product['benefits']:
                            st.markdown(f"- ✓ {benefit}")
                        
                        # CTA
                        col_learn, col_apply = st.columns(2)
                        with col_learn:
                            st.button(
                                f"📖 Detalii {product['name']}", 
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

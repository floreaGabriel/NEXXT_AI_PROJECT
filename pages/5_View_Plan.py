"""View Financial Plan Page - Personalized plan analysis and visualization.

This page displays a user's financial plan with:
- Plan overview (expandable dropdown)
- Personalized analysis adapted to user profile
- Statistical insights and predictions
- Interactive charts and visualizations
- Goal tracking and timelines
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import asyncio
import nest_asyncio

from src.components.ui_components import render_sidebar_info, apply_button_styling
from src.utils.plan_analytics import (
    generate_key_statistics,
    calculate_wealth_projection,
    calculate_goal_timeline,
)
from src.agents.plan_analysis_agent import generate_personalized_analysis

# Apply styling
apply_button_styling()
render_sidebar_info()

# Enable nested event loops for async operations
nest_asyncio.apply()

st.title("📊 Planul Tău Financiar Personalizat")

# Top auth nav
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

# Require authentication
if not st.session_state.get("auth", {}).get("logged_in"):
    st.warning("Pentru a accesa planul financiar, vă rugăm să vă autentificați.")
    link_col1, link_col2 = st.columns(2)
    with link_col1:
        if st.button("→ Autentificare", use_container_width=True):
            st.switch_page("pages/0_Login.py")
    with link_col2:
        if st.button("→ Înregistrare", use_container_width=True):
            st.switch_page("pages/1_Register.py")
    st.stop()

st.divider()


# =============================================================================
# MOCK DATA FUNCTIONS - Easy to replace with database queries later
# =============================================================================

def get_user_financial_plan(email: str) -> dict:
    """
    Get user's financial plan from database.
    
    TODO: Replace with actual database query:
        from src.utils.db import get_user_by_email
        user_data = get_user_by_email(email)
        return {
            "plan_text": user_data.get("user_plan"),
            "user_profile": {...}
        }
    
    Args:
        email: User email
    
    Returns:
        Dictionary with plan_text and user_profile
    """
    # MOCK DATA - Replace this entire function with DB query
    mock_user_profile = {
        "email": email,
        "first_name": "Alexandra",
        "last_name": "Popescu",
        "age": 32,
        "marital_status": "Căsătorit/ă",
        "annual_income": 72000.0,
        "employment_status": "Angajat",
        "has_children": True,
        "number_of_children": 1,
        "risk_tolerance": "Medie",
        "education_level": "Facultate",
        "financial_goals": [
            "Economii pe termen lung",
            "Educație copii",
            "Investiții"
        ]
    }
    
    mock_plan = """# Plan Financiar Personalizat

## 1. Rezumat Executiv

Planul dumneavoastră financiar este construit pentru o etapă dinamică a vieții - vârsta de 32 de ani, cu un venit solid de 72.000 RON anual și responsabilități familiale crescânde. Cu un copil și planuri pentru viitor, acest plan balansează creșterea patrimoniului cu securitatea financiară.

**Obiective Principale:**
- Construirea unui fond de educație pentru copil
- Dezvoltarea unui portofoliu de investiții diversificat
- Asigurarea securității financiare pe termen lung

**Produse Selectate:**
- Cont de Economii Super Acces Plus - pentru lichiditate și fond de urgență
- Fond de Pensii Facultative Raiffeisen Acumulare - pentru securitate pe termen lung
- SmartInvest - Planuri de Investiții Inteligente - pentru creștere patrimonială

## 2. Analiza Situației Actuale

**Profil Financiar:**
- Vârstă: 32 ani - etapa de consolidare a carierei și creștere a familiei
- Venit anual: 72.000 RON (6.000 RON/lună)
- Situație familială: Căsătorit/ă cu 1 copil
- Status profesional: Angajat cu venit stabil
- Toleranță la risc: Medie - deschis la oportunități dar conștient de responsabilități

**Obiective Financiare:**

*Pe termen scurt (1-3 ani):*
- Construirea unui fond de urgență de 36.000 RON (6 luni cheltuieli)
- Inițierea contributiilor regulate la investiții
- Stabilirea unui plan de economii pentru educație

*Pe termen mediu (3-7 ani):*
- Acumularea a 100.000 RON pentru educația copilului
- Diversificarea portofoliului de investiții
- Creșterea patrimoniului cu 40%

*Pe termen lung (7+ ani):*
- Asigurarea unui fond de pensie privat de 500.000 RON
- Independență financiară la vârsta de 55 ani
- Securitate financiară pentru familie

## 3. Strategia de Produse Recomandate

### 3.1 Cont de Economii Super Acces Plus

**De ce acest produs:**
Acest cont oferă flexibilitatea necesară pentru gestionarea cash flow-ului și construirea fondului de urgență. Cu acces instant la bani și dobândă competitivă, este fundația securității dumneavoastră financiare.

**Beneficii principale:**
- Dobândă variabilă de până la 3% - superioară conturilor curente
- Acces instant la fonduri fără penalizări
- Fără comision de administrare - economii maxime
- Securitate garantată de stat până la 100.000 EUR
- Interfață online simplă pentru monitorizare

**Mod de utilizare recomandat:**
1. **Luna 1-2:** Deschideți contul și setați un transfer automat de 1.500 RON lunar
2. **Luna 3-12:** Continuați contribuțiile până atingeți 18.000 RON (3 luni cheltuieli)
3. **Anul 2:** Completați fondul de urgență la 36.000 RON (6 luni cheltuieli)
4. **Menținere:** Păstrați acest nivel și folosiți pentru cheltuieli neprevăzute

### 3.2 Fond de Pensii Facultative Raiffeisen Acumulare

**De ce acest produs:**
La 32 de ani, aveți 28 de ani până la pensionare standard - perfect pentru puterea compunerii. Acest fond oferă avantaje fiscale imediate (400 RON/an) și siguranța unui portofoliu gestionat profesional.

**Beneficii principale:**
- Randament mediu-lung estimat: 6% anual
- Deducere fiscală de până la 400 EUR/an
- Gestiune profesională a investițiilor
- Diversificare automată a riscului
- Protecție în caz de evenimente neprevăzute

**Mod de utilizare recomandat:**
1. **Contribuție recomandată:** 600 RON/lună (10% din venit)
2. **Strategie:** Profil balanced pentru toleranța dumneavoastră medie la risc
3. **Proiecție:** La vârsta de 60 ani, estimăm 500.000+ RON acumulați
4. **Review:** Anual pentru ajustarea strategiei în funcție de vârstă

### 3.3 SmartInvest - Planuri de Investiții Inteligente

**De ce acest produs:**
Pentru obiectivele pe termen mediu (educație copil, creștere patrimonială), SmartInvest oferă flexibilitatea unui portofoliu diversificat cu gestiune profesională și praguri mici de intrare.

**Beneficii principale:**
- Portofoliu diversificat: acțiuni, obligațiuni, fonduri
- Randament țintă: 7-9% anual (profil balanced)
- Contribuții flexibile - ajustabile oricând
- Acces la piețe internaționale
- Rapoarte lunare detaliate

**Mod de utilizare recomandat:**
1. **Start:** Investiție inițială de 5.000 RON
2. **Contribuție lunară:** 1.200 RON (20% din venit)
3. **Orizont:** Minim 5 ani pentru maximizarea randamentului
4. **Strategie:** 60% acțiuni, 40% obligațiuni (balanced)
5. **Rebalansare:** Automată trimestrială

## 4. Timeline de Implementare

**Luna 1-2: Fundamentele**
- Deschidere Cont de Economii Super Acces Plus
- Transfer inițial 3.000 RON + setup transfer automat 1.500 RON/lună
- Înscriere Fond de Pensii cu contribuție 600 RON/lună
- Configurare plăți automate

**Luna 3-6: Consolidare**
- Deschidere SmartInvest cu 5.000 RON investiție inițială
- Setup contribuție automată 1.200 RON/lună
- Prima evaluare a progresului - ajustări dacă e necesar
- Construirea obiceiurilor de monitorizare lunară

**Luna 7-12: Creștere**
- Fondul de urgență atinge 18.000 RON (50% din țintă)
- Portofoliul SmartInvest crește la ~12.000 RON
- Pensia privată acumulează ~6.000 RON
- Evaluare anuală și planificare anul următor

**Anul 2+: Obiective pe Termen Lung**
- Completare fond urgență la 36.000 RON
- Creșterea contribuției la investiții cu inflația
- Acumulare constantă pentru educație copil
- Construirea patrimoniului pentru pensionare

## 5. Analiza Riscurilor și Protecție

**Riscuri identificate:**
- Pierderea venitului (șomaj, boală)
- Cheltuieli medicale neprevăzute pentru familie
- Inflație care erodează puterea de cumpărare
- Volatilitate piețelor financiare
- Nevoi financiare crescute odată cu creșterea copilului

**Măsuri de protecție:**
- **Fond de urgență:** 36.000 RON acoperă 6 luni cheltuieli - protecție solidă
- **Diversificare:** 3 produse diferite reduc riscul concentrării
- **Produse protejate:** Contul de economii și pensia au garantii de siguranță
- **Flexibilitate:** SmartInvest permite retrageri dacă e nevoie
- **Gestiune profesională:** Fondurile sunt gestionate de experți

## 6. Rezultate Așteptate

**Pe termen scurt (1 an):**
- Fond de urgență: 18.000 RON acumulați
- Total economii + investiții: ~30.000 RON
- Obiceiuri financiare solide stabilite
- Reducere stres financiar și creștere a siguranței

**Pe termen mediu (3-5 ani):**
- Fond educație copil: 80.000-100.000 RON
- Fond pensie privată: 40.000-50.000 RON
- Portofoliu investiții: 90.000-110.000 RON
- Patrimoniu total crescut cu 50%+

**Pe termen lung (7+ ani):**
- Siguranță financiară completă pentru familie
- Fond pensie: 500.000+ RON la vârsta de 60 ani
- Independență financiară pentru educația copilului
- Opțiuni pentru pensionare anticipată

## 7. Pași Următori Imediați

1. **Programare întâlnire** cu consultantul Raiffeisen pentru deschiderea produselor (online sau în sucursală)
2. **Pregătire documente:** CI, dovadă venit, cod IBAN cont curent
3. **Deschidere Cont Economii** - 15 minute online
4. **Înscriere Pensie Privată** - completare formular și alegere strategie
5. **Activare SmartInvest** - evaluare profil risc și transfer inițial

## 8. Recomandări Finale

**Pentru succes maxim:**
- **Automatizați tot:** Transferurile automate elimină tentația cheltuielilor
- **Revedeți lunar:** 15 minute pentru a monitoriza progresul
- **Rămâneți pe traseu:** Nu vă lăsați descurajat de volatilitatea pe termen scurt
- **Creșteți contribuțiile:** Odată cu creșterea venitului, măriți economisirea
- **Comunicați în familie:** Asigurați-vă că partenerul înțelege și susține planul

**Frecvență de revizuire:**
- **Lunar:** Check rapid al soldurilor și contribuțiilor
- **Trimestrial:** Analiză performanță investiții
- **Anual:** Revizuire completă și ajustări strategice

**Când să contactați consultantul:**
- Schimbare semnificativă în venit (±20%)
- Apariția unui al doilea copil
- Planuri de achiziție proprietate
- Orice întrebare sau nelămurire

---

*Acest plan este personalizat pentru situația dumneavoastră actuală și trebuie revizuit anual sau la schimbări majore în viață.*
"""
    
    return {
        "plan_text": mock_plan,
        "user_profile": mock_user_profile,
        "products": [
            "Cont de Economii Super Acces Plus",
            "Fond de Pensii Facultative Raiffeisen Acumulare",
            "SmartInvest - Planuri de Investiții Inteligente"
        ]
    }


# =============================================================================
# MAIN PAGE LOGIC
# =============================================================================

# Get user data
user_email = st.session_state["auth"]["email"]

# Load financial plan
with st.spinner("Încărcăm planul dumneavoastră financiar..."):
    try:
        plan_data = get_user_financial_plan(user_email)
        plan_text = plan_data["plan_text"]
        user_profile = plan_data["user_profile"]
        products = plan_data["products"]
        
        if not plan_text:
            st.warning("Nu aveți încă un plan financiar generat. Vizitați pagina de recomandări pentru a crea unul.")
            if st.button("→ Mergi la Recomandări", use_container_width=True):
                st.switch_page("pages/2_Product_Recommendations_Florea.py")
            st.stop()
        
    except Exception as e:
        st.error(f"Eroare la încărcarea planului: {str(e)}")
        st.stop()

# Generate statistics
with st.spinner("Analizăm planul dumneavoastră..."):
    statistics = generate_key_statistics(user_profile, plan_text, products)

# =============================================================================
# PERSONALIZED INTRODUCTION
# =============================================================================

st.markdown("### 👋 Bun venit înapoi!")

# Generate personalized introduction
with st.spinner("Personalizăm conținutul pentru dumneavoastră..."):
    try:
        async def get_intro():
            return await generate_personalized_analysis(
                user_profile=user_profile,
                financial_plan=plan_text,
                analysis_type="introduction",
                statistics=statistics
            )
        
        intro_text = asyncio.run(get_intro())
        st.markdown(intro_text)
    except Exception as e:
        # Fallback if agent fails
        st.markdown(f"""
        Salutare, **{user_profile.get('first_name', 'Alexandra')}**! Planul dumneavoastră financiar 
        este construit special pentru profilul și obiectivele dumneavoastră. Vom analiza împreună 
        cum vă puteți atinge obiectivele financiare.
        """)

st.divider()

# =============================================================================
# KEY METRICS CARDS
# =============================================================================

st.markdown("### 📈 Statistici Cheie")

metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

with metrics_col1:
    st.metric(
        label="Venit Lunar",
        value=f"{statistics['savings_capacity']['monthly_income']:,.0f} RON",
        help="Venitul dumneavoastră lunar estimat"
    )

with metrics_col2:
    st.metric(
        label="Economii Lunare",
        value=f"{statistics['savings_capacity']['monthly_savings_potential']:,.0f} RON",
        delta=f"{statistics['savings_capacity']['savings_ratio']:.1f}% din venit",
        help="Capacitatea dumneavoastră estimată de economisire"
    )

with metrics_col3:
    st.metric(
        label="Randament Așteptat",
        value=f"{statistics['risk_return_analysis']['average_return']:.1f}%",
        delta="Anual",
        help="Randamentul mediu estimat al produselor dumneavoastră"
    )

with metrics_col4:
    st.metric(
        label="Nivel Risc",
        value=statistics['risk_return_analysis']['risk_level'],
        help="Nivelul de risc al portofoliului dumneavoastră"
    )

st.divider()

# =============================================================================
# PLAN OVERVIEW (EXPANDABLE)
# =============================================================================

st.markdown("### 📄 Planul Dumneavoastră Complet")

with st.expander("👁️ Vezi Planul Financiar Detaliat", expanded=False):
    st.markdown(plan_text)
    
    # Download button
    st.download_button(
        label="📥 Descarcă Planul (Markdown)",
        data=plan_text,
        file_name=f"plan_financiar_{user_email}_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown",
        use_container_width=True
    )

st.divider()

# =============================================================================
# WEALTH PROJECTION CHART
# =============================================================================

st.markdown("### 💰 Proiecția Creșterii Patrimoniului")

projection_years = st.slider(
    "Selectați orizontul de timp (ani):",
    min_value=1,
    max_value=30,
    value=10,
    help="Alegeți câți ani doriți să vizualizați"
)

wealth_proj = calculate_wealth_projection(user_profile, years=projection_years)

# Create chart data
years = [p["year"] for p in wealth_proj["projections"]]
balances = [p["balance"] for p in wealth_proj["projections"]]
contributions = [p["total_contributions"] for p in wealth_proj["projections"]]
returns = [p["total_returns"] for p in wealth_proj["projections"]]

# Create Plotly figure
fig_wealth = go.Figure()

fig_wealth.add_trace(go.Scatter(
    x=years,
    y=balances,
    name='Total Patrimoniu',
    mode='lines+markers',
    line=dict(color='#1f77b4', width=3),
    fill='tozeroy',
    fillcolor='rgba(31, 119, 180, 0.1)'
))

fig_wealth.add_trace(go.Scatter(
    x=years,
    y=contributions,
    name='Contribuții Totale',
    mode='lines',
    line=dict(color='#ff7f0e', width=2, dash='dash')
))

fig_wealth.add_trace(go.Scatter(
    x=years,
    y=returns,
    name='Randament Total',
    mode='lines',
    line=dict(color='#2ca02c', width=2, dash='dot')
))

fig_wealth.update_layout(
    title=f"Evoluția Patrimoniului în {projection_years} Ani",
    xaxis_title="Ani",
    yaxis_title="Valoare (RON)",
    hovermode='x unified',
    template='plotly_white',
    height=400
)

st.plotly_chart(fig_wealth, use_container_width=True, key="wealth_projection_chart")

# Summary metrics for projection
proj_col1, proj_col2, proj_col3 = st.columns(3)

with proj_col1:
    st.metric(
        "Contribuții Totale",
        f"{wealth_proj['summary']['total_contributions']:,.0f} RON",
        help="Total sume depuse de dumneavoastră"
    )

with proj_col2:
    st.metric(
        "Randament Total",
        f"{wealth_proj['summary']['total_returns']:,.0f} RON",
        delta=f"+{wealth_proj['summary']['roi_percentage']:.1f}%",
        help="Câștigul generat de investiții"
    )

with proj_col3:
    st.metric(
        "Patrimoniu Final",
        f"{wealth_proj['summary']['final_balance']:,.0f} RON",
        help=f"Valoarea totală după {projection_years} ani"
    )

st.divider()

# =============================================================================
# GOAL TIMELINES
# =============================================================================

st.markdown("### 🎯 Progresul către Obiective")

if statistics['goal_timelines']:
    
    # Create timeline visualization
    for idx, goal_data in enumerate(statistics['goal_timelines'][:3]):  # Top 3 goals
        st.markdown(f"#### {idx + 1}. {goal_data['goal'].title()}")
        
        goal_col1, goal_col2 = st.columns([2, 1])
        
        with goal_col1:
            # Progress bar (simulate current progress)
            current_months = min(6, goal_data['months_needed'])  # Assume 6 months progress
            progress_percentage = (current_months / goal_data['months_needed']) * 100 if goal_data['months_needed'] > 0 else 0
            
            st.progress(min(progress_percentage / 100, 1.0))
            st.caption(f"Progres estimat: {progress_percentage:.1f}%")
            
            # Timeline info
            st.markdown(f"""
            - **Țintă:** {goal_data['target_amount']:,.0f} RON
            - **Contribuție lunară:** {goal_data['monthly_contribution']:,.0f} RON
            - **Timp estimat:** {goal_data['years_needed']:.1f} ani ({goal_data['months_needed']:.0f} luni)
            - **Finalizare estimată:** {goal_data['estimated_completion']}
            """)
        
        with goal_col2:
            # Mini milestone chart
            milestones = goal_data.get('milestones', [])
            if milestones:
                milestone_percentages = [m['percentage'] for m in milestones]
                milestone_months = [m['months_from_now'] for m in milestones]
                
                fig_milestone = go.Figure()
                fig_milestone.add_trace(go.Bar(
                    x=milestone_percentages,
                    y=[f"{m}%" for m in milestone_percentages],
                    orientation='h',
                    marker=dict(
                        color=milestone_percentages,
                        colorscale='Greens',
                        showscale=False
                    ),
                    text=[f"{m} luni" for m in milestone_months],
                    textposition='auto',
                ))
                
                fig_milestone.update_layout(
                    title="Milestone-uri",
                    xaxis_title="Progres (%)",
                    yaxis_title="",
                    height=200,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig_milestone, use_container_width=True, key=f"milestone_chart_{idx}")
        
        st.divider()

else:
    st.info("Obiectivele dumneavoastră sunt în curs de analiză. Veți vedea aici progresul către fiecare obiectiv.")

# =============================================================================
# RISK-RETURN ANALYSIS
# =============================================================================

st.markdown("### ⚖️ Analiza Risc-Randament")

risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    # Risk gauge
    risk_score = statistics['risk_return_analysis']['risk_score']
    
    fig_risk = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Scor Risc Portofoliu"},
        gauge={
            'axis': {'range': [0, 4]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 1.5], 'color': "lightgreen"},
                {'range': [1.5, 2.5], 'color': "yellow"},
                {'range': [2.5, 4], 'color': "salmon"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 3
            }
        }
    ))
    
    fig_risk.update_layout(height=250)
    st.plotly_chart(fig_risk, use_container_width=True, key="risk_gauge_chart")
    
    st.metric(
        "Nivel Risc",
        statistics['risk_return_analysis']['risk_level'],
        help="Nivelul de risc al portofoliului dumneavoastră"
    )

with risk_col2:
    # Return potential
    avg_return = statistics['risk_return_analysis']['average_return']
    
    fig_return = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_return,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Randament Estimat (%)"},
        delta={'reference': 4.0, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [0, 12]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 4], 'color': "lightgray"},
                {'range': [4, 8], 'color': "lightblue"},
                {'range': [8, 12], 'color': "lightgreen"}
            ],
        }
    ))
    
    fig_return.update_layout(height=250)
    st.plotly_chart(fig_return, use_container_width=True, key="return_gauge_chart")
    
    st.metric(
        "Randament Mediu Anual",
        f"{avg_return:.1f}%",
        delta=f"Sharpe Ratio: {statistics['risk_return_analysis']['sharpe_ratio']:.2f}",
        help="Randamentul așteptat al investițiilor dumneavoastră"
    )

# Diversification score
st.markdown("#### Scor Diversificare")
diversification = statistics['risk_return_analysis']['diversification_score']

diversification_color = "green" if diversification > 60 else "orange" if diversification > 40 else "red"

st.progress(diversification / 100)
st.markdown(f"**{diversification:.0f}%** - {'Foarte bine diversificat' if diversification > 60 else 'Moderat diversificat' if diversification > 40 else 'Necesită diversificare'}")

st.divider()

# =============================================================================
# PERSONALIZED INSIGHTS
# =============================================================================

st.markdown("### 💡 Insight-uri Personalizate")

with st.spinner("Generăm insight-uri personalizate..."):
    try:
        async def get_insights():
            return await generate_personalized_analysis(
                user_profile=user_profile,
                financial_plan=plan_text,
                analysis_type="insights",
                statistics=statistics
            )
        
        insights_text = asyncio.run(get_insights())
        st.markdown(insights_text)
    except Exception as e:
        st.info("""
        **Insight-uri cheie:**
        
        1. **Capacitate solidă de economisire** - Cu rata dumneavoastră de economisire, sunteți pe drumul cel bun
        2. **Diversificare echilibrată** - Portofoliul combină securitate cu oportunități de creștere
        3. **Orizont de timp favorabil** - Aveți timp suficient pentru a beneficia de puterea compunerii
        """)

st.divider()

# =============================================================================
# PRODUCT BREAKDOWN
# =============================================================================

st.markdown("### 📦 Produsele Dumneavoastră")

if products:
    product_tabs = st.tabs(products)
    
    for idx, product_name in enumerate(products):
        with product_tabs[idx]:
            st.markdown(f"#### {product_name}")
            
            # Get product-specific info from risk-return analysis
            product_info = statistics['risk_return_analysis']['products_analysis'].get(product_name, {})
            
            if product_info:
                prod_col1, prod_col2 = st.columns(2)
                
                with prod_col1:
                    st.metric(
                        "Randament Estimat Anual",
                        f"{product_info['annual_return_rate'] * 100:.1f}%"
                    )
                
                with prod_col2:
                    st.metric(
                        "Categorie",
                        product_info.get('category', 'N/A').replace('_', ' ').title()
                    )
                
                st.info(f"Acest produs este ajustat pentru profilul dumneavoastră de risc: **{user_profile.get('risk_tolerance', 'Medie')}**")
            else:
                st.info("Informații detaliate despre acest produs vor fi disponibile în curând.")

st.divider()

# =============================================================================
# FOOTER ACTIONS
# =============================================================================

st.markdown("### 🚀 Următorii Pași")

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📧 Trimite Plan pe Email", use_container_width=True):
        st.success("Planul va fi trimis pe email în curând!")

with action_col2:
    if st.button("🔄 Actualizează Profilul", use_container_width=True):
        st.switch_page("pages/2_Product_Recommendations_Florea.py")

with action_col3:
    if st.button("💬 Contactează Consultant", use_container_width=True):
        st.info("Un consultant vă va contacta în 24-48 ore.")

st.divider()

# Last updated info
st.caption(f"*Ultima actualizare: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
st.caption("*Acest plan este generat automat bazat pe profilul dumneavoastră și trebuie revizuit periodic.*")

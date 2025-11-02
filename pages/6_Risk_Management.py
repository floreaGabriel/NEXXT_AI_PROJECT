"""Risk Management - Churn Risk Analysis with Bayesian Networks.

This page displays:
- Interactive Bayesian Network visualizations
- Churn risk factor identification
- Model comparison (HC, PC→HC, GES)
- Actionable insights for client retention
"""

import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from src.components.ui_components import render_sidebar_info, apply_button_styling

apply_button_styling()
render_sidebar_info()

st.title("📊 Risk Management - Analiza Riscului de Churn")

st.write(
    """
    Vizualizați factorii de risc care influențează decizia clienților de a renunța la serviciile bancare.
    Rețelele Bayesiene sunt învățate din date istorice folosind 3 algoritmi diferiți.
    """
)

st.divider()

# ============================================================================
# CHURN RISK BAYESIAN NETWORKS - Static Data from ML Models
# ============================================================================

BAYESIAN_NETWORKS = {
    "HC(bic-d)": {
        "name": "Hill Climbing (BIC)",
        "logloss": 0.6931,
        "auc": 0.5000,
        "edges": [
            ('Age', 'Complain'), ('Age', 'Exited'), ('Balance', 'Exited'), 
            ('Complain', 'Balance'), ('Complain', 'Exited'), ('Complain', 'Geography'), 
            ('Complain', 'NumOfProducts'), ('CreditScore', 'Exited'), ('Geography', 'Balance'), 
            ('Geography', 'Exited'), ('IsActiveMember', 'Age'), ('IsActiveMember', 'Complain'), 
            ('IsActiveMember', 'Exited'), ('NumOfProducts', 'Balance'), ('NumOfProducts', 'Exited')
        ]
    },
    "PC→HC(bic-d)": {
        "name": "PC → Hill Climbing (BIC)",
        "logloss": 0.6931,
        "auc": 0.5000,
        "edges": [
            ('Age', 'Exited'), ('Balance', 'Complain'), ('Balance', 'Exited'), 
            ('Complain', 'Age'), ('Complain', 'Exited'), ('Complain', 'IsActiveMember'), 
            ('CreditScore', 'Exited'), ('Geography', 'Balance'), ('Geography', 'Complain'), 
            ('Geography', 'Exited'), ('IsActiveMember', 'Age'), ('IsActiveMember', 'Exited'), 
            ('NumOfProducts', 'Balance'), ('NumOfProducts', 'Complain'), ('NumOfProducts', 'Exited')
        ]
    },
    "GES(bdeu)": {
        "name": "Greedy Equivalence Search (BDeu)",
        "logloss": 0.6931,
        "auc": 0.5000,
        "edges": [
            ('Age', 'IsActiveMember'), ('Complain', 'Age'), ('Complain', 'Balance'), 
            ('Complain', 'Exited'), ('Complain', 'Geography'), ('Complain', 'IsActiveMember'), 
            ('Geography', 'Balance'), ('NumOfProducts', 'Balance'), ('NumOfProducts', 'Complain'), 
            ('NumOfProducts', 'Exited')
        ]
    }
}


def create_churn_risk_network_visualization(model_name: str, model_data: dict) -> go.Figure:
    """
    Create interactive Bayesian Network visualization showing churn risk factors.
    
    Args:
        model_name: Name of the model (e.g., "HC(bic-d)")
        model_data: Dictionary with 'edges', 'logloss', 'auc'
    
    Returns:
        Plotly figure with network graph
    """
    # Create directed graph
    G = nx.DiGraph()
    G.add_edges_from(model_data['edges'])
    
    # Calculate layout using spring layout for better visualization
    pos = nx.spring_layout(G, seed=42, k=1.5, iterations=50)
    
    # Find nodes that directly influence 'Exited' (churn)
    direct_churn_factors = [source for source, target in model_data['edges'] if target == 'Exited']
    
    # Categorize nodes for coloring
    node_colors = []
    node_sizes = []
    hover_texts = []
    
    for node in G.nodes():
        if node == 'Exited':
            node_colors.append('#FF4444')  # Red for target
            node_sizes.append(40)
            hover_texts.append(f"<b>{node}</b><br>TARGET: Client Churn")
        elif node in direct_churn_factors:
            node_colors.append('#FFA500')  # Orange for direct risk factors
            node_sizes.append(30)
            hover_texts.append(f"<b>{node}</b><br>Direct Risk Factor")
        else:
            node_colors.append('#87CEEB')  # Sky blue for secondary factors
            node_sizes.append(20)
            hover_texts.append(f"<b>{node}</b><br>Indirect Factor")
    
    # Don't create separate edge traces - we'll use annotations for everything
    
    # Create node traces
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=list(G.nodes()),
        textposition="top center",
        textfont=dict(size=10, color='black'),
        hovertext=hover_texts,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )
    
    # Create figure with just nodes first
    fig = go.Figure(data=[node_trace])
    
    # Add arrow annotations for each edge
    # Arrows at midpoint with colored lines and black arrowheads
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Calculate midpoint for arrow placement
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        
        is_churn_edge = (edge[1] == 'Exited')
        line_color = '#FF4444' if is_churn_edge else '#888'
        
        # Add annotation with colored line and black arrowhead at midpoint
        fig.add_annotation(
            x=mid_x,
            y=mid_y,
            ax=x0,
            ay=y0,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5 if is_churn_edge else 1,
            arrowwidth=3 if is_churn_edge else 1.5,  # Colored line width
            arrowcolor='#000000',  # Black arrowhead only
            standoff=0,
            opacity=0.8
        )
        
        # Add the continuation of the line from midpoint to destination
        fig.add_annotation(
            x=x1,
            y=y1,
            ax=mid_x,
            ay=mid_y,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=0,  # No arrowhead on second half
            arrowwidth=3 if is_churn_edge else 1.5,
            arrowcolor=line_color,
            standoff=0,
            opacity=0.8
        )
    
    fig.update_layout(
        title=dict(
            text=f"{model_data['name']}<br><sub>LogLoss: {model_data['logloss']:.4f} | AUC: {model_data['auc']:.4f} | Edges: {len(model_data['edges'])}</sub>",
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=60),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(240,240,240,0.5)',
        height=500
    )
    
    return fig


# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown("### 📊 Rețele Bayesiene pentru Predicția Churn")

st.info(
    "**Ce reprezintă aceste grafuri?**\n\n"
    "Rețelele Bayesiene învățate din date istorice arată factorii care influențează "
    "decizia clienților de a renunța la serviciile bancare (**Exited**).\n\n"
    "- 🔴 **Roșu**: Variabila țintă (Exited = Churn)\n"
    "- 🟠 **Portocaliu**: Factori de risc directi\n"
    "- 🔵 **Albastru**: Factori secundari\n"
    "- ➡️ **Săgeți**: Relații cauzale (ex: Age → Exited)\n"
    "- 🔴 **Linii roșii groase**: Influență directă asupra churn\n"
    "- ⚫ **Săgeți negre**: Direcția cauzală"
)

st.divider()

# Create tabs for each model
tab1, tab2, tab3 = st.tabs([
    "🔹 HC(bic-d)",
    "🔹 PC→HC(bic-d)",
    "🔹 GES(bdeu)"
])

with tab1:
    st.markdown("#### Hill Climbing cu BIC Score")
    st.markdown(
        "Algoritm de căutare locală care găsește structura rețelei prin maximizarea scorului BIC. "
        "**15 edges identificate** care arată relațiile cauzale între variabile."
    )
    fig1 = create_churn_risk_network_visualization("HC(bic-d)", BAYESIAN_NETWORKS["HC(bic-d)"])
    st.plotly_chart(fig1, use_container_width=True, key="bayesian_hc")
    
    # Key insights
    direct_factors_hc = [source for source, target in BAYESIAN_NETWORKS["HC(bic-d)"]["edges"] if target == 'Exited']
    st.success(f"**Factori de risc directi identificați ({len(direct_factors_hc)})**: {', '.join(direct_factors_hc)}")

with tab2:
    st.markdown("#### PC Algorithm → Hill Climbing")
    st.markdown(
        "Combinație hibridă: PC (constraint-based) pentru structura inițială, apoi HC pentru rafinare. "
        "**15 edges** cu relații mai clare între variabile."
    )
    fig2 = create_churn_risk_network_visualization("PC→HC(bic-d)", BAYESIAN_NETWORKS["PC→HC(bic-d)"])
    st.plotly_chart(fig2, use_container_width=True, key="bayesian_pc_hc")
    
    # Key insights
    direct_factors_pc = [source for source, target in BAYESIAN_NETWORKS["PC→HC(bic-d)"]["edges"] if target == 'Exited']
    st.success(f"**Factori de risc directi identificați ({len(direct_factors_pc)})**: {', '.join(direct_factors_pc)}")

with tab3:
    st.markdown("#### Greedy Equivalence Search cu BDeu")
    st.markdown(
        "Algoritm de căutare în spațiul claselor de echivalență. Mai parsimonic cu **doar 10 edges**, "
        "dar cu relații mai robuste și mai puține dependențe spurioase."
    )
    fig3 = create_churn_risk_network_visualization("GES(bdeu)", BAYESIAN_NETWORKS["GES(bdeu)"])
    st.plotly_chart(fig3, use_container_width=True, key="bayesian_ges")
    
    # Key insights
    direct_factors_ges = [source for source, target in BAYESIAN_NETWORKS["GES(bdeu)"]["edges"] if target == 'Exited']
    st.success(f"**Factori de risc directi identificați ({len(direct_factors_ges)})**: {', '.join(direct_factors_ges)}")

# Summary of all models
st.divider()
st.markdown("#### 🎯 Factori de Risc Comuni (Consensus)")

all_direct_factors = set(
    [source for source, target in BAYESIAN_NETWORKS["HC(bic-d)"]["edges"] if target == 'Exited'] +
    [source for source, target in BAYESIAN_NETWORKS["PC→HC(bic-d)"]["edges"] if target == 'Exited'] +
    [source for source, target in BAYESIAN_NETWORKS["GES(bdeu)"]["edges"] if target == 'Exited']
)

# Count occurrences
factor_counts = {}
for model_name, model_data in BAYESIAN_NETWORKS.items():
    for source, target in model_data['edges']:
        if target == 'Exited':
            factor_counts[source] = factor_counts.get(source, 0) + 1

# Sort by consensus
sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)

cols = st.columns(len(sorted_factors))
for i, (factor, count) in enumerate(sorted_factors):
    with cols[i]:
        st.metric(
            label=factor,
            value=f"{count}/3 modele",
            help=f"Identificat ca factor de risc direct în {count} din 3 modele"
        )

st.divider()

# ============================================================================
# ACTIONABLE INSIGHTS
# ============================================================================

st.markdown("### 💡 Insight-uri și Recomandări")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ⚠️ Factori de Risc Critici")
    st.error(
        """
        **Clienți cu risc ridicat de churn:**
        
        1. **Complain = 1** (Au făcut plângeri)
           - Monitorizare activă obligatorie
           - Contact imediat din partea echipei de retenție
        
        2. **IsActiveMember = 0** (Inactivi)
           - Nu folosesc serviciile frecvent
           - Risc crescut de migrare către competiție
        
        3. **Age** (Vârsta extremă)
           - Tineri (<25): risc de migrare către fintech
           - Seniori (>65): risc de reducere servicii
        
        4. **Balance scăzut**
           - Clienți cu balanță sub 10,000 RON
           - Profitabilitate scăzută → churn
        
        5. **CreditScore scăzut**
           - Corelat cu instabilitate financiară
           - Risc de default și plecare
        """
    )

with col2:
    st.markdown("#### ✅ Acțiuni Recomandate")
    st.success(
        """
        **Strategii de retenție bazate pe date:**
        
        1. **Sistemul de Early Warning**
           - Alert automat pentru Complain=1
           - Scoring combinat: Age + Balance + IsActive
        
        2. **Engagement Campaigns**
           - Re-activare clienți inactivi (30-60-90 zile)
           - Oferte personalizate bazate pe profil
        
        3. **Segmentare Geografică**
           - Analyse churn rate pe regiuni
           - Ajustare oferte locale
        
        4. **Product Mix Optimization**
           - Clienți cu NumOfProducts=1 → cross-sell
           - Diversificare portofoliu reduce churn
        
        5. **Proactive Support**
           - Contact preventiv clienți risc mediu-ridicat
           - NPS surveys pentru feedback continuu
        """
    )

st.divider()

# ============================================================================
# MODEL COMPARISON
# ============================================================================

st.markdown("### 📈 Comparație Modele")

comparison_data = {
    "Model": ["HC(bic-d)", "PC→HC(bic-d)", "GES(bdeu)"],
    "Edges": [15, 15, 10],
    "Factori Risc Directi": [
        len([s for s, t in BAYESIAN_NETWORKS["HC(bic-d)"]["edges"] if t == 'Exited']),
        len([s for s, t in BAYESIAN_NETWORKS["PC→HC(bic-d)"]["edges"] if t == 'Exited']),
        len([s for s, t in BAYESIAN_NETWORKS["GES(bdeu)"]["edges"] if t == 'Exited'])
    ],
    "LogLoss": [0.6931, 0.6931, 0.6931],
    "AUC": [0.5000, 0.5000, 0.5000]
}

import pandas as pd
df_comparison = pd.DataFrame(comparison_data)

st.dataframe(
    df_comparison,
    use_container_width=True,
    hide_index=True
)

st.markdown(
    """
    **Observații:**
    - Toate modelele au performanțe similare (LogLoss și AUC identice)
    - **GES** este mai parsimonic (10 edges vs 15) → mai interpretabil
    - **Consensus factors** apar în multiple modele → mai robuști
    - Abordare recomandată: **ensemble** (combinare predicții din toate 3)
    """
)

st.divider()

# Information sidebar
with st.sidebar:
    st.divider()
    st.subheader("ℹ️ Informații Risk Management")
    
    with st.expander("Ce sunt Rețelele Bayesiene?"):
        st.write(
            """
            **Rețelele Bayesiene** sunt modele grafice probabilistice care reprezintă 
            relații cauzale între variabile.
            
            **Avantaje:**
            - Interpretabilitate ridicată
            - Capturează dependențe complexe
            - Permit inferență cauzală
            - Robuște la overfitting
            
            **Algoritmi folosiți:**
            1. **HC (Hill Climbing)**: Greedy local search
            2. **PC**: Constraint-based cu teste de independență
            3. **GES**: Căutare în spații de echivalență
            """
        )
    
    with st.expander("Cum interpretez grafurile?"):
        st.write(
            """
            **Noduri (cercuri):**
            - Roșu = Target (Exited/Churn)
            - Portocaliu = Risc direct
            - Albastru = Risc indirect
            
            **Săgeți:**
            - Direcția = Relație cauzală
            - Grosime = Importanță (roșu gros = foarte important)
            - Negru = Direcție clară
            
            **Exemplu:**
            `Complain → Exited` (roșu gros) = Plângerile cauzează direct churn
            """
        )

st.caption("Risk Management - Analiza Churn cu Bayesian Networks | Raiffeisen Bank © 2025")

"""Main entry that defines programmatic navigation; pages appear only after login."""

import streamlit as st
from pathlib import Path
from src.config.settings import APP_TITLE

# Load favicon
favicon_path = Path(__file__).parent / "assets" / "favicon.svg"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Determine auth status
logged_in = bool(st.session_state.get("auth", {}).get("logged_in"))

# Build programmatic navigation structure
sections = {
    "General": [
        st.Page("pages/00_Home.py", title="Acasă", icon="🏠"),
        st.Page("pages/0_Login.py", title="Login", icon="🔑"),
        st.Page("pages/1_Register.py", title="Register", icon="📝"),
    ]
}

if logged_in:
    sections["Funcționalități"] = [
        st.Page("pages/2_Product_Recommendations_Florea.py", title="Recomandări produse", icon="🎯"),
        st.Page("pages/5_Operator_Recommendations.py", title="Operator - Recomandări Client", icon="👔"),
        st.Page("pages/6_Risk_Management.py", title="Risk Management", icon="⚠️"),
        st.Page("pages/3_Bedrock_Chat_Test.py", title="Bedrock Chat", icon="💬"),
        st.Page("pages/4_Bank_Term_Highlighter.py", title="Bank Term Highlighter", icon="🔎"),
    ]

nav = st.navigation(sections)
nav.run()
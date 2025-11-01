"""Main Streamlit application for Raiffeisen Bank AI Solutions."""

import streamlit as st
from pathlib import Path
from src.config.settings import APP_TITLE
from src.components.ui_components import render_sidebar_info, apply_button_styling

# Load favicon
favicon_path = Path(__file__).parent / "assets" / "favicon.svg"

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply button styling
apply_button_styling()

# Render sidebar
render_sidebar_info()

# Main content
st.title("AI-Powered Banking Solutions")

st.divider()

# Welcome section
st.subheader("Welcome to NEXXT AI Hackathon")
st.write(
    """
    Explore cutting-edge AI solutions for modern banking challenges.
    Select a use case from the sidebar to get started.
    """
)

st.divider()

# Feature cards
st.subheader("Challenge Areas")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### 🔍 Financial Data Analysis")
        st.write(
            """
            Multi-agent system for automated analysis of financial data, 
            risk assessment, and intelligent reporting.
            """
        )
    
    with st.container(border=True):
        st.markdown("#### 📋 Compliance & Regulations")
        st.write(
            """
            AI-powered tool for supporting compliance checks, 
            KYC verification, and AML monitoring.
            """
        )
    
    with st.container(border=True):
        st.markdown("#### 🎯 Product Recommendations")
        st.write(
            """
            Personalized banking product recommendations based on 
            customer profile and financial goals.
            """
        )

with col2:
    with st.container(border=True):
        st.markdown("#### 💬 Customer Service")
        st.write(
            """
            Intelligent chatbot and virtual assistant for enhanced 
            customer interactions and support.
            """
        )
    
    with st.container(border=True):
        st.markdown("#### 📞 Call Center Analytics")
        st.write(
            """
            Transcription and summarization system for call center 
            conversations with sentiment analysis.
            """
        )

# Footer
st.divider()
st.caption("Built with OpenAI Agents SDK, scikit-learn, and Streamlit | NEXXT AI Hackathon 2025")
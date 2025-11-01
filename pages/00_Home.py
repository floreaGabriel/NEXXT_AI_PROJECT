"""Home page content (shown via programmatic navigation)."""

import streamlit as st
from src.components.ui_components import render_sidebar_info, apply_button_styling

apply_button_styling()
render_sidebar_info()

st.title("AI-Powered Banking Solutions")

st.divider()

# Top quick links
nav_c1, nav_c2 = st.columns(2)
with nav_c1:
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/0_Login.py")
with nav_c2:
    if st.button("Register", use_container_width=True):
        st.switch_page("pages/1_Register.py")

# Welcome section
st.subheader("Welcome to NEXXT AI Hackathon")
st.write(
    """
    Explore cutting-edge AI solutions for modern banking challenges.
    Select a use case from the navigation to get started.
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

st.divider()
st.caption("Built with OpenAI Agents SDK, scikit-learn, and Streamlit | NEXXT AI Hackathon 2025")

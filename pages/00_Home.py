"""Home page content (shown via programmatic navigation)."""

import streamlit as st
from src.components.ui_components import render_sidebar_info, apply_button_styling

# Custom CSS for centered title, yellow hover buttons, and hook section
st.markdown("""
<style>
    /* Center the title */
    h1 {
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Yellow hover effect for buttons */
    .stButton > button {
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #FFD700 !important;
        color: #000000 !important;
        border-color: #FFD700 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
    }
    
    /* Hook section styling */
    .hook-container {
        background: linear-gradient(75deg, #000000 0%, #FFD700 100%);
        padding: 2.5rem 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
    }
    
    .hook-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hook-text {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.95);
        line-height: 1.6;
        margin-bottom: 0;
    }
    
    .highlight {
        color: #FFD700;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

apply_button_styling()
render_sidebar_info()

st.title("ShyAI")

st.divider()

# Top quick links
nav_c1, nav_c2 = st.columns(2)
with nav_c1:
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/0_Login.py")
with nav_c2:
    if st.button("Register", use_container_width=True):
        st.switch_page("pages/1_Register.py")

# Hook section - Enhanced and catchy
st.markdown("""
<div class="hook-container">
    <div class="hook-title">💡 Economisești Mai Inteligent, Fără Bătăi de Cap</div>
    <div class="hook-text">
        ShyAI este <span class="highlight">robotul tău prietenos</span> care lucrează în fundal, 
        analizează obiceiurile tale financiare și îți creează <span class="highlight">planuri personalizate</span> 
        de economii — <strong>simplu, sigur și eficient</strong>. 
        <br><br>
        🚀 Fără chatbot-uri complicate. Fără incertitudini. Doar recomandări clare, adaptate ție.
    </div>
</div>
""", unsafe_allow_html=True)


st.divider()
st.caption("Built with OpenAI Agents SDK, scikit-learn, and Streamlit | NEXXT AI Hackathon 2025")

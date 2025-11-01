"""UI components for consistent Raiffeisen Bank branding."""

import streamlit as st


def apply_button_styling():
    """Apply minimal CSS for button text color only."""
    st.markdown(
        """
        <style>
        /* Button text color */
        .stButton button {
            color: #2b2d33 !important;
        }
        
        .stButton button:hover {
            color: #2b2d33 !important;
        }
        
        /* Download button text color */
        .stDownloadButton button {
            color: #2b2d33 !important;
        }
        
        .stDownloadButton button:hover {
            color: #2b2d33 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_info():
    """Render sidebar information with logo."""
    # Logo at the top of sidebar
    st.logo("assets/Raiffeisen Bank.svg", icon_image="assets/Raiffeisen Bank.svg")
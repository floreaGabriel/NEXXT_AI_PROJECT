"""Login Page - Simple in-memory authentication for demo/testing.

Stores users in Streamlit session_state (in-memory). Intended only for demos.
"""

import hashlib
import streamlit as st
from src.components.ui_components import render_sidebar_info, apply_button_styling


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _init_db():
    if "users_db" not in st.session_state:
        st.session_state["users_db"] = {}


apply_button_styling()
render_sidebar_info()

st.title("Autentificare")

# Top nav shortcuts
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    st.page_link("pages/0_Register.py", label="Nu ai cont? Înregistrează-te →")
with col_nav2:
    st.page_link("pages/1_Product_Recommendations_Sabin.py", label="Recomandări produse →")

st.divider()

_init_db()

with st.form("login_form", clear_on_submit=False, border=True):
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Parolă", type="password", key="login_password")
    submitted = st.form_submit_button("Autentifică-te", type="primary", use_container_width=True)

    if submitted:
        users = st.session_state["users_db"]
        if email in users and users[email]["password_hash"] == _hash_password(password):
            st.session_state["auth"] = {"logged_in": True, "email": email}
            # Load profile into session for convenience
            st.session_state["user_profile"] = users[email]["profile"]
            st.success("Autentificare reușită!")
            st.page_link("pages/1_Product_Recommendations_Sabin.py", label="Continuă la Recomandări →")
        else:
            st.error("Email sau parolă invalide.")

st.caption("Demo: autentificare în memorie, doar pentru testare.")

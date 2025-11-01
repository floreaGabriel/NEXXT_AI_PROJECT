"""Login Page - Authentication with database support.

Checks both in-memory session_state and Postgres database for user credentials.
"""

import hashlib
import streamlit as st
from src.components.ui_components import render_sidebar_info, apply_button_styling
from src.utils import db as app_db


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
    if st.button("Nu ai cont? Înregistrează-te →", use_container_width=True):
        st.switch_page("pages/1_Register.py")
with col_nav2:
    if st.button("Recomandări produse →", use_container_width=True):
        st.switch_page("pages/2_Product_Recommendations_Florea.py")

st.divider()

_init_db()

with st.form("login_form", clear_on_submit=False, border=True):
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Parolă", type="password", key="login_password")
    submitted = st.form_submit_button("Autentifică-te", type="primary", use_container_width=True)

    if submitted:
        # First, try to authenticate from database
        user_from_db = None
        try:
            app_db.init_users_table()
            user_from_db = app_db.get_user_by_email(email)
        except Exception:
            pass  # Database not configured, will check session_state only
        
        authenticated = False
        user_profile = None
        
        # Check database authentication
        if user_from_db and user_from_db.get("password_hash") == _hash_password(password):
            authenticated = True
            # Build profile from database data
            user_profile = {
                "first_name": user_from_db.get("first_name", ""),
                "last_name": user_from_db.get("last_name", ""),
                "age": user_from_db.get("age"),
                "marital_status": user_from_db.get("marital_status", ""),
                "employment_status": user_from_db.get("employment_status", ""),
                "has_children": user_from_db.get("has_children", False),
                "number_of_children": user_from_db.get("number_of_children", 0),
                # Add extras from JSONB
                **user_from_db.get("extra", {}),
            }
        else:
            # Fallback to session_state (for backwards compatibility)
            users = st.session_state["users_db"]
            if email in users and users[email]["password_hash"] == _hash_password(password):
                authenticated = True
                user_profile = users[email]["profile"]
        
        if authenticated and user_profile:
            st.session_state["auth"] = {"logged_in": True, "email": email}
            st.session_state["user_profile"] = user_profile
            st.session_state["redirect_to_recommendations"] = True
            st.success("Autentificare reușită!")
        else:
            st.error("Email sau parolă invalide.")

# Handle redirect after successful login (outside form)
if st.session_state.get("redirect_to_recommendations"):
    st.session_state.pop("redirect_to_recommendations")
    if st.button("Continuă la Recomandări →", type="primary", use_container_width=True):
        st.switch_page("pages/2_Product_Recommendations_Florea.py")

st.caption("Demo: autentificare cu suport pentru baza de date.")

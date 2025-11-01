"""Register Page - Collects user details and creates a demo profile.

Persists to Streamlit session_state (in-memory). Intended only for demos.
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

st.title("Înregistrare cont")

# Top nav shortcuts
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("Ai deja cont? Autentifică-te →", use_container_width=True):
        st.switch_page("pages/0_Login.py")
with col_nav2:
    if st.button("Recomandări produse →", use_container_width=True):
        st.switch_page("pages/2_Product_Recommendations_Florea.py")

st.divider()

_init_db()

with st.form("register_form", clear_on_submit=False, border=True):
    st.subheader("Date de cont")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Parolă", type="password", key="reg_password")

    st.subheader("Profil personal")
    last_name = st.text_input("Nume", key="reg_last_name")
    first_name = st.text_input("Prenume", key="reg_first_name")
    age = st.number_input("Vârstă", min_value=18, max_value=100, value=30, step=1, key="reg_age")

    marital_status = st.selectbox(
        "Stare maritală",
        ["Necăsătorit/ă", "Căsătorit/ă", "Divorțat/ă", "Văduv/ă"],
        index=0,
        key="reg_marital_status",
    )

    employment_status = st.selectbox(
        "Status profesional",
        ["Angajat", "Independent", "Șomer", "Pensionar", "Student"],
        index=0,
        key="reg_employment_status",
    )

    has_children = st.checkbox("Aveți copii?", value=False, key="reg_has_children")
    num_children = 0
    if has_children:
        num_children = st.number_input("Număr copii", min_value=1, max_value=10, value=1, step=1, key="reg_num_children")

    submitted = st.form_submit_button("Creează cont", type="primary", use_container_width=True)

    if submitted:
        if not email or "@" not in email:
            st.error("Vă rugăm introduceți un email valid.")
        elif not password or len(password) < 6:
            st.error("Parola trebuie să aibă cel puțin 6 caractere.")
        elif not last_name or not first_name:
            st.error("Completați nume și prenume.")
        else:
            # Check if user already exists in database first
            existing_user_db = None
            try:
                app_db.init_users_table()
                existing_user_db = app_db.get_user_by_email(email)
            except Exception:
                pass  # Database not configured, will check session_state only
            
            users = st.session_state["users_db"]
            if email in users or existing_user_db is not None:
                st.error("Există deja un cont cu acest email.")
            else:
                # Mock pentru câmpurile nespecificate
                profile = {
                    "marital_status": marital_status,
                    "annual_income": 60000.0,  # mock
                    "age": int(age),
                    "employment_status": employment_status,
                    "has_children": bool(has_children),
                    "risk_tolerance": "Medie",  # mock
                    "financial_goals": ["Economii pe termen lung"],  # mock
                    "first_name": first_name,
                    "last_name": last_name,
                    "number_of_children": int(num_children) if has_children else 0,
                }

                users[email] = {
                    "password_hash": _hash_password(password),
                    "profile": profile,
                }

                st.session_state["auth"] = {"logged_in": True, "email": email}
                st.session_state["user_profile"] = profile
                st.session_state["redirect_to_recommendations"] = True
                st.success("Cont creat cu succes și autentificat!")

                # Persist in Postgres (if configured)
                try:
                    app_db.init_users_table()
                    app_db.upsert_user({
                        "email": email,
                        "password_hash": _hash_password(password),
                        "first_name": first_name,
                        "last_name": last_name,
                        "age": int(age),
                        "marital_status": marital_status,
                        "employment_status": employment_status,
                        "has_children": bool(has_children),
                        "number_of_children": int(num_children) if has_children else 0,
                        # Extras go here (flexible):
                        "annual_income": 60000.0,
                        "risk_tolerance": "Medie",
                        "financial_goals": ["Economii pe termen lung"],
                    })
                    st.success("Utilizator salvat în baza de date.")
                except Exception as db_err:
                    st.warning(f"Nu am putut salva în baza de date: {db_err}")

# Handle redirect after successful registration (outside form)
if st.session_state.get("redirect_to_recommendations"):
    st.session_state.pop("redirect_to_recommendations")
    if st.button("Continuă la Recomandări →", type="primary", use_container_width=True):
        st.switch_page("pages/2_Product_Recommendations_Florea.py")

st.caption("Demo: înregistrare cu salvare în baza de date PostgreSQL.")

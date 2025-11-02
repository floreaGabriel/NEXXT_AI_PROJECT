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
    """Render sidebar information with logo and logout button."""
    # Logo at the top of sidebar
    st.logo("assets/Raiffeisen Bank.svg", icon_image="assets/Raiffeisen Bank.svg")
    
    # Add sticky logout button at the bottom of sidebar
    with st.sidebar:
        # Check if user is logged in
        if st.session_state.get("auth", {}).get("logged_in"):
            user_email = st.session_state.get("auth", {}).get("email", "")
            user_profile = st.session_state.get("user_profile", {})
            first_name = user_profile.get("first_name", "")
            
            # User info section
            st.markdown("---")
            if first_name:
                st.markdown(f"👤 **{first_name}**")
            st.caption(f"📧 {user_email}")
            
            # Sticky logout button at bottom with custom styling
            st.markdown(
                """
                <style>
                .logout-container {
                    position: fixed;
                    bottom: 20px;
                    width: calc(100% - 3rem);
                    padding: 0.5rem 0;
                    background: white;
                    z-index: 999;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True, type="secondary", key="sidebar_logout"):
                # Clear session state
                st.session_state.clear()
                st.success("Deconectat cu succes!")
                st.rerun()
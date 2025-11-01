"""Bedrock Chat Test - Simple chatbot to verify AWS Bedrock (Claude via LiteLLM).

Usage: Enter a message; the page will call the Bedrock-backed agent and display a response.
"""

import asyncio
import streamlit as st

from src.config.settings import AWS_BEDROCK_API_KEY
from src.components.ui_components import render_sidebar_info, apply_button_styling
from agents import Runner
from src.agents.bedrock_chat_agent import bedrock_chat_agent

# Styling + sidebar
apply_button_styling()
render_sidebar_info()

st.title("🔧 Bedrock Chat Test (Claude via LiteLLM)")

# Require login to access chat
if not st.session_state.get("auth", {}).get("logged_in"):
    st.warning("Pentru a accesa chat-ul Bedrock, autentificați-vă sau înregistrați-vă.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("→ Autentificare", use_container_width=True):
            st.switch_page("pages/0_Login.py")
    with c2:
        if st.button("→ Înregistrare", use_container_width=True):
            st.switch_page("pages/1_Register.py")
    st.stop()

st.write(
    """
    This page makes a real request to Claude (via AWS Bedrock and LiteLLM) using the
    OpenAI Agents SDK. Use it to confirm that your Bedrock API key is configured.
    """
)

# Validate API key presence
if not AWS_BEDROCK_API_KEY:
    st.error(
        "Missing Bedrock API key. Please set AWS_BEARER_TOKEN_BEDROCK in your .env file, then restart the app."
    )

st.divider()

# Initialize chat history
if "bedrock_chat_messages" not in st.session_state:
    st.session_state.bedrock_chat_messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm Claude (via AWS Bedrock). Ask me anything to test the connection.",
        }
    ]

# Display chat history
for message in st.session_state.bedrock_chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) 

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Append user message
    st.session_state.bedrock_chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the agent (async) and display result
    with st.chat_message("assistant"):
        with st.spinner("Contacting Claude via Bedrock..."):
            try:
                async def run_chat():
                    return await Runner.run(bedrock_chat_agent, prompt)

                result = asyncio.run(run_chat())
                reply = result.final_output or "(no content from model)"

                st.markdown(reply)
                st.session_state.bedrock_chat_messages.append({
                    "role": "assistant",
                    "content": reply,
                })

                # Optional usage display
                usage = getattr(result.context_wrapper, "usage", None)
                if usage:
                    # Agents SDK Usage fields: requests, input_tokens, output_tokens, total_tokens
                    st.caption(
                        f"tokens_in={usage.input_tokens} · tokens_out={usage.output_tokens} · total={usage.total_tokens} · requests={usage.requests}"
                    )

            except Exception as e:
                st.error(f"Chat error: {str(e)}")
                st.session_state.bedrock_chat_messages.append({
                    "role": "assistant",
                    "content": f"I encountered an error: {str(e)}",
                })

st.divider()
st.caption("If you see a valid response above, your Bedrock API key is working.")

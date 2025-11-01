"""Bedrock Chat Agent for quick API key verification via LiteLLM (Claude).

This agent is intentionally minimal and used by the Streamlit chat test page.
"""

from agents import Agent, ModelSettings
from src.config.settings import build_default_litellm_model

# Minimal assistant: no tools, just a friendly chat persona
bedrock_chat_agent = Agent(
    name="Bedrock Chat Tester",
    instructions=(
        "You are a concise, helpful assistant for Raiffeisen developers. "
        "Answer briefly and clearly. If asked, confirm that you're powered by Claude via AWS Bedrock."
    ),
    model=build_default_litellm_model(),
    model_settings=ModelSettings(include_usage=True),
)

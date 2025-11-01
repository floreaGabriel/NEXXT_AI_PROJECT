"""Product Title Generation Agent - Personalized titles for banking products.

This agent generates immersive, personalized Romanian titles for existing bank
products based on a provided user profile. It is designed to be invoked from the
Streamlit UI and uses the same model configuration as the other agents.
"""

from agents import Agent, ModelSettings  # type: ignore
from src.config.settings import build_default_litellm_model


# Minimal, prompt-only agent: the UI passes product + user context in the prompt.
# We don't expose tools here to keep it simple and predictable for the UI call.
product_title_agent = Agent(
    name="Product Title Crafter",
    instructions=(
        "You create concise, immersive and highly personalized product titles in Romanian "
        "for banking products, tailored to a given user's profile.\n\n"
        "Style and rules:\n"
        "- 6–12 words per title, natural Romanian, clear and professional.\n"
        "- Use polite second person plural (dumneavoastră).\n"
        "- Reflect user's goals, age, family situation and risk tolerance.\n"
        "- Focus on concrete benefits, no unrealistic promises or regulatory violations.\n"
        "- Do NOT use emojis.\n\n"
        "Output strictly JSON in the schema requested in the prompt."
    ),
    model=build_default_litellm_model(),
    model_settings=ModelSettings(include_usage=True),
)

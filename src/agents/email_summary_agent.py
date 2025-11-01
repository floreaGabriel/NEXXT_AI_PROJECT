"""Email Summary Agent - drafts and sends personalized product summaries via email.

This agent composes a Romanian email (no emojis) tailored to the user's profile
and product recommendations, then sends it using the MCP Email Server.
"""

from agents import Agent, ModelSettings  # type: ignore
from agents.mcp import MCPServerStdio
from src.config.settings import build_default_litellm_model
from src.utils.mcp_email_client import get_mcp_email_server_config


email_summary_agent = Agent(
    name="Email Summary Sender",
    instructions=(
        "You compose a concise, professional Romanian email (NO emojis) that summarizes "
        "a user's personalized banking product recommendations. After drafting the email, "
        "call the send_email tool with the provided recipient, subject and the drafted body.\n\n"
        "Guidelines:\n"
        "- Use polite second person plural (dumneavoastră).\n"
        "- Keep it short: 120–200 words.\n"
        "- Focus on the top recommended products; list 3–5 items with 1 sentence each.\n"
        "- Do not invent benefits beyond the provided summaries.\n"
        "- No emojis.\n\n"
        "When done, confirm that the email was sent."
    ),
    mcp_servers=[MCPServerStdio(get_mcp_email_server_config())],
    model=build_default_litellm_model(),
    model_settings=ModelSettings(include_usage=True),
)

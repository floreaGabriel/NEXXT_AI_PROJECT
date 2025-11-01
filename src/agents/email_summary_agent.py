"""Email Summary Agent - drafts and sends personalized product summaries via email.

This agent composes a Romanian email (no emojis) tailored to the user's profile
and product recommendations, then sends it using an SMTP tool.
"""

from agents import Agent, function_tool, ModelSettings  # type: ignore
from src.config.settings import build_default_litellm_model
from src.utils.emailer import send_email as _send_email


@function_tool
def send_email(
    to: str,
    subject: str,
    body: str,
) -> str:
    """Send an email via SMTP to the given recipient and return 'sent' on success."""
    return _send_email(to=to, subject=subject, body=body)


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
    tools=[send_email],
    model=build_default_litellm_model(),
    model_settings=ModelSettings(include_usage=True),
)

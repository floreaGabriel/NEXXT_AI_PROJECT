"""Configuration settings for the Raiffeisen Bank AI Hackathon application."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
# Legacy support (some pages may still reference this)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Primary model API key: AWS Bedrock via LiteLLM
# Expected to be provided in .env as AWS_BEARER_TOKEN_BEDROCK
AWS_BEDROCK_API_KEY = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

# Application Settings
APP_TITLE = "Raiffeisen Bank AI Solutions"
APP_ICON = "assets/Raiffeisen_Bank.svg"

# Model Configuration (LiteLLM)
# Default to Claude 4.5 Sonnet via Anthropic provider; can be overridden via env
DEFAULT_LITELLM_MODEL = os.getenv(
	"DEFAULT_LITELLM_MODEL",
	"global.anthropic.claude-sonnet-4-5-20250929-v1:0",
)
TEMPERATURE = 0.7

# Agent Configuration
MAX_TURNS = 10

# Helpers to construct models for Agents SDK
try:
	# Import lazily so pure config imports don't hard-require Agents SDK
	from agents.extensions.models.litellm_model import LitellmModel  # type: ignore

	def build_default_litellm_model():
		"""Return a LitellmModel configured for AWS Bedrock/Anthropic via LiteLLM.

		Relies on AWS_BEDROCK_API_KEY and DEFAULT_LITELLM_MODEL.
		"""
		return LitellmModel(model=DEFAULT_LITELLM_MODEL, api_key=AWS_BEDROCK_API_KEY)

except Exception:  # pragma: no cover - optional at import time
	# Fallback when Agents SDK (with litellm extra) isn't installed yet
	def build_default_litellm_model():  # type: ignore
		raise RuntimeError(
			"LitellmModel unavailable. Ensure 'openai-agents[litellm]' is installed."
		)
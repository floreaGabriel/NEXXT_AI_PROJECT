"""Agents package initialization.

CRITICAL: This module applies a patch to disable LiteLLM async logging
to prevent event loop conflicts in Streamlit and other environments.
"""

# Apply LiteLLM patch IMMEDIATELY on any agent import
from src.utils.litellm_patch import patch_litellm
patch_litellm()

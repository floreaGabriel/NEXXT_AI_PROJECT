"""Configuration settings for the Raiffeisen Bank AI Hackathon application."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Application Settings
APP_TITLE = "Raiffeisen Bank AI Solutions"
APP_ICON = "assets/Raiffeisen_Bank.svg"

# Model Configuration
DEFAULT_MODEL = "gpt-4.1"
TEMPERATURE = 0.7

# Agent Configuration
MAX_TURNS = 10
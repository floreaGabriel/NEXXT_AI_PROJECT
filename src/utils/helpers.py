"""Helper utilities for the application."""

from typing import Any
import pandas as pd


def format_currency(amount: float, currency: str = "RON") -> str:
    """Format currency values."""
    return f"{amount:,.2f} {currency}"


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format."""
    return api_key and api_key.startswith("sk-") and len(api_key) > 20


def create_sample_dataframe() -> pd.DataFrame:
    """Create sample financial data for demonstration."""
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Transaction": [f"TXN-{i:04d}" for i in range(1, 11)],
            "Amount": [1000 + i * 100 for i in range(10)],
            "Category": ["Deposit", "Withdrawal"] * 5,
        }
    )


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    return text if len(text) <= max_length else text[:max_length] + "..."
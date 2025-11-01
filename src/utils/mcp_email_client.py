"""MCP Email Client Utilities - Helper functions for interacting with the MCP Email Server.

This module provides convenient utilities for integrating the MCP Email Server
with agents and other components of the application.
"""

import os
from pathlib import Path
from agents.mcp import MCPServerStdioParams


def get_mcp_email_server_config() -> MCPServerStdioParams:
    """Get configured parameters for the MCP Email Server.
    
    This function reads SMTP configuration from environment variables
    and returns a properly configured MCPServerStdioParams object that
    can be used with MCPServerStdio.
    
    Environment Variables Used:
        - SMTP_HOST: SMTP server hostname
        - SMTP_PORT: SMTP server port (default: 587)
        - SMTP_USER: SMTP username
        - SMTP_PASSWORD: SMTP password
        - SMTP_TLS: Use TLS encryption (default: true)
        - FROM_EMAIL: Default sender email address
    
    Returns:
        MCPServerStdioParams: Configured server parameters for MCP connection
        
    Example:
        >>> from agents import Agent
        >>> from agents.mcp import MCPServerStdio
        >>> from src.utils.mcp_email_client import get_mcp_email_server_config
        >>> 
        >>> agent = Agent(
        ...     name="Email Agent",
        ...     mcp_servers=[MCPServerStdio(get_mcp_email_server_config())],
        ... )
    """
    # Get the project root and mcp-email directory
    project_root = Path(__file__).parent.parent.parent
    mcp_email_dir = project_root / "src" / "mcp-email"
    
    return MCPServerStdioParams(
        command="python",
        args=["-m", "mcp_email.server"],
        env={
            "PYTHONPATH": str(mcp_email_dir),
            "SMTP_HOST": os.getenv("SMTP_HOST", ""),
            "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
            "SMTP_USER": os.getenv("SMTP_USER", ""),
            "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
            "SMTP_TLS": os.getenv("SMTP_TLS", "true"),
            "FROM_EMAIL": os.getenv("FROM_EMAIL", ""),
        },
    )


def verify_smtp_config() -> tuple[bool, str]:
    """Verify that required SMTP configuration is present.
    
    Returns:
        tuple[bool, str]: (is_valid, message) where is_valid indicates
            if the configuration is complete and message provides details
            
    Example:
        >>> is_valid, message = verify_smtp_config()
        >>> if not is_valid:
        ...     print(f"SMTP configuration error: {message}")
    """
    smtp_host = os.getenv("SMTP_HOST")
    
    if not smtp_host:
        return False, "SMTP_HOST environment variable is not set"
    
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if smtp_user and not smtp_password:
        return False, "SMTP_USER is set but SMTP_PASSWORD is missing"
    
    if smtp_password and not smtp_user:
        return False, "SMTP_PASSWORD is set but SMTP_USER is missing"
    
    return True, "SMTP configuration is valid"

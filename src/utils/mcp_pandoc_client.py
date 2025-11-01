"""MCP Pandoc Client Utilities - Helper functions for document conversion using MCP Pandoc Server.

This module provides convenient utilities for integrating the MCP Pandoc Server
with agents and other components of the application for document format conversions.

The MCP Pandoc server is an external package that provides document conversion
capabilities using pandoc. More info: https://github.com/vivekVells/mcp-pandoc
"""

import os
from pathlib import Path
from agents.mcp import MCPServerStdioParams


def get_mcp_pandoc_server_config() -> MCPServerStdioParams:
    """Get configured parameters for the MCP Pandoc Server.
    
    This function returns a properly configured MCPServerStdioParams object that
    can be used with MCPServerStdio for document conversion operations.
    
    The MCP Pandoc server provides tools for converting documents between various
    formats including:
    - Markdown → PDF, DOCX, HTML, etc.
    - HTML → PDF, DOCX, Markdown, etc.
    - And many more format combinations
    
    Requirements:
        - mcp-pandoc package (installed via pip/uv)
        - pandoc system package (brew install pandoc on macOS)
        - texlive (for PDF conversion: brew install texlive on macOS)
    
    Returns:
        MCPServerStdioParams: Configured server parameters for MCP Pandoc connection
        
    Example:
        >>> from agents import Agent
        >>> from agents.mcp import MCPServerStdio
        >>> from src.utils.mcp_pandoc_client import get_mcp_pandoc_server_config
        >>> 
        >>> agent = Agent(
        ...     name="PDF Converter Agent",
        ...     mcp_servers=[MCPServerStdio(get_mcp_pandoc_server_config())],
        ... )
    
    Note:
        For production use, ensure pandoc and texlive are installed on the system:
        - macOS: brew install pandoc texlive
        - Ubuntu: sudo apt-get install pandoc texlive-xetex
        - Windows: Install from https://pandoc.org and https://miktex.org
    """
    return MCPServerStdioParams(
        command="uvx",
        args=["mcp-pandoc"],
        env=None  # No special environment variables needed for mcp-pandoc
    )

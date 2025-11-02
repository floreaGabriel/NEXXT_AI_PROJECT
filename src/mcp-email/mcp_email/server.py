"""MCP Email Server - Provides email sending capabilities via SMTP.

This server implements the Model Context Protocol (MCP) to expose
email sending functionality through a standardized interface.

Environment Variables:
  - SMTP_HOST (required): SMTP server hostname
  - SMTP_PORT (default: 587): SMTP server port
  - SMTP_USER (optional): SMTP username for authentication
  - SMTP_PASSWORD (optional): SMTP password for authentication
  - SMTP_TLS (default: true): Whether to use TLS encryption
  - FROM_EMAIL (optional): Default sender email address
"""

from __future__ import annotations

import asyncio
import os
import smtplib
from email.message import EmailMessage
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Initialize the MCP server
app = Server("mcp-email")


def _send_email_smtp(to: str, subject: str, body: str, from_email: str | None = None, html: bool = False) -> dict[str, Any]:
    """Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content (plain text or HTML)
        from_email: Optional sender email (overrides FROM_EMAIL env var)
        html: If True, send body as HTML; if False, send as plain text
        
    Returns:
        Dictionary with status and message
        
    Raises:
        RuntimeError: If SMTP configuration is invalid
        ValueError: If recipient email is invalid
    """
    host = os.getenv("SMTP_HOST")
    if not host:
        raise RuntimeError("SMTP_HOST environment variable is not configured")
    
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_TLS", "true").lower() in {"1", "true", "yes"}
    sender = from_email or os.getenv("FROM_EMAIL", user or "no-reply@example.com")

    if not to or "@" not in to:
        raise ValueError(f"Invalid recipient email address: {to}")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    
    # Set content based on html flag
    if html:
        msg.set_content(body, subtype='html')
    else:
        msg.set_content(body)

    try:
        if use_tls:
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as server:
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        
        return {
            "status": "success",
            "message": f"Email sent successfully to {to}",
            "to": to,
            "subject": subject,
        }
    except smtplib.SMTPAuthenticationError as e:
        return {
            "status": "error",
            "message": f"SMTP authentication failed: {str(e)}",
        }
    except smtplib.SMTPException as e:
        return {
            "status": "error",
            "message": f"SMTP error: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
        }


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available email tools."""
    return [
        Tool(
            name="send_email",
            description=(
                "Send an email via SMTP to a recipient. "
                "Requires SMTP configuration via environment variables. "
                "Returns status and confirmation message."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address (required)",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line (required)",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content in plain text or HTML (required)",
                    },
                    "from_email": {
                        "type": "string",
                        "description": "Optional sender email address (overrides FROM_EMAIL env var)",
                    },
                    "html": {
                        "type": "boolean",
                        "description": "If true, send body as HTML email; if false (default), send as plain text",
                        "default": False,
                    },
                },
                "required": ["to", "subject", "body"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution requests."""
    if name != "send_email":
        raise ValueError(f"Unknown tool: {name}")

    to = arguments.get("to")
    subject = arguments.get("subject")
    body = arguments.get("body")
    from_email = arguments.get("from_email")
    html = arguments.get("html", False)

    if not to or not subject or not body:
        raise ValueError("Missing required parameters: to, subject, and body are required")

    # Execute the email sending
    result = _send_email_smtp(to=to, subject=subject, body=body, from_email=from_email, html=html)

    # Format response
    if result["status"] == "success":
        response_text = f"✓ {result['message']}"
    else:
        response_text = f"✗ {result['message']}"

    return [TextContent(type="text", text=response_text)]


async def main():
    """Run the MCP email server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

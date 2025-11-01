"""SMTP email helper used by the Email Summary Agent and UI.

Env vars:
  - SMTP_HOST (required)
  - SMTP_PORT (default 587)
  - SMTP_USER (optional)
  - SMTP_PASSWORD (optional)
  - SMTP_TLS (default true)
  - FROM_EMAIL (fallback to SMTP_USER)
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_email(to: str, subject: str, body: str) -> str:
    host = os.getenv("SMTP_HOST")
    if not host:
        raise RuntimeError("SMTP_HOST is not configured")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_TLS", "true").lower() in {"1", "true", "yes"}
    from_email = os.getenv("FROM_EMAIL", user or "no-reply@example.com")

    if not to or "@" not in to:
        raise ValueError("Invalid 'to' email address")

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

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

    return "sent"

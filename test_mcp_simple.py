#!/usr/bin/env python3
"""Test simplu și direct pentru MCP Email Server."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import asyncio
import nest_asyncio

# Enable nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

print("=" * 70)
print("  TEST MCP EMAIL SERVER (LOCAL - VIA MCP PROTOCOL)")
print("=" * 70)

# Verificare configurație
print("\n✓ Configurație SMTP:")
print(f"   SMTP_HOST: {os.getenv('SMTP_HOST')}")
print(f"   SMTP_USER: {os.getenv('SMTP_USER')}")
print(f"   FROM_EMAIL: {os.getenv('FROM_EMAIL', os.getenv('SMTP_USER'))}")

if not os.getenv('SMTP_HOST'):
    print("\n❌ SMTP_HOST nu este setat!")
    sys.exit(1)

# Test agent
print("\n⏳ Încărcare agent...")

try:
    from agents import Runner
    from src.agents.email_summary_agent import email_summary_agent
    
    print("✓ Agent încărcat cu succes!")
    
    # Email de test
    test_email = os.getenv("SMTP_USER")
    print(f"\n📧 Trimitere email de test la: {test_email}")
    print("   (Agentul va porni MCP Email Server în fundal...)\n")
    
    # Prompt simplu
    prompt = f"""
Trimite un email de test cu aceste detalii:

To: {test_email}
Subject: Test MCP Email Server
Body: 
Bună,

Acesta este un test al noului sistem MCP Email Server.

Dacă primești acest email, înseamnă că totul funcționează perfect!

Detalii:
- Server MCP: Activ (local, fără Docker)
- SMTP: {os.getenv('SMTP_HOST')}
- Protocol: Model Context Protocol

Cu respect,
Sistemul de Email
"""
    
    print("🤖 Agentul procesează cererea...\n")
    
    # Rulează agentul
    async def run_test():
        return await Runner.run(email_summary_agent, prompt)
    
    result = asyncio.run(run_test())
    
    print("\n" + "=" * 70)
    print("  RĂSPUNS DE LA AGENT:")
    print("=" * 70)
    if hasattr(result, 'output'):
        print(result.output)
    else:
        print(result)
    print("=" * 70)
    
    print(f"\n✅ SUCCESS! Verifică emailul la: {test_email}")
    print("   (Nu uita să verifici și folder-ul Spam)")
    
except Exception as e:
    print(f"\n❌ EROARE: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

#!/usr/bin/env python3
"""Test MCP Email Server cu conexiune explicită."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

print("=" * 70)
print("  TEST MCP EMAIL SERVER (CU CONEXIUNE EXPLICITĂ)")
print("=" * 70)

# Verificare configurație
print("\n✓ Configurație SMTP:")
print(f"   SMTP_HOST: {os.getenv('SMTP_HOST')}")
print(f"   SMTP_USER: {os.getenv('SMTP_USER')}")

if not os.getenv('SMTP_HOST'):
    print("\n❌ SMTP_HOST nu este setat!")
    sys.exit(1)

# Test agent
print("\n⏳ Încărcare agent și MCP server...")

try:
    from agents import Runner
    from agents.mcp import MCPServerStdio
    from src.agents.email_summary_agent import email_summary_agent
    from src.utils.mcp_email_client import get_mcp_email_server_config
    
    print("✓ Imports OK!")
    
    # Email de test
    test_email = os.getenv("SMTP_USER")
    print(f"\n📧 Trimitere email de test la: {test_email}")
    
    # Prompt simplu
    prompt = f"""
Trimite un email de test cu aceste detalii:

To: {test_email}
Subject: Test MCP Email Server - Funcționează!
Body: 
Bună,

Acesta este un test al MCP Email Server.

Dacă primești acest email, înseamnă că:
✓ MCP Server pornit cu succes
✓ Conexiune stabilită
✓ SMTP funcțional

Detalii:
- Protocol: Model Context Protocol (stdio)
- SMTP: {os.getenv('SMTP_HOST')}

Cu respect,
MCP Email Server
"""
    
    async def run_with_mcp():
        """Rulează agentul cu MCP server conectat explicit."""
        
        # Creează instanța MCP server
        mcp_server = MCPServerStdio(get_mcp_email_server_config())
        
        print("\n🔌 Conectare la MCP Email Server...")
        
        try:
            # Conectează serverul explicit
            await mcp_server.connect()
            print("   ✓ MCP Server conectat!")
            
            # Creează un agent temporar cu serverul conectat
            from agents import Agent, ModelSettings
            from src.config.settings import build_default_litellm_model
            
            temp_agent = Agent(
                name="Email Summary Sender",
                instructions=email_summary_agent.instructions,
                mcp_servers=[mcp_server],
                model=build_default_litellm_model(),
                model_settings=ModelSettings(include_usage=True),
            )
            
            print("\n🤖 Agentul procesează cererea...\n")
            
            # Rulează agentul
            result = await Runner.run(temp_agent, prompt)
            
            return result
            
        except Exception as e:
            print(f"\n⚠️  Eroare la rulare: {e}")
            raise
    
    result = asyncio.run(run_with_mcp())
    
    print("\n" + "=" * 70)
    print("  RĂSPUNS DE LA AGENT:")
    print("=" * 70)
    if hasattr(result, 'output'):
        print(result.output)
    else:
        print(result)
    print("=" * 70)
    
    print(f"\n✅ SUCCESS! Verifică emailul la: {test_email}")
    
except Exception as e:
    print(f"\n❌ EROARE: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

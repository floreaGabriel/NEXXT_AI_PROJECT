#!/usr/bin/env python3
"""Script rapid de test pentru MCP Email Server - versiune simplificată."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import asyncio
import nest_asyncio

# Enable nested event loops for asyncio compatibility
nest_asyncio.apply()

# Load environment variables
load_dotenv()

print("=" * 70)
print("  TEST RAPID MCP EMAIL SERVER")
print("=" * 70)

# Step 1: Verify SMTP config
print("\n1. Verificare configurație SMTP:")
print(f"   SMTP_HOST: {os.getenv('SMTP_HOST', '❌ NU ESTE SETAT')}")
print(f"   SMTP_PORT: {os.getenv('SMTP_PORT', '587')}")
print(f"   SMTP_USER: {os.getenv('SMTP_USER', '❌ NU ESTE SETAT')}")
print(f"   SMTP_PASSWORD: {'✓ Setat' if os.getenv('SMTP_PASSWORD') else '❌ NU ESTE SETAT'}")
print(f"   FROM_EMAIL: {os.getenv('FROM_EMAIL', os.getenv('SMTP_USER', '❌ NU ESTE SETAT'))}")

if not os.getenv('SMTP_HOST'):
    print("\n❌ SMTP_HOST nu este configurat!")
    print("   Te rog să setezi variabilele în fișierul .env")
    sys.exit(1)

print("\n✓ Configurația SMTP este OK!")

# Step 2: Test the agent
print("\n2. Test agent cu MCP Email Server:")

try:
    from agents import Runner
    from src.agents.email_summary_agent import email_summary_agent
    import asyncio
    print("   ✓ email_summary_agent încărcat cu succes")
    
    # Get test email
    test_email = os.getenv("SMTP_USER")  # Trimite la propriul email
    
    print(f"\n3. Trimitere email de test la: {test_email}")
    print("   (Se va folosi MCP Email Server în fundal...)\n")
    
    # Create a simple test message
    test_prompt = f"""
    Te rog trimite un email de test cu următoarele detalii:
    
    To: {test_email}
    Subject: ✓ Test MCP Email Server - Funcționează!
    Body: 
    Bună ziua,
    
    Acesta este un email de test pentru a verifica funcționalitatea noului MCP Email Server.
    
    Dacă primiți acest mesaj, înseamnă că:
    ✓ MCP Email Server funcționează corect
    ✓ Configurația SMTP este validă
    ✓ Integrarea cu agentul este completă
    
    Detalii tehnice:
    - Protocol: Model Context Protocol (MCP)
    - SMTP Server: {os.getenv('SMTP_HOST')}
    - Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Cu respect,
    Sistemul MCP Email
    """
    
    # Run the agent with asyncio
    result = asyncio.run(Runner.run(email_summary_agent, test_prompt))
    
    print("\n" + "=" * 70)
    print("  RĂSPUNS DE LA AGENT:")
    print("=" * 70)
    print(result.output)
    print("=" * 70)
    
    print(f"\n✅ TEST FINALIZAT CU SUCCES!")
    print(f"   Verifică inbox-ul la {test_email}")
    
except ImportError as e:
    print(f"\n❌ Eroare la import: {e}")
    print("   Asigură-te că toate pachetele sunt instalate:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Eroare la testare: {e}")
    print("\nDetalii eroare:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

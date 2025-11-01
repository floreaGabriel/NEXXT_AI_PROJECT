"""Test: Trimite email profesional cu planul financiar ca PDF atașat.

Folosește componentele existente:
- pdf_converter_direct pentru generare PDF
- mcp-email server pentru trimitere email cu atașament
"""

import asyncio
import os
from pathlib import Path
from agents import Runner, Agent, ModelSettings
from agents.mcp import MCPServerStdio
from src.utils.mcp_email_client import get_mcp_email_server_config
from src.agents.pdf_converter_direct import convert_markdown_to_pdf_direct
from src.config.settings import build_default_litellm_model

# Plan financiar profesional de test
FINANCIAL_PLAN = """# Plan Financiar Personalizat

**Client:** Andrei Popescu  
**Data:** 02 Noiembrie 2025  
**Consultant:** Raiffeisen Banking & Advisory

---

## Rezumat Executiv

Bine ați venit la planul dumneavoastră financiar personalizat! Acest document conține recomandări adaptate profilului și obiectivelor dumneavoastră financiare.

**Profil Client:**
- Vârstă: 35 ani
- Venit Lunar: 8,000 RON
- Status: Angajat permanent
- Obiective: Economii, Investiții, Pensie

---

## Recomandări Produse

### 1. Cont de Economii Super Acces Plus

**Scop:** Constituire fond de urgență (6 luni cheltuieli = 48,000 RON)

**Caracteristici:**
- Dobândă competitivă la vedere
- Acces instant la fonduri
- Fără comisioane de administrare
- Garantat FGDB până la 100,000 EUR

**Strategie recomandat:**
1. Depozit inițial: 10,000 RON
2. Contribuție lunară: 1,500 RON
3. Orizont: 24-30 luni

---

### 2. SmartInvest - Fonduri de Investiții

**Scop:** Creștere capital pe termen mediu-lung (10+ ani)

**Caracteristici:**
- Portofoliu diversificat global
- Gestiune profesională
- Randament țintă: 7-9% anual
- Contribuții lunare flexibile

**Strategie recomandat:**
1. Contribuție lunară: 1,200 RON
2. Profil risc: Mediu (60% acțiuni, 40% obligațiuni)
3. Valoare estimată 10 ani: ~200,000 RON

---

### 3. Fond Pensii Facultative Raiffeisen Acumulare

**Scop:** Asigurare venit suplimentar la pensionare

**Caracteristici:**
- Deducere fiscală: 400 EUR/an
- Randament atractiv pe termen lung
- Flexibilitate contribuții
- Gestiune profesională

**Strategie recomandat:**
1. Contribuție lunară: 400 RON
2. Start imediat (maxim beneficiu din compunere)
3. Valoare estimată la 65 ani: ~350,000 RON

---

## Plan de Implementare

### Luna 1-3: Fundație
- Deschidere Cont Economii Super Acces Plus
- Transfer automat 1,500 RON/lună
- Depozit inițial fond urgență

### Luna 4-6: Investiții
- Planificare SmartInvest cu consultant
- Activare contribuții lunare 1,200 RON
- Selectare profil risc mediu

### Luna 7+: Pensie
- Deschidere Fond Pensii Facultative
- Contribuție lunară 400 RON
- Optimizare deducere fiscală

---

## Proiecție Financiară

| An | Vârstă | Economii | Investiții | Pensie | Total |
|----|--------|----------|------------|--------|-------|
| 1  | 36     | 18,000   | 14,400     | 4,800  | 37,200 |
| 5  | 40     | 48,000   | 85,000     | 28,000 | 161,000 |
| 10 | 45     | 48,000   | 200,000    | 70,000 | 318,000 |
| 30 | 65     | 48,000   | 850,000    | 350,000| 1,248,000 |

*Calculele sunt estimative și nu garantează rezultate specifice.*

---

## Note Importante

1. **Revizuire Periodică:** Recomandăm revizuirea planului la fiecare 6-12 luni
2. **Ajustări:** Planul poate fi adaptat la schimbări în situația financiară
3. **Consultanță:** Consultanță gratuită disponibilă pentru clienții Raiffeisen
4. **Inflație:** Ajustați contribuțiile anual cu rata inflației (5-7%)

---

## Pași Următori

1. Programați consultanță gratuită: **tel. *2000**
2. Pregătiți documente necesare (CI, adeverință venit)
3. Vizitați sucursala sau aplicați online

---

**Raiffeisen Bank România**  
📞 Tel: *2000 (gratuit)  
📧 Email: advisory@raiffeisen.ro  
🌐 Web: www.raiffeisen.ro

*Document generat de NEXXT AI Banking Assistant*  
*Acest plan este orientativ. Consultați un specialist financiar pentru validare.*
"""


async def send_professional_email_with_pdf():
    """Trimite email profesional bancar cu PDF planului financiar atașat."""
    
    print("=" * 80)
    print("TEST: Trimitere Email Profesional cu Plan Financiar PDF")
    print("=" * 80)
    print()
    
    # Step 1: Verifică configurația SMTP
    print("📋 PASO 1: Verificare configurație SMTP...")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    
    if not all([smtp_host, smtp_user, smtp_pass]):
        print("❌ EROARE: SMTP nu este configurat complet în .env")
        print("\nConfigurazione necesară:")
        print("  SMTP_HOST=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USER=your.email@gmail.com")
        print("  SMTP_PASSWORD=your_app_password")
        print("  FROM_EMAIL=your.email@gmail.com")
        return False
    
    print(f"✅ SMTP Host: {smtp_host}")
    print(f"✅ SMTP User: {smtp_user}")
    print(f"✅ SMTP Password: {'*' * len(smtp_pass)} ({len(smtp_pass)} chars)")
    print()
    
    # Step 2: Generează PDF
    print("📋 PASO 2: Generare PDF plan financiar...")
    
    def pdf_progress(msg):
        print(f"  {msg}")
    
    try:
        pdf_path, pdf_message, pdf_logs = convert_markdown_to_pdf_direct(
            FINANCIAL_PLAN,
            "plan_financiar_andrei_popescu.pdf",
            progress_callback=pdf_progress
        )
        print(f"\n✅ PDF generat: {pdf_path}")
        
        # Verifică dimensiunea
        pdf_size = Path(pdf_path).stat().st_size
        print(f"📊 Dimensiune: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
        print()
        
    except Exception as e:
        print(f"❌ EROARE la generare PDF: {e}")
        return False
    
    # Step 3: Pregătește email profesional
    print("📋 PASO 3: Pregătire conținut email profesional...")
    
    recipient_email = input("\n📧 Introdu adresa de email destinatar: ").strip()
    if not recipient_email or '@' not in recipient_email:
        print("❌ Email invalid!")
        return False
    
    # Conținut email profesional bancar
    email_subject = "Planul Dumneavoastră Financiar Personalizat - Raiffeisen Bank"
    
    email_body = f"""Stimate Domn/Doamnă,

Vă mulțumim pentru încrederea acordată Raiffeisen Bank România.

Atașat acestui email veți găsi planul dumneavoastră financiar personalizat, elaborat de echipa noastră de specialiști în consultanță bancară. Documentul conține:

• Analiză detaliată a profilului dumneavoastră financiar
• Recomandări personalizate de produse și servicii bancare
• Strategie de implementare pas cu pas
• Proiecții financiare pe termen mediu și lung

Planul a fost conceput pentru a vă ajuta să vă atingeți obiectivele financiare într-un mod sigur și eficient, adaptat nevoilor și profilului dumneavoastră de risc.

PAȘI URMĂTORI:

1. Revizuiți cu atenție documentul atașat
2. Notați eventualele întrebări sau clarificări necesare
3. Programați o consultanță gratuită cu un specialist Raiffeisen:
   - Telefon: *2000 (apel gratuit din orice rețea)
   - Email: advisory@raiffeisen.ro
   - Online: www.raiffeisen.ro/programare

Echipa noastră de consultanți certificați este la dispoziția dumneavoastră pentru a discuta în detaliu recomandările și a vă ghida în implementarea planului.

Cu stimă,

Echipa Raiffeisen Banking & Advisory
Raiffeisen Bank România

---
📞 Contact: *2000 (gratuit) | 📧 advisory@raiffeisen.ro | 🌐 www.raiffeisen.ro

Acest email și documentul atașat conțin informații confidențiale destinate exclusiv dumneavoastră.
Recomandările sunt orientative și necesită validare cu un consultant financiar certificat.
"""
    
    print(f"✅ Destinatar: {recipient_email}")
    print(f"✅ Subiect: {email_subject}")
    print(f"✅ Conținut: {len(email_body)} caractere")
    print(f"✅ Atașament: {Path(pdf_path).name} ({pdf_size/1024:.1f} KB)")
    print()
    
    # Step 4: Citește PDF ca bytes pentru atașament
    print("📋 PASO 4: Pregătire atașament PDF...")
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        # Encoding base64 pentru atașament
        import base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        print(f"✅ PDF codificat în base64: {len(pdf_base64)} caractere")
        print()
        
    except Exception as e:
        print(f"❌ EROARE la citire PDF: {e}")
        return False
    
    # Step 5: Conectare la MCP Email Server și trimitere
    print("📋 PASO 5: Conectare la MCP Email Server...")
    
    try:
        # Creează MCP server
        mcp_server = MCPServerStdio(get_mcp_email_server_config())
        await mcp_server.connect()
        print("✅ Conectat la MCP Email Server")
        print()
        
        # Creează agent pentru email
        print("📋 PASO 6: Trimitere email cu atașament PDF...")
        
        email_agent = Agent(
            name="Professional Email Sender",
            instructions="""You are a professional email sending assistant.
            
When asked to send an email:
1. Use the send_email tool with the exact parameters provided
2. For attachments, use the attachments parameter with base64 encoded content
3. Confirm successful delivery
4. Be concise and professional

Always use the send_email tool to actually send the email.""",
            mcp_servers=[mcp_server],
            model=build_default_litellm_model(),
            model_settings=ModelSettings(include_usage=True),
        )
        
        # Prompt pentru agent
        prompt = f"""Send a professional banking email with the following details:

TO: {recipient_email}
SUBJECT: {email_subject}

BODY:
{email_body}

ATTACHMENT:
- filename: plan_financiar_andrei_popescu.pdf
- content: {pdf_base64}
- content_type: application/pdf

Please send this email now using the send_email tool with the attachment."""
        
        # Rulează agentul
        result = await Runner.run(email_agent, prompt)
        
        print("\n" + "=" * 80)
        print("✅ EMAIL TRIMIS CU SUCCES!")
        print("=" * 80)
        print(f"\n📧 Destinatar: {recipient_email}")
        print(f"📝 Subiect: {email_subject}")
        print(f"📎 Atașament: plan_financiar_andrei_popescu.pdf ({pdf_size/1024:.1f} KB)")
        print(f"\n💬 Răspuns Agent:")
        if hasattr(result, 'output'):
            print(result.output)
        else:
            print(str(result))
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLET - Verificați inbox-ul (și Spam)!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ EROARE la trimitere email: {e}")
        import traceback
        print("\nTraceback complet:")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("\n🏦 RAIFFEISEN BANK - Test Email Profesional cu PDF")
    print("=" * 80)
    print()
    
    success = asyncio.run(send_professional_email_with_pdf())
    
    print()
    exit(0 if success else 1)

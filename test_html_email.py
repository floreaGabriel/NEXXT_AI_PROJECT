"""Test: Trimite plan financiar ca email HTML profesional Raiffeisen Bank.

Flow complet:
1. Plan financiar în Markdown
2. Conversie la HTML cu design Raiffeisen (galben & alb)
3. Trimitere email HTML prin MCP Email Server
"""

import asyncio
import os
from dotenv import load_dotenv
from agents import Runner, ModelSettings
from agents.mcp import MCPServerStdio
from src.utils.mcp_email_client import get_mcp_email_server_config
from src.utils.html_converter import convert_financial_plan_to_html, clean_markdown_for_email
from src.agents.html_email_agent import html_email_agent

# Load environment variables
load_dotenv()

# Plan financiar de test (Markdown)
FINANCIAL_PLAN_MD = """# Plan Financiar Personalizat

**Client:** Maria Popescu  
**Data:** 02 Noiembrie 2025  
**Consultant:** Raiffeisen Banking & Advisory

---

## Rezumat Executiv

Bine ați venit la planul dumneavoastră financiar personalizat! Acest document conține recomandări adaptate profilului și obiectivelor dumneavoastră financiare.

**Profil Client:**
- Vârstă: 32 ani
- Venit Lunar: 6,500 RON
- Status: Angajat permanent
- Obiective: Economii, Investiții, Educație Copii

---

## Recomandări Produse

### 1. Cont de Economii Super Acces Plus

**Scop:** Constituire fond de urgență (6 luni cheltuieli = 39,000 RON)

**De ce acest produs se potrivește:**
Cu un venit stabil de 6,500 RON/lună și responsabilități familiale, un fond de urgență este esențial. Acest cont oferă:

- Acces instant la fonduri fără penalizări
- Dobândă competitivă la vedere
- Siguranță maximă - garantat FGDB
- Fără comisioane ascunse

**Strategie recomandat:**
1. Depozit inițial: 5,000 RON
2. Contribuție lunară automată: 1,000 RON
3. Orizont completare: 34 luni

---

### 2. SmartInvest - Fonduri de Investiții

**Scop:** Creștere capital pentru educația copilului (orizont 15 ani)

**De ce acest produs se potrivește:**
La 32 de ani cu copil mic, investițiile pe termen lung vă vor asigura resursele pentru educație superioară. Avantaje:

- Portofoliu diversificat global
- Gestiune profesională activă
- Randament țintă: 7-9% anual
- Contribuții lunare flexibile (minim 100 RON)

**Strategie recomandat:**
1. Contribuție lunară: 800 RON (12% din venit)
2. Profil risc: Mediu (60% acțiuni, 40% obligațiuni)
3. Valoare estimată la 15 ani: ~200,000 RON

---

### 3. Fond Pensii Facultative Raiffeisen Acumulare

**Scop:** Asigurare venit suplimentar la pensionare

**De ce acest produs se potrivește:**
Pornind timpuriu, veți beneficia maxim de compunerea dobânzii. Plusuri importante:

- Deducere fiscală: 400 EUR/an (economie ~480 RON/an)
- Randament atractiv pe termen lung (6-8% anual)
- Flexibilitate contribuții
- Siguranță reglementată ASF

**Strategie recomandat:**
1. Contribuție lunară: 300 RON
2. Start imediat (35 ani până la pensionare)
3. Valoare estimată la 67 ani: ~280,000 RON

---

## Plan de Implementare Gradual

### Anul 1-2: Fundație Financiară

**Focusuri principale:**
- Fond urgență: 1,000 RON/lună
- Investiții copil: 800 RON/lună
- Pensie facultativă: 300 RON/lună

**Total alocat:** 2,100 RON/lună (32% din venit)

### Anul 3-5: Consolidare

După completarea fondului de urgență (luna 34):
- Investiții copil: 1,500 RON/lună (creștere)
- Pensie facultativă: 400 RON/lună (creștere)
- Investiții suplimentare: 200 RON/lună

**Total alocat:** 2,100 RON/lună (menținut)

---

## Proiecție Financiară

| An | Vârstă | Fond Urgență | Investiții Copil | Pensie | Total Acumulat |
|----|--------|--------------|------------------|--------|----------------|
| 1  | 33     | 12,000       | 9,600            | 3,600  | 25,200         |
| 3  | 35     | 36,000       | 30,400           | 11,200 | 77,600         |
| 5  | 37     | 39,000       | 60,000           | 19,500 | 118,500        |
| 10 | 42     | 39,000       | 145,000          | 48,000 | 232,000        |
| 15 | 47     | 39,000       | 200,000          | 85,000 | 324,000        |

*Calculele includ estimări conservative de randament și nu garantează rezultate specifice.*

---

## Sfaturi pentru Succes

### 1. Automatizare Totală
Setați toate transferurile automat în ziua salariului - așa nu uitați și nu sunteți tentată să cheltuiți banii.

### 2. Revizuire Regulată
Analizați planul la fiecare 6 luni și ajustați:
- La creșteri salariale
- La schimbări în familie
- La oportunități noi

### 3. Disciplină Financiară
- Evitați datoriile de consum (carduri revolving)
- Păstrați un buget lunar strict
- Investiți 70% din creșterile salariale

### 4. Educație Continuă
- Citiți lunar despre finanțe personale
- Participați la webinarii Raiffeisen
- Consultați-vă anual cu specialistul

---

## Note Importante

**Inflație:** Ajustați contribuțiile anual cu 5-7% pentru a menține puterea de cumpărare.

**Randamente:** Estimările sunt conservative. Rezultatele reale pot varia în funcție de condiții de piață.

**Flexibilitate:** Planul poate fi ajustat oricând la schimbări în circumstanțe.

**Consultanță:** Serviciile de consultanță financiară sunt gratuite pentru clienții Raiffeisen.

---

*Plan generat de NEXXT AI Banking Assistant*  
*Document orientativ - validare necesară cu consultant financiar certificat*
"""


async def send_html_financial_plan_email():
    """Trimite plan financiar ca email HTML profesional Raiffeisen."""
    
    print("=" * 80)
    print("TEST: Email HTML Profesional - Raiffeisen Bank Design")
    print("=" * 80)
    print()
    
    # Step 1: Verifică SMTP
    print("📋 STEP 1: Verificare configurație SMTP...")
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASSWORD", "").strip()
    
    if not smtp_host or not smtp_user or not smtp_pass:
        print("❌ SMTP nu este configurat complet în .env")
        print(f"   SMTP_HOST: {'✅' if smtp_host else '❌'}")
        print(f"   SMTP_USER: {'✅' if smtp_user else '❌'}")
        print(f"   SMTP_PASSWORD: {'✅' if smtp_pass else '❌'}")
        return False
    
    print(f"✅ SMTP: {smtp_host}")
    print(f"✅ User: {smtp_user}")
    print(f"✅ Pass: {'*' * len(smtp_pass)} ({len(smtp_pass)} chars)")
    print()
    
    # Step 2: Email destinatar
    recipient = "sabinstan19@gmail.com"
    print(f"📧 Email destinatar: {recipient}")
    print()
    
    # Step 3: Curăță și convertește Markdown la HTML
    print("📋 STEP 2: Conversie Markdown → HTML Raiffeisen...")
    
    # Date client pentru personalizare
    client_name = "Maria Popescu"
    client_age = 32
    client_income = 78000  # RON/an
    
    # Curăță markdown
    cleaned_md = clean_markdown_for_email(FINANCIAL_PLAN_MD)
    print(f"✅ Markdown curățat: {len(cleaned_md)} caractere")
    
    # Convertește la HTML
    html_content = convert_financial_plan_to_html(
        cleaned_md,
        client_name=client_name,
        client_age=client_age,
        client_income=client_income
    )
    print(f"✅ HTML generat: {len(html_content)} caractere")
    print(f"✅ Design: Raiffeisen Bank (Galben #FFED00 & Alb)")
    print()
    
    # Step 4: Conectare MCP Email Server
    print("📋 STEP 3: Conectare la MCP Email Server...")
    
    try:
        mcp_server = MCPServerStdio(get_mcp_email_server_config())
        await mcp_server.connect()
        print("✅ MCP Email Server conectat")
        print()
        
    except Exception as e:
        print(f"❌ Eroare conexiune MCP: {e}")
        return False
    
    # Step 5: Trimite email HTML
    print("📋 STEP 4: Trimitere email HTML...")
    print(f"📧 Către: {recipient}")
    print(f"📝 Subiect: Planul Dumneavoastră Financiar Personalizat - Raiffeisen Bank")
    print(f"🎨 Format: HTML (design Raiffeisen)")
    print()
    
    try:
        # Creează agent cu MCP server
        from src.config.settings import build_default_litellm_model
        from agents import ModelSettings
        
        # Configurează agentul cu MCP server
        html_email_agent.mcp_servers = [mcp_server]
        html_email_agent.model = build_default_litellm_model()
        html_email_agent.model_settings = ModelSettings(include_usage=True)
        
        # Prompt pentru agent
        prompt = f"""Send an HTML email with the following details:

RECIPIENT: {recipient}
SUBJECT: Planul Dumneavoastră Financiar Personalizat - Raiffeisen Bank

HTML BODY (complete HTML document with Raiffeisen branding):
{html_content}

CRITICAL INSTRUCTIONS:
- Use send_email tool
- Set html parameter to boolean true (not string "true", but actual boolean true)
- The html parameter enables HTML rendering in email clients
- Send immediately without modifications to the HTML content

Please send this professional HTML email now using send_email tool with html=true."""
        
        # Rulează agentul
        result = await Runner.run(html_email_agent, prompt)
        
        print("\n" + "=" * 80)
        print("✅ EMAIL HTML TRIMIS CU SUCCES!")
        print("=" * 80)
        print(f"\n📧 Destinatar: {recipient}")
        print(f"📝 Subiect: Planul Dumneavoastră Financiar Personalizat - Raiffeisen Bank")
        print(f"🎨 Design: Corporate Raiffeisen (Galben & Alb)")
        print(f"📊 Dimensiune HTML: {len(html_content)/1024:.1f} KB")
        
        if hasattr(result, 'output'):
            print(f"\n💬 Răspuns Agent: {result.output}")
        
        print("\n" + "=" * 80)
        print("✅ Verificați inbox-ul (și folder Spam)!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ EROARE la trimitere: {e}")
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("\n🏦 RAIFFEISEN BANK - Email HTML Profesional")
    print("=" * 80)
    print("Design: Galben #FFED00 & Alb | Responsive | Corporate Branding")
    print("=" * 80)
    print()
    
    success = asyncio.run(send_html_financial_plan_email())
    exit(0 if success else 1)

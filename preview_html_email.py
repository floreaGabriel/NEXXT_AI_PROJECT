"""Preview HTML Email - Generează și deschide în browser pentru vizualizare."""

from src.utils.html_converter import convert_financial_plan_to_html, clean_markdown_for_email
from pathlib import Path

# Plan financiar de test
PLAN_MD = """# Plan Financiar Personalizat

**Client:** Maria Popescu  
**Data:** 02 Noiembrie 2025

---

## Rezumat Executiv

Bine ați venit la planul dumneavoastră financiar personalizat!

**Profil Client:**
- Vârstă: 32 ani
- Venit Lunar: 6,500 RON  
- Obiective: Economii, Investiții, Educație

---

## Recomandări Produse

### 1. Cont de Economii Super Acces Plus

**Scop:** Fond de urgență (39,000 RON)

Cu un venit stabil de 6,500 RON/lună, un fond de urgență este esențial:

- Acces instant la fonduri
- Dobândă competitivă
- Siguranță FGDB
- Fără comisioane

**Strategie:**
1. Depozit inițial: 5,000 RON
2. Contribuție lunară: 1,000 RON
3. Completare în 34 luni

---

### 2. SmartInvest - Fonduri Investiții

**Scop:** Educație copil (15 ani)

Investiții pe termen lung pentru educație:

- Portofoliu diversificat
- Randament 7-9% anual
- Contribuții flexibile
- Gestiune profesională

**Strategie:**
1. Lunar: 800 RON
2. Risc: Mediu
3. Estimare 15 ani: 200,000 RON

---

## Proiecție Financiară

| An | Vârstă | Economii | Investiții | Total |
|----|--------|----------|------------|-------|
| 1  | 33     | 12,000   | 9,600      | 21,600 |
| 3  | 35     | 36,000   | 30,400     | 66,400 |
| 5  | 37     | 39,000   | 60,000     | 99,000 |
| 10 | 42     | 39,000   | 145,000    | 184,000 |

---

## Pași Următori

- Automatizați transferurile
- Revizuiți planul semestrial
- Consultați specialist Raiffeisen
- Ajustați la creșteri salariu

---

*Plan generat de NEXXT AI Banking Assistant*
"""

# Generează HTML
print("🎨 Generare preview HTML...")

cleaned = clean_markdown_for_email(PLAN_MD)
html = convert_financial_plan_to_html(
    cleaned,
    client_name="Maria Popescu",
    client_age=32,
    client_income=78000
)

# Salvează în fișier
output_file = Path.home() / "Downloads" / "preview_raiffeisen_email.html"
output_file.write_text(html, encoding='utf-8')

print(f"✅ HTML generat: {output_file}")
print(f"📊 Dimensiune: {len(html)/1024:.1f} KB")
print(f"\n🌐 Deschide fișierul în browser pentru preview!")
print(f"   {output_file}")

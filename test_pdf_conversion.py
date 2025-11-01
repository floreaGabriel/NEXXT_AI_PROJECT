"""Test script for PDF conversion functionality using MCP Pandoc.

This script tests the markdown to PDF conversion using the PDF converter agent.
It creates a sample financial plan in Markdown and converts it to PDF.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.pdf_converter_agent import convert_markdown_to_pdf


def test_pdf_conversion():
    """Test converting a sample financial plan to PDF."""
    
    # Sample markdown financial plan
    sample_plan = """# Plan Financiar Personalizat

## 1. Rezumat Executiv

Clientul este un profesionist în vârstă de 35 de ani cu venituri stabile și obiective financiare clare pe termen mediu și lung. Strategia recomandată include diversificarea economiilor prin produse bancare adaptate profilului de risc moderat.

### Obiective Principale
- Creștere economii pentru achiziție locuință în 5-7 ani
- Protecție financiară familie
- Investiții diversificate pentru pensionare

### Produse Selectate
1. **Cont de Economii Super Acces Plus** - pentru fond de urgență
2. **Depozit Fresh Money** - pentru obiective pe termen scurt
3. **Fonduri de Investiții Raiffeisen** - pentru creștere pe termen lung

---

## 2. Analiza Situației Actuale

### Profil Financiar
- **Vârstă:** 35 ani
- **Etapă de viață:** Profesionist în carieră, familie tânără
- **Venit anual estimat:** 60,000 - 80,000 RON
- **Situație familială:** Căsătorit, un copil
- **Status profesional:** Angajat full-time, poziție stabilă
- **Toleranță la risc:** Moderat - dorește echilibru între siguranță și creștere

### Obiective Financiare

**Termen Scurt (1-3 ani):**
- Constituire fond de urgență (6 luni cheltuieli)
- Economii pentru vacanțe și cheltuieli neprevăzute

**Termen Mediu (3-7 ani):**
- Acumulare avans pentru locuință (30% din valoare)
- Economii pentru educația copilului

**Termen Lung (7+ ani):**
- Fond de pensionare complementară
- Independență financiară la 60 ani

---

## 3. Strategia de Produse Recomandate

### 3.1 Cont de Economii Super Acces Plus

**De ce acest produs:**
Oferă flexibilitate maximă pentru fondul de urgență, cu acces instant la bani și dobândă competitivă. Este esențial pentru siguranța financiară pe termen scurt.

**Beneficii principale:**
- Acces 24/7 la economii prin Internet Banking și Mobile Banking
- Dobândă progresivă în funcție de sold
- Fără comisioane pentru operațiuni online
- Garanție depozite până la 100,000 EUR
- Lichiditate totală - retrageri fără penalizări

**Mod de utilizare recomandat:**
1. Deschideți contul cu un depozit inițial de 5,000 RON
2. Configurați transfer automat lunar de 1,500 RON din salariu
3. Ținta: 30,000 RON (6 luni cheltuieli) în 18 luni
4. După atingerea țintei, mențineți nivelul și redirecționați surplus către alte obiective

---

### 3.2 Depozit Fresh Money

**De ce acest produs:**
Perfect pentru obiective concrete pe termen scurt cu date stabilite. Oferă dobânzi atractive și disciplină financiară prin economii programate.

**Beneficii principale:**
- Dobânzi superioare contului de economii clasic
- Flexibilitate în alegerea perioadei (3-24 luni)
- Posibilitate reinvestire automată
- Planificare precisă pentru obiective specifice
- Protecție împotriva cheltuielilor impulsive

**Mod de utilizare recomandat:**
1. Deschideți 2 depozite separate:
   - **Depozit Vacanță:** 10,000 RON pe 12 luni
   - **Depozit Educație:** 15,000 RON pe 24 luni
2. La maturitate, reinvestiți cu dobânda câștigată
3. Pentru obiective noi, deschideți depozite noi din economiile lunare

---

### 3.3 Fonduri de Investiții Raiffeisen Asset Management

**De ce acest produs:**
Pentru obiective pe termen lung, investițiile în fonduri mutual oferă potențial de creștere superior depozitelor, cu risc controlat prin diversificare profesionistă.

**Beneficii principale:**
- Diversificare automată (acțiuni, obligațiuni, piețe internaționale)
- Management profesionist de către experți financiari
- Acces la piețe de capital cu sume mici (de la 500 RON)
- Lichiditate - posibilitate retragere în 2-3 zile
- Avantaj fiscal - impozit redus pe câștiguri din investiții

**Mod de utilizare recomandat:**
1. **Luna 1-3:** Educație financiară și studiu produse disponibile
2. **Luna 4:** Start cu investiție inițială 5,000 RON în fond mixt (60% obligațiuni, 40% acțiuni)
3. **Luna 5+:** Contribuție lunară automată 2,000 RON (Dollar Cost Averaging)
4. **Distribuție recomandată:**
   - 40% - Fond conservator (obligațiuni)
   - 40% - Fond echilibrat (mixt)
   - 20% - Fond dinamic (acțiuni) pentru creștere pe termen lung
5. **Revizuire:** Quarterly review și rebalansare anuală

---

## 4. Timeline de Implementare

### Luna 1-2: Fundamentele

**Pași imediați:**
- ✅ Deschidere Cont Super Acces Plus
- ✅ Configurare transfer automat lunar 1,500 RON
- ✅ Depunere inițială 5,000 RON în contul de economii
- ✅ Programare întâlnire consultant pentru fonduri de investiții

**Configurări:**
- Activare Internet Banking și Mobile Banking
- Setare alerte SMS/email pentru tranzacții
- Conectare cont economii cu cardul de debit

### Luna 3-6: Consolidare

**Dezvoltare obiceiuri:**
- ✅ Monitorizare lunară sold cont economii (target: 9,000 RON după 6 luni)
- ✅ Luna 4: Deschidere Depozit Fresh Money (10,000 RON, 12 luni)
- ✅ Luna 5: Start investiție fonduri - prima contribuție 5,000 RON
- ✅ Luna 6: Configurare contribuție automată lunară 2,000 RON în fonduri

**Ajustări:**
- Review cheltuieli lunare și optimizare buget
- Identificare oportunități creștere venituri
- Evaluare performanță economii vs. plan

### Luna 7-12: Creștere

**Extindere strategii:**
- Crescătoare sold cont economii către ținta 30,000 RON
- Monitorizare performanță fonduri de investiții
- Luna 12: Evaluare depozit Fresh Money și decizie reinvestire
- Posibilă creștere contribuție lunară dacă venitul permite

**Evaluare progres:**
- Review anual complet la luna 12
- Calculare randament total pe toate produsele
- Ajustare strategie în funcție de schimbări situație personală

### Anul 2+: Obiective pe Termen Lung

**Planuri investiționale:**
- Creștere pondere fonduri de investiții pentru avans locuință
- Posibilă modificare proporții fonduri (mai agresiv dacă piața permite)
- Explorare produse suplimentare (pensii private, asigurări de viață)

**Securitate financiară:**
- Menținere fond urgență la zi
- Diversificare continuă investiții
- Planificare fiscală optimă

---

## 5. Analiza Riscurilor și Protecție

### Riscuri Identificate

**1. Risc de lichiditate:**
- Situație: Necesitate bani urgentă când fonduri blocate în depozite/investiții
- Probabilitate: Medie
- Impact: Ridicat

**2. Risc de piață:**
- Situație: Scădere valoare fonduri investiții în perioade adverse
- Probabilitate: Medie
- Impact: Moderat (orizont lung diminuează riscul)

**3. Risc de inflație:**
- Situație: Inflație erodează putere de cumpărare economii
- Probabilitate: Ridicată
- Impact: Moderat

**4. Risc personal:**
- Situație: Pierdere venit (șomaj, boală)
- Probabilitate: Scăzută
- Impact: Foarte ridicat

### Măsuri de Protecție

**Implementate prin produsele selectate:**
1. **Fond de urgență** (Cont Super Acces Plus): Protecție lichiditate imediată
2. **Diversificare** (Fonduri investiții): Reducere risc concentrare
3. **Depozite garantate**: Protecție până la 100,000 EUR prin FGDB
4. **Investiții diversificate**: Protecție contra inflației pe termen lung

**Recomandări suplimentare:**
- ✅ Asigurare de viață pentru protecția familiei (în caz de deces/invaliditate)
- ✅ Asigurare locuință (dacă nu există deja)
- ✅ Asigurare sănătate privată
- ✅ Creștere competențe profesionale pentru stabilitate venit

---

## 6. Rezultate Așteptate

### Pe termen scurt (1 an)

**Rezultate concrete măsurabile:**
- ✅ Fond de urgență: 18,000 RON economisiți (din ținta 30,000)
- ✅ Depozit Fresh Money: 10,000 RON + ~350 RON dobândă
- ✅ Fonduri investiții: ~20,000 RON investiți (5,000 inițial + 12×1,500 lunar)
- ✅ **Total economisit/investit:** ~48,350 RON
- ✅ Obiceiuri financiare solide formate
- ✅ Înțelegere piețe financiare îmbunătățită

### Pe termen mediu (3-5 ani)

**Progres către obiectivele majore:**
- ✅ Fond urgență complet: 30,000 RON
- ✅ Portofoliu fonduri investiții: ~120,000 RON (cu creștere 6-8% anual)
- ✅ Depozite acumulate: ~50,000 RON
- ✅ **Total avere lichidă:** ~200,000 RON
- ✅ Avans locuință 30%: Posibilitate cumpărare în anul 5
- ✅ Fond educație copil: 50,000 RON

### Pe termen lung (7+ ani)

**Securitate financiară și independență:**
- ✅ Locuință proprie achitată sau în plată (avans substanțial plătit)
- ✅ Portofoliu investiții: ~300,000+ RON
- ✅ Venit pasiv din investiții: ~1,500-2,000 RON/lună
- ✅ Pregătire solidă pentru pensionare
- ✅ **Independență financiară parțială:** Capacitate menținere stil de viață fără venit activ pentru 5+ ani
- ✅ Educație copil asigurată financiar
- ✅ Opțiuni flexibile: Semi-retirement, schimbare carieră, antreprenoriat

---

## 7. Monitorizare și Ajustări

### Review-uri Programate

**Lunar:**
- Verificare sold conturi și depozite
- Monitorizare contribuții automate
- Actualizare buget personal

**Trimestrial:**
- Evaluare performanță fonduri investiții
- Rebalansare portofoliu dacă necesar
- Review obiective și progres

**Anual:**
- Analiză completă situație financiară
- Ajustare strategie în funcție de schimbări (venit, familie, obiective)
- Optimizare fiscală
- Consultare cu consultant financiar

### Indicatori Cheie de Performanță (KPI)

1. **Rata de economisire:** >20% din venit net lunar
2. **Fond urgență:** Minim 6 luni cheltuieli
3. **Randament investiții:** >inflație + 3% anual
4. **Diversificare:** <40% din avere în același activ
5. **Lichiditate:** >10,000 RON accesibil instant

---

## 8. Concluzii și Recomandări Finale

Acest plan financiar oferă o fundație solidă pentru atingerea obiectivelor dumneavoastră financiare pe termen scurt, mediu și lung. Prin combinarea inteligentă a produselor Raiffeisen Bank - economii cu acces rapid, depozite la termen și fonduri de investiții - veți beneficia de:

✅ **Siguranță:** Fond de urgență complet în 20 luni
✅ **Creștere:** Potențial randamente superioare inflației
✅ **Flexibilitate:** Acces la fonduri când aveți nevoie
✅ **Diversificare:** Risc distribuit pe multiple produse și clase de active

### Pașii Următori Imediați

1. **Săptămâna 1:** Deschideți Cont Super Acces Plus și configurați transferul automat
2. **Săptămâna 2:** Programați întâlnire cu consultant pentru fonduri de investiții
3. **Luna 2:** După acumulare sumă inițială, deschideți primul Depozit Fresh Money
4. **Luna 4-5:** Start investiții în fonduri după studiere opțiuni disponibile

### Contact și Suport

Pentru implementarea acestui plan și consultanță continuă:
- 📞 **Apelați:** Centrul de Relații Clienți Raiffeisen Bank
- 🏦 **Vizitați:** Sucursala dumneavoastră Raiffeisen
- 💻 **Online:** Programare întâlnire prin Internet Banking
- 📧 **Email:** Consultanții noștri sunt disponibili pentru întrebări

---

**Succes în călătoria dumneavoastră către independența financiară!** 🎯💰

*Planul a fost generat pe baza informațiilor furnizate. Este recomandat să consultați un consultant financiar pentru personalizare suplimentară în funcție de situația dumneavoastră specifică.*

---

**Document generat:** Noiembrie 2025  
**Raiffeisen Bank România** | Produse Financiare Personalizate
"""

    print("=" * 80)
    print("TEST: Conversie Markdown → PDF folosind MCP Pandoc")
    print("=" * 80)
    print("\n📝 Plan financiar Markdown pregătit (lungime: {} caractere)".format(len(sample_plan)))
    print("\n⏳ Încep conversia în PDF...\n")
    
    try:
        # Convert to PDF
        pdf_path, message = convert_markdown_to_pdf(
            sample_plan,
            "test_plan_financiar.pdf"
        )
        
        print("✅ SUCCES!")
        print(f"📄 {message}")
        print(f"📁 Locație fișier: {pdf_path}")
        print("\n" + "=" * 80)
        print("Test complet cu succes! ✅")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ EROARE: {str(e)}")
        print("\n💡 Verificați că sunt instalate:")
        print("   - pandoc (brew install pandoc)")
        print("   - texlive (brew install texlive)")
        print("   - mcp-pandoc (pip install mcp-pandoc)")
        print("\n" + "=" * 80)
        print("Test eșuat! ❌")
        print("=" * 80)
        
        return False


if __name__ == "__main__":
    test_pdf_conversion()

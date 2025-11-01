# 🎯 Financial Plan Agent - Documentație

## 📋 Descriere

Agentul de Plan Financiar este un LLM agent profesional care generează planuri financiare personalizate, comprehensive și acționabile pentru clienții băncii.

## 🎨 Caracteristici

### ✅ **Analiza Completă**
- Evaluarea situației financiare actuale
- Identificarea obiectivelor pe termen scurt, mediu și lung
- Analiza riscurilor și oportunităților

### 📊 **Strategie Personalizată**
- Plan detaliat pentru fiecare produs selectat
- Integrare produse cu obiectivele utilizatorului
- Timeline de implementare concret

### 🔒 **Profesionalism**
- Ton profesional bancar
- Limba română formală (dumneavoastră)
- Format markdown structurat
- 800-1200 cuvinte pentru acoperire completă

### 🎯 **Acționabil**
- Pași concreți de implementare
- Recomandări specifice cu numere
- Timeline clar (lunar, anual, pe termen lung)

## 📐 Structura Planului Generat

```
# Plan Financiar Personalizat

## 1. Rezumat Executiv
## 2. Analiza Situației Actuale
## 3. Strategia de Produse Recomandate
   ### 3.1 [Produs 1]
   ### 3.2 [Produs 2]
   ...
## 4. Timeline de Implementare
## 5. Analiza Riscurilor și Protecție
## 6. Rezultate Așteptate
## 7. Pași Următori Imediați
## 8. Recomandări Finale
```

## 🔧 Utilizare

### În Cod Python

```python
from src.agents.financial_plan_agent import generate_financial_plan, format_plan_for_display

# Profil utilizator
user_profile = {
    "age": 35,
    "marital_status": "Căsătorit/ă",
    "annual_income": 75000.0,
    "employment_status": "Angajat",
    "has_children": True,
    "number_of_children": 2,
    "risk_tolerance": "Medie",
    "financial_goals": ["Economii pe termen lung", "Educație copii"]
}

# Produse selectate
selected_products = [
    {
        "product_id": "cont_economii",
        "name_ro": "Cont de Economii",
        "description": "...",
        "benefits": ["...", "..."],
        "personalized_summary": "..."
    },
    # ... alte produse
]

# Generare plan
plan = generate_financial_plan(user_profile, selected_products)
formatted_plan = format_plan_for_display(plan)

print(formatted_plan)
```

### În Interfața Streamlit

1. **Completează profilul** utilizatorului
2. **Generează recomandări** produse
3. **Selectează produsele** dorite (checkbox-uri)
4. Click pe **"🎯 Generează Plan Financiar Personalizat"**
5. **Vizualizează** planul generat
6. **Descarcă** planul ca fișier Markdown

## 🧪 Testare

### Test Direct

```bash
# Din rădăcina proiectului
python -m src.agents.financial_plan_agent
```

Acest script va:
- Rula agentul cu date de test
- Afișa planul generat
- Valida funcționalitatea

### Test în Aplicație

1. Login în aplicație
2. Mergi la "Recomandări Produse"
3. Completează profilul
4. Generează recomandări
5. Selectează 2-3 produse
6. Generează plan financiar

## ⚙️ Configurație LLM

### Model
- **Default:** Claude 3.5 Sonnet (via Bedrock + LiteLLM)
- **Temperature:** 0.7 (balans creativitate/consistență)
- **Max Tokens:** 4000 (suficient pentru plan complet)

### Personalizare

Modifică în `financial_plan_agent.py`:

```python
financial_plan_agent = Agent(
    name="Financial Plan Generator",
    model=build_default_litellm_model(),
    model_settings=ModelSettings(
        temperature=0.7,      # 0.0-1.0: mai mic = mai consistent
        max_tokens=4000,      # Crește pentru planuri mai detaliate
        include_usage=True,
    ),
)
```

## 📊 Input Format

### User Profile (dict)

```python
{
    "first_name": str,           # optional
    "last_name": str,            # optional
    "age": int,                  # required
    "marital_status": str,       # required
    "annual_income": float,      # required
    "employment_status": str,    # required
    "has_children": bool,        # required
    "number_of_children": int,   # required
    "risk_tolerance": str,       # required: "Scăzută", "Medie", "Ridicată"
    "financial_goals": list[str] # required
}
```

### Selected Products (list[dict])

```python
[
    {
        "product_id": str,              # required
        "name": str,                    # optional
        "name_ro": str,                 # required
        "description": str,             # required
        "benefits": list[str],          # required
        "personalized_summary": str,    # optional (dar recomandat)
        "score": float                  # optional
    },
    # ... more products
]
```

## 🎨 Output Format

### Markdown Text
Plan complet formatat în Markdown cu:
- Headers (##, ###)
- Bold text (**text**)
- Lists (- item)
- Structură clară și consistentă

### Metadata
Header automat adăugat cu:
- Data generării
- Tip document
- Marcaj confidențial

## ⚡ Performance

### Timp de Generare
- **Tipic:** 10-20 secunde
- **Depinde de:**
  - Număr produse selectate
  - Complexitatea profilului
  - Latență API Bedrock

### Optimizări
- Cache rezultate în session_state
- Async execution pentru non-blocking UI
- Error handling robust

## ❌ Error Handling

### ValueError
- Profil lipsă sau incomplet
- Niciun produs selectat
- Date invalide

### RuntimeError
- LLM agent failure
- API connection issues
- Bedrock errors

### Toate erorile
- Mesaje user-friendly în română
- Traceback detaliat în expander
- Suggestions pentru rezolvare

## 🔐 Securitate & Privacy

- ✅ Datele NU sunt stocate permanent
- ✅ Plan generat în session - dispare la logout
- ✅ Download plan local (client-side)
- ✅ Nicio trimitere externă de date

## 📝 Exemple de Output

### Exemplu Rezumat Executiv

```markdown
## 1. Rezumat Executiv

La vârsta de 35 de ani, cu o familie în creștere (soț/soție și 2 copii) și un 
venit anual de 75.000 RON, vă aflați într-o etapă crucială pentru construirea 
securității financiare. Profilul dumneavoastră indică o toleranță medie la risc 
și obiective clare: economii pe termen lung, educația copiilor și achiziția unei locuințe.

Produsele selectate - Cont de Economii și Pensie Privată Pilon III - formează o 
fundație solidă pentru realizarea acestor obiective, oferind atât flexibilitate 
pe termen scurt, cât și securitate pe termen lung.
```

### Exemplu Strategie Produs

```markdown
### 3.1 Cont de Economii

**De ce acest produs:**
Contul de economii reprezintă fundația strategiei dumneavoastră financiare, oferind 
flexibilitate maximă și siguranță capitatului. Este ideal pentru construirea unui 
fond de urgență echivalent cu 3-6 luni de cheltuieli și pentru economisirea către 
obiective pe termen scurt, cum ar fi vacanțe sau mobilier.

**Beneficii principale:**
- Acces imediat la fonduri fără penalizări în caz de urgențe
- Dobândă variabilă competitivă care protejează împotriva inflației
- Fără comisioane de administrare, maximizând economiile nete
- Securitate maximă - depozitele sunt garantate până la 100.000 EUR
- Instrumente digitale pentru monitorizare și automatizare contribuții

**Mod de utilizare recomandat:**
1. **Fond de urgență:** Alocați 1.500 RON lunar până atingeți 30.000 RON (6 luni cheltuieli)
2. **Automatizare:** Setați transfer automat în prima zi a lunii
3. **Contribuții extra:** Depuneți bonusuri anuale sau venituri suplimentare
4. **Monitorizare:** Revizuiți trimestrial și ajustați contribuțiile
5. **Target:** Atingeți fondul de urgență în 20 luni
```

## 🚀 Dezvoltări Viitoare

- [ ] Export PDF profesional cu logo bancă
- [ ] Grafice și vizualizări financiare
- [ ] Comparare scenarii "what-if"
- [ ] Integrare calendar cu reminder-e
- [ ] Plan de acțiune interactiv cu checklist
- [ ] Versiuni multiple ale planului (optimist/pesimist/realist)

## 🤝 Contribuții

Pentru îmbunătățiri sau bug fixes:
1. Modifică `src/agents/financial_plan_agent.py`
2. Testează cu `python -m src.agents.financial_plan_agent`
3. Verifică output-ul generat
4. Update documentația dacă e necesar

---

**Versiune:** 1.0  
**Data:** 2025-11-01  
**Agent:** Claude 3.5 Sonnet via AWS Bedrock

# View Plan - Quick Start Guide

## 🚀 Cum să folosești noua pagină

### 1. Pornire Rapidă (Mock Data)

Pagina funcționează imediat cu date mock - nu necesită baza de date:

```bash
# Activare virtual environment
source .venv/bin/activate

# Pornire aplicație
streamlit run pages/5_View_Plan.py
```

**Login cu orice credențiale** - mock data va fi folosit automat.

---

### 2. Testare Funcții Analytics

Verifică că toate calculele deterministe funcționează:

```bash
python test_plan_analytics.py
```

Ar trebui să vezi output-uri pentru:
- ✅ Capacitate economisire
- ✅ Proiecții investiții
- ✅ Estimări randamente
- ✅ Timeline-uri obiective
- ✅ Proiecție patrimoniu
- ✅ Analiză risc-randament
- ✅ Statistici complete

---

### 3. Integrare cu Baza de Date

Pentru a folosi date reale din database:

#### A. Setup Database
```bash
# Asigură-te că ai .env configurat cu credențiale DB
# APP_DB_HOST, APP_DB_PORT, APP_DB_USER, APP_DB_PASSWORD, APP_DB_NAME

# Inițializare tabel users (dacă nu există)
python -c "from src.utils.db import init_users_table; init_users_table()"
```

#### B. Generare Plan
1. Navighează la pagina `2_Product_Recommendations_Florea.py`
2. Login cu un user
3. Completează profilul
4. Click "Obține Recomandări"
5. Selectează produse
6. Click "Generează Plan Financiar"
7. Click "💾 Salvează Planul în Baza de Date"

#### C. Înlocuire Mock Data
În fișierul `pages/5_View_Plan.py`, linia ~50-140:

**Înlocuiește**:
```python
def get_user_financial_plan(email: str) -> dict:
    # MOCK DATA - Replace this entire function with DB query
    mock_user_profile = {...}
    ...
```

**Cu**:
```python
def get_user_financial_plan(email: str) -> dict:
    """Get user's financial plan from database."""
    from src.utils.db import get_user_by_email
    
    user_data = get_user_by_email(email)
    
    if not user_data:
        raise ValueError(f"User not found: {email}")
    
    plan_text = user_data.get("user_plan")
    
    if not plan_text:
        return {"plan_text": None, "user_profile": None, "products": []}
    
    # Build user profile from database
    user_profile = {
        "email": user_data.get("email"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "age": user_data.get("age"),
        "marital_status": user_data.get("marital_status"),
        "annual_income": user_data.get("extra", {}).get("annual_income", 50000.0),
        "employment_status": user_data.get("employment_status"),
        "has_children": user_data.get("has_children", False),
        "number_of_children": user_data.get("number_of_children", 0),
        "risk_tolerance": user_data.get("extra", {}).get("risk_tolerance", "Medie"),
        "education_level": user_data.get("extra", {}).get("education_level", "Facultate"),
        "financial_goals": user_data.get("extra", {}).get("financial_goals", []),
    }
    
    # Extract products from plan
    import re
    product_matches = re.findall(r'### 3\.\d+ (.+)', plan_text)
    products = product_matches if product_matches else []
    
    return {
        "plan_text": plan_text,
        "user_profile": user_profile,
        "products": products
    }
```

#### D. Test cu Date Reale
```bash
streamlit run pages/5_View_Plan.py
```

Login cu user-ul pentru care ai generat planul → vezi planul real!

---

### 4. Structura Fișierelor

```
pages/
  5_View_Plan.py              # ← Pagina principală Streamlit

src/
  agents/
    plan_analysis_agent.py    # ← Agent LLM pentru personalizare
  
  utils/
    plan_analytics.py         # ← Funcții deterministe de analiză
    db.py                     # ← Database helpers (deja există)

test_plan_analytics.py        # ← Script de testare

docs/
  VIEW_PLAN_README.md         # ← Documentație completă
  VIEW_PLAN_DB_INTEGRATION.md # ← Ghid integrare DB
```

---

### 5. Funcționalități Principale

#### 📊 Statistici Cheie
- Venit lunar
- Economii lunare
- Randament așteptat
- Nivel risc

#### 📈 Grafic Wealth Projection
- Slider pentru orizont (1-30 ani)
- 3 curbe: Total / Contribuții / Randamente
- Interactive hover

#### 🎯 Progres către Obiective
- Top 3 obiective
- Progress bars
- Timeline cu milestone-uri
- Date estimate completare

#### ⚖️ Analiză Risc-Randament
- Gauge chart pentru risc
- Gauge chart pentru randament
- Scor diversificare

#### 💡 Insight-uri Personalizate
- Generate de agent LLM
- Adaptate la profil user complet
- Stil comunicare personalizat

#### 📦 Breakdown Produse
- Tab pentru fiecare produs
- Randament estimat
- Categorie și risc

---

### 6. Personalizare Agent

Agentul se adaptează automat bazat pe:

| Caracteristică | Adaptare |
|----------------|----------|
| **Vârstă** | 18-25: energic → 51+: conservativ |
| **Educație** | Liceu: simplu → Doctorat: sofisticat |
| **Venit** | <30K: accesibil → >70K: complex |
| **Familie** | Single: flexibil → Cu copii: securitate |
| **Risc** | Scăzut: siguranță → Ridicat: creștere |

**Exemplu**:
- User: 32 ani, Facultate, 72K, căsătorită, 1 copil, risc mediu
- Ton: Professional, balansmat, focus familie și educație

---

### 7. Calculele Deterministe

Toate statisticile sunt calculate matematic, fără halucinații:

#### Capacitate Economisire
- Formula: `Venit - Cheltuieli = Economii`
- Cheltuieli bază: 60% din venit
- Ajustări: +10% per copil, -5% căsătorie, +5% vârstă >50

#### Proiecții Investiții
- Formula compunere: `FV = PV * (1 + r)^n + PMT * [((1+r)^n - 1)/r]`
- Randamente conservative bazate pe date istorice RON

#### Timeline Obiective
- Ținte realiste: 15K (economii scurte) → 500K (pensionare)
- Calcul cu dobândă 5% anuală

---

### 8. Troubleshooting

#### "Nu aveți un plan generat"
→ Generează plan prin pagina 2_Product_Recommendations_Florea.py

#### Grafice nu apar
→ `pip install plotly`

#### Agent timeout
→ Pagina are fallback text hardcodat, funcționează și fără agent

#### Database connection error
→ Verifică .env și credențiale DB, sau folosește mock data

---

### 9. Next Steps

După ce pagina funcționează:

1. ✅ Testează cu mock data
2. ✅ Testează funcții analytics
3. ⬜ Integrează cu baza de date
4. ⬜ Generează plan real prin pagina 2
5. ⬜ Testează View Plan cu date reale
6. ⬜ Ajustează prompturile agentului (dacă necesar)
7. ⬜ Customizează stilul vizual (culori, layout)
8. ⬜ Deploy în producție

---

### 10. Demo Flow Complet

```
User → Login/Register
  ↓
Navigate to "Product Recommendations" (Page 2)
  ↓
Complete profile + Generate plan + Save to DB
  ↓
Navigate to "View Plan" (Page 5)
  ↓
See personalized analysis with:
  - Statistics
  - Charts
  - Insights
  - Predictions
  ↓
Download plan / Email / Contact consultant
```

---

### 📞 Support

- **Cod comentat**: Vezi inline comments în fișiere
- **Documentație completă**: `docs/VIEW_PLAN_README.md`
- **Integrare DB**: `docs/VIEW_PLAN_DB_INTEGRATION.md`
- **Logică matematică**: Studiază `src/utils/plan_analytics.py`

---

**🎉 Enjoy your personalized financial plan view!**

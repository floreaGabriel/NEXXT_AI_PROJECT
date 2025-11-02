# View Plan Page - Documentație Completă

## 📋 Prezentare Generală

Pagina **View Plan** (5_View_Plan.py) este o interfață avansată care prezintă utilizatorului planul său financiar într-un mod personalizat, vizual și ușor de înțeles.

## 🎯 Obiective

1. **Personalizare Profundă**: Conținutul se adaptează la fiecare caracteristică a utilizatorului (vârstă, educație, venit, familie, risc)
2. **Analiză Deterministă**: Toate statisticile și predicțiile sunt calculate matematic, fără halucinații
3. **Vizualizare Atractivă**: Grafice interactive și metrice clare
4. **Curiozitate și Engagement**: Prezentare care crește interesul utilizatorului

## 🏗️ Arhitectură

### Componente Principale

```
pages/5_View_Plan.py                    # Pagina Streamlit principală
│
├── src/agents/plan_analysis_agent.py   # Agent LLM pentru conținut personalizat
│   └── generate_personalized_analysis() # Generează texte adaptate la user
│
├── src/utils/plan_analytics.py         # Funcții deterministe de analiză
│   ├── generate_key_statistics()       # Statistici complete
│   ├── calculate_savings_capacity()    # Capacitate economisire
│   ├── calculate_wealth_projection()   # Proiecție patrimoniu
│   ├── calculate_goal_timeline()       # Timeline obiective
│   ├── estimate_product_returns()      # Randamente estimate
│   └── analyze_plan_risk_return()      # Analiza risc-randament
│
└── Mock Data (get_user_financial_plan) # Ușor de înlocuit cu DB query
```

## 🔧 Funcționalități Implementate

### 1. Mock Data (Tranziție Ușoară la DB)

Funcția `get_user_financial_plan()` returnează date mock în formatul exact necesar:

```python
{
    "plan_text": "...",      # Planul financiar complet (markdown)
    "user_profile": {...},   # Profilul utilizatorului
    "products": [...]        # Lista produselor din plan
}
```

**Pentru integrare DB**: Vezi `docs/VIEW_PLAN_DB_INTEGRATION.md`

### 2. Agent de Analiză Personalizat

**Fișier**: `src/agents/plan_analysis_agent.py`

Agent LLM specializat care:
- Analizează fiecare caracteristică a utilizatorului
- Adaptează stilul de comunicare (formal/informal, simplu/complex)
- Generează conținut specific pentru vârstă, educație, venit, familie
- Creează text motivant și care stimulează curiozitatea

**Tipuri de conținut generat**:
- `introduction` - Introducere personalizată
- `insights` - Insight-uri cheie
- `timeline` - Narative despre progres
- `synergy` - Explicații despre sinergia produselor
- `motivation` - Rezumate motivaționale

**Adaptări automate bazate pe**:
- **Vârstă**: 18-25 (energic) → 51+ (conservativ)
- **Educație**: Liceu (simplu) → Doctorat (sofisticat)
- **Venit**: <30K (accesibil) → >70K (complex)
- **Familie**: Single (flexibil) → Cu copii (securitate)
- **Risc**: Scăzut (siguranță) → Ridicat (oportunități)

### 3. Funcții Deterministe de Analiză

**Fișier**: `src/utils/plan_analytics.py`

#### a) `calculate_savings_capacity()`
Calculează capacitatea realistă de economisire bazată pe:
- Venit anual
- Rată cheltuieli de bază (60% baseline)
- Ajustări pentru: căsătorie (-5%), copii (+10% per copil), vârstă >50 (+5%)
- Limitare la maxim 85% cheltuieli

**Output**:
```python
{
    "monthly_income": 6000.0,
    "monthly_expenses": 3900.0,
    "monthly_savings_potential": 2100.0,
    "annual_savings_potential": 25200.0,
    "expense_ratio": 65.0,
    "savings_ratio": 35.0,
    "emergency_fund_target": 23400.0,
    "months_to_emergency_fund": 11.1
}
```

#### b) `calculate_investment_projections()`
Proiecție an cu an a creșterii investițiilor:
- Suma inițială + contribuții lunare
- Randament compus anual
- Breakdown: contribuții vs randamente

**Parametri**:
- `initial_amount`: Suma de start
- `monthly_contribution`: Contribuție lunară
- `annual_return_rate`: Rata anuală (ex: 0.06 = 6%)
- `years`: Perioada de proiecție

#### c) `estimate_product_returns()`
Estimări conservative bazate pe date istorice românești:

| Produs | Risc Scăzut | Risc Mediu | Risc Ridicat |
|--------|-------------|------------|--------------|
| Cont economii | 2% | 2.5% | 3% |
| Depozit | 4% | 4.5% | 5% |
| Fond investiții | 5% | 7% | 9% |
| Pensie privată | 4% | 6% | 8% |
| Titluri venit fix | 4.5% | 5% | 5.5% |

#### d) `calculate_goal_timeline()`
Calculează timeline realist pentru obiective:

**Sume țintă conservative** (RON):
- Economii termen scurt: 15,000
- Economii termen lung: 100,000
- Investiții: 50,000
- Cumpărare casă (avans 30%): 150,000
- Educație copii: 80,000
- Pensionare: 500,000
- Călătorii: 20,000
- Achiziții mari: 30,000

**Calcul**: Formula FV (Future Value) cu dobândă compusă 5%

#### e) `calculate_wealth_projection()`
Proiecție completă pe 10+ ani:
- Folosește capacitatea de economisire calculată
- Aplică rata de randament bazată pe profil risc
- Generează grafic an cu an

#### f) `analyze_plan_risk_return()`
Analiză risc-randament a portofoliului:
- Scoruri risc per categorie produs (1-4)
- Randament mediu ponderat
- Sharpe ratio simplificat
- Scor diversificare (% categorii unice)

### 4. Interfață Streamlit

**Secțiuni pagină**:

#### A. Header și Autentificare
- Navigare: Login / Register / Logout
- Verificare autentificare obligatorie

#### B. Metrici Cheie (4 cards)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Venit Lunar │ Economii    │ Randament   │ Nivel Risc  │
│   6,000 RON │   2,100 RON │      6.5%   │    Mediu    │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### C. Plan Complet (Dropdown Expandabil)
- Plan în markdown, complet formatat
- Buton descărcare ca fișier `.md`

#### D. Grafic Proiecție Patrimoniu (Plotly Interactive)
- Slider pentru orizont timp (1-30 ani)
- 3 linii: Total Patrimoniu / Contribuții / Randamente
- Hover detaliat per an
- 3 metrici sub grafic: Contribuții / Randament / Final

#### E. Progres către Obiective
Pentru top 3 obiective:
- Progress bar vizual
- Detalii: țintă, contribuție, timp estimat
- Mini-grafic milestone-uri (25%, 50%, 75%, 100%)

#### F. Analiza Risc-Randament
- 2 gauge charts (Plotly Indicator):
  - Scor Risc (0-4 scale)
  - Randament Estimat (0-12% scale)
- Progress bar diversificare

#### G. Insight-uri Personalizate
- Text generat de agent LLM
- Adaptat la profil complet utilizator
- 3-5 insight-uri concrete

#### H. Breakdown Produse (Tabs)
- Tab per produs
- Randament estimat per produs
- Categorie și ajustare risc

#### I. Footer Acțiuni
```
┌────────────────┬────────────────┬────────────────┐
│ Trimite Email  │ Actualizează   │ Contactează    │
│                │    Profilul    │  Consultant    │
└────────────────┴────────────────┴────────────────┘
```

## 📊 Exemple de Vizualizări

### 1. Grafic Wealth Projection
- **Tip**: Line chart cu fill
- **Axe**: Ani (X) vs RON (Y)
- **Linii**: 3 (Total, Contribuții, Randamente)
- **Interactiv**: Hover unified, zoom, pan

### 2. Goal Timeline Milestones
- **Tip**: Horizontal bar chart
- **Date**: Procentaj progres + luni
- **Colorscale**: Verde gradient

### 3. Risk Gauge
- **Tip**: Indicator gauge
- **Range**: 0-4
- **Zones**: Verde (0-1.5), Galben (1.5-2.5), Roșu (2.5-4)

### 4. Return Gauge
- **Tip**: Indicator gauge cu delta
- **Range**: 0-12%
- **Reference**: 4% (inflație/risk-free)

## 🔄 Flow Complet

```
User Login
    ↓
Navigate to "View Plan"
    ↓
Load plan from DB (currently mock)
    ↓
Generate statistics (deterministic)
    ↓
Generate personalized content (LLM agent)
    ↓
Render visualizations (Plotly)
    ↓
Display insights and recommendations
    ↓
User actions: Download / Email / Update
```

## 🎨 Personalizare Exemplu

### Utilizator A: Alexandra, 32 ani, Facultate, 72K venit, căsătorită, 1 copil

**Stil comunicare generat**:
```
"Planul dumneavoastră reflectă o etapă dinamică a vieții - consolidarea 
carierei și creșterea familiei. Cu un venit solid de 72.000 RON anual, 
aveți oportunitatea de a construi o fundație financiară robustă înainte de..."
```

**Ton**: Professional, balansmat, focus pe familie și educație

### Utilizator B: Ion, 55 ani, Liceu, 35K venit, căsătorit, 2 copii

**Stil comunicare generat**:
```
"Cu o experiență de viață bogată și responsabilități familiale importante, 
planul dumneavoastră pune accent pe siguranță și predictibilitate. Produsele 
selectate asigură protecția economiilor pe care le-ați construit cu trudă..."
```

**Ton**: Respectuos, simplu, focus pe securitate și protecție

## 🧪 Testing

### Mock Data Testing (Current)
```bash
# Rulare pagină cu mock data
streamlit run pages/5_View_Plan.py
```

### Database Integration Testing
```bash
# 1. Setup database
python -c "from src.utils.db import init_users_table; init_users_table()"

# 2. Generate plan via page 2
# Navigate to Product Recommendations și generează plan

# 3. Test View Plan
streamlit run pages/5_View_Plan.py
```

### Unit Testing Analytics
```bash
# Test funcții deterministe
python -c "
from src.utils.plan_analytics import calculate_savings_capacity

profile = {'annual_income': 72000, 'age': 32, 'has_children': True, 'number_of_children': 1}
result = calculate_savings_capacity(profile)
print(result)
"
```

## 📦 Dependențe

Toate dependințele sunt în `requirements.txt`:
- `streamlit` - Framework UI
- `plotly` - Grafice interactive
- `pandas` - Manipulare date
- `python-dateutil` - Calcule date
- `nest-asyncio` - Async in Streamlit
- `openai-agents` - Framework LLM agents

## 🔮 Îmbunătățiri Viitoare

1. **Comparare Planuri**: Vezi evoluția între versiuni
2. **Notificări**: Alertă când se apropie milestone-uri
3. **Recomandări Dinamice**: Sugestii de ajustare bazate pe progres
4. **Export PDF**: Plan formatat profesional
5. **Sharing**: Partajare plan cu family member
6. **Gamification**: Badges pentru atingere obiective
7. **AI Chatbot**: Întrebări despre plan în limbaj natural

## 📝 Mentenanță

### Update Estimate Returns
Fișier: `src/utils/plan_analytics.py` → `estimate_product_returns()`

Actualizează dicționarul `return_estimates` cu date de piață curente.

### Update Agent Prompts
Fișier: `src/agents/plan_analysis_agent.py` → `instructions`

Ajustează instrucțiunile agentului pentru îmbunătățirea stilului.

### Update Mock Data
Fișier: `pages/5_View_Plan.py` → `get_user_financial_plan()`

Modifică mock data pentru teste.

## 🆘 Troubleshooting

### "Nu aveți un plan generat"
**Cauză**: User nu are user_plan în DB
**Soluție**: Generează plan prin pagina 2_Product_Recommendations_Florea.py

### Grafice nu se afișează
**Cauză**: Plotly import error
**Soluție**: `pip install plotly`

### Async errors
**Cauză**: nest_asyncio issue
**Soluție**: Verifică că `nest_asyncio.apply()` e apelat la începutul paginii

### Agent LLM timeout
**Cauză**: AWS Bedrock API slow/unavailable
**Soluție**: Pagina are fallback text hardcodat

## 📞 Contact

Pentru întrebări despre implementare:
- Vezi cod inline comments
- Consultă `docs/VIEW_PLAN_DB_INTEGRATION.md`
- Review `src/utils/plan_analytics.py` pentru logică matematică

---

**Versiune**: 1.0  
**Data**: November 2025  
**Autor**: Gabriel Florea

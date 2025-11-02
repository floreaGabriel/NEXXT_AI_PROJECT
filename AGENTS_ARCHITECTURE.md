# Arhitectura Agenților - NEXXT AI Banking Project

## 📋 Cuprins
1. [Prezentare Generală](#prezentare-generală)
2. [Flow-uri Complete](#flow-uri-complete)
3. [Agenții Detaliat](#agenții-detaliat)
4. [Integrări și Dependencies](#integrări-și-dependencies)

---

## Prezentare Generală

Proiectul folosește **8 agenți AI specializați** care lucrează împreună pentru a oferi servicii bancare personalizate utilizatorilor Raiffeisen Bank România.

### Stack Tehnologic
- **Framework Agenți**: OpenAI Agents SDK (via LiteLLM)
- **Model Principal**: Claude 3.5 Sonnet (AWS Bedrock)
- **Limbaj**: Python 3.11+
- **UI**: Streamlit
- **Bază de Date**: PostgreSQL
- **MCP Servers**: Email, Postgres

### Filosofia Sistemului
- **Personalizare Profundă**: Fiecare agent adaptează outputul bazat pe profil complet utilizator
- **Modularitate**: Fiecare agent are o responsabilitate clară și bine definită
- **Integrare Seamless**: Agenții comunică prin JSON structurat
- **Siguranță**: Nu inventează caracteristici produse - folosește doar informații oficiale

---

## Flow-uri Complete

### 🎯 Flow 1: Product Recommendation (Pagina Principală) - **UPDATED WITH AI-POWERED JUSTIFICATION**

```
[USER PROFILE]
    ↓
[FETCH PRODUCTS FROM DATABASE]
    ├── PostgreSQL: SELECT * FROM products
    └── Returns: All products with full markdown descriptions
    ↓
[Product Recommendation Agent - MAIN ORCHESTRATOR]
    ├── For EACH product in database:
    │   ↓
    │   [Product Justification Agent - AI TOOL]
    │   ├── Receives: Product description + User profile
    │   ├── Analyzes: Life stage, financial capacity, risk fit, goals, practicality
    │   ├── Generates: Detailed justification (2-3 sentences)
    │   ├── Outputs: 
    │   │   - Relevance Score (0.0-1.0)
    │   │   - Justification text
    │   │   - Key Benefits (3-5 specific to user)
    │   │   - Recommended Action (concrete next step)
    │   └── Returns: ProductJustification object
    │   ↓
    ├── Collects all justifications
    ├── Ranks products by AI-generated relevance score
    └── Output: Lista produse rangate cu scoruri + justificări AI
    ↓
[User Experience Summary Agent]
    ├── Primește: profil user + produs individual
    ├── Generează: rezumat personalizat hyper-specific
    └── Output: Descriere personalizată cu sume RON concrete
    ↓
[Product Title Generation Agent]
    ├── Primește: produs + profil user
    ├── Generează: titlu personalizat 6-12 cuvinte
    └── Output: Titlu captivant în română
    ↓
[DISPLAY TO USER]
    └── Cards cu produse rangate + descrieri + titluri + justificări AI
```

**Arhitectură Nouă (November 2, 2025):**
- ❌ **REMOVED**: Heuristic scoring (`_calculate_product_score_internal`)
- ✅ **ADDED**: Product Justification Agent (AI-powered tool agent)
- ✅ **ADDED**: Database integration for products (PostgreSQL)
- ✅ **ADDED**: AI-generated justifications for each product
- ✅ **ADDED**: Key benefits extraction from markdown
- ✅ **ADDED**: Recommended actions personalized per user

**Exemplu Concret:**
- **Input**: Utilizator 28 ani, angajat, căsătorit, fără copii, venit 65K RON, risc mediu
- **Database Fetch**: 10 products loaded from PostgreSQL
- **Product Justification Agent** (per product):
  - Cont Economii: Score 0.85, "Perfect pentru construirea unui fond de urgență la această vârstă. Cu venitul de 65K RON/an, recomandăm 20K RON (3 luni cheltuieli) în acest cont pentru flexibilitate și siguranță.", Benefits: ["Acces instant la bani", "Dobândă 3% pe sume >50K", "SavingBox economisire automată"]
  - SmartInvest: Score 0.78, "Excelent pentru creștere pe termen lung. Risc mediu se aliniază perfect cu fonduri mixte. Investiție lunară recomandată: 1000 RON (15% din venit)."
  - Credit Ipotecar: Score 0.72, "Vârstă ideală pentru prima casă. Venit permite credit 150K EUR (rată max 2600 RON/lună). Pregătiți avans 15%."
- **User Experience Agent**: "La venitul dumneavoastră de 65.000 RON/an, recomandăm să economisiți lunar 1.500 RON în Depozitul la Termen 12 luni cu dobândă 5.20%..."
- **Product Title Agent**: "Depozitul Sigur Pentru Familia Dumneavoastră În Creștere"

**Key Improvements:**
1. **AI-Driven Scoring**: Replaces rule-based heuristics with Claude 3.5 Sonnet analysis
2. **Database Integration**: Real-time product data from PostgreSQL (no hardcoded catalog)
3. **Detailed Justifications**: Every score includes WHY the product fits the user
4. **Personalized Benefits**: Benefits extracted and contextualized for user profile
5. **Actionable Recommendations**: Concrete next steps (amounts, timeframes, actions)

---

### 💼 Flow 2: Financial Plan Generation (View Plan)

```
[USER SELECTS PRODUCTS]
    ↓
[Financial Plan Agent]
    ├── Primește: profil complet + produse selectate
    ├── Analizează: situație financiară, obiective, risc
    ├── Generează: plan financiar structurat 800-1200 cuvinte
    └── Output: Plan complet în Markdown cu 8 secțiuni
    ↓
[SAVE TO DATABASE]
    └── users.user_plan (TEXT)
    ↓
[Plan Analysis Agent] (Opțional - pentru preview/insights)
    ├── Primește: profil + plan generat
    ├── Generează: conținut personalizat (5 tipuri)
    │   ├── A) Plan Introduction
    │   ├── B) Key Insights
    │   ├── C) Timeline Narrative
    │   ├── D) Product Synergy
    │   └── E) Motivational Summary
    └── Output: Secțiune de analiză adaptată profilului
    ↓
[DISPLAY IN STREAMLIT]
    └── Pagina "View Plan" cu plan complet formatat
```

**Exemplu Flow:**
1. User selectează: "Cont Economii", "Flexidepozit", "SmartInvest"
2. **Financial Plan Agent** generează plan cu:
   - Rezumat executiv: "Planul dumneavoastră combină siguranță (Cont Economii) cu creștere moderată..."
   - Analiza situației: vârstă 28, venit 65K, căsătorit...
   - Strategie produse: cum să folosească fiecare produs
   - Timeline: luna 1-2, 3-6, 7-12, anul 2+
   - Riscuri și protecție
   - Rezultate așteptate pe termen scurt/mediu/lung
3. **Plan Analysis Agent** creează insights: "Pentru dumneavoastră, la 28 de ani cu venit stabil de 5.400 RON/lună..."
4. Plan salvat în DB și afișat user-ului

---

### 📧 Flow 3: Email Summary Sending

```
[USER HAS PLAN + RECOMMENDATIONS]
    ↓
[USER CLICKS "SEND EMAIL"]
    ↓
[Email Summary Agent]
    ├── Primește: profil user + recomandări produse
    ├── Compune: email profesional românesc 120-200 cuvinte
    ├── Format: fără emoji, formal (dumneavoastră)
    ├── Conținut: top 3-5 produse cu 1 propoziție fiecare
    └── Calls MCP Email Server Tool: send_email()
    ↓
[MCP EMAIL SERVER]
    ├── Conectare SMTP
    ├── Trimitere email
    └── Return: success/failure
    ↓
[CONFIRMATION TO USER]
    └── "Email-ul a fost trimis cu succes!"
```

**Exemplu Email Generat:**
```
Subiect: Planul Dumneavoastră Financiar Personalizat - Raiffeisen Bank

Stimată/Stimate [Nume],

Am pregătit un plan financiar personalizat pentru dumneavoastră bazat pe profilul și obiectivele dumneavoastră.

Produsele recomandate:
- Cont de Economii Super Acces Plus: Flexibilitate totală cu dobândă progresivă 2-3% și funcție SavingBox pentru economisire automată
- Flexidepozit: Depozit 6 luni cu dobândă 4.80% și posibilitate depuneri lunare automate prin FixPay
- SmartInvest: Investiții lunare automate de la 200 RON cu gestiune profesională pentru creștere pe termen lung

Pentru detalii complete, vă rugăm să accesați platforma sau să ne contactați.

Cu respect,
Echipa Raiffeisen Bank România
```

---

### 🔍 Flow 4: Bank Term Extraction (Bank Term Highlighter)

```
[USER PASTES BANKING TEXT]
    ↓
[Bank Term Extractor Agent]
    ├── Primește: text arbitrar (română/engleză)
    ├── Identifică: termeni bancari din 3 categorii
    │   ├── Products: card de credit, depozit, ipotecar...
    │   ├── Rates: dobândă, rată fixă, APR...
    │   └── Fees: comision, penalități, taxă...
    ├── Calculează: span-uri exacte (start, end) pentru fiecare termen
    └── Output: JSON strict cu categories + spans
    ↓
[UI HIGHLIGHTS TEXT]
    └── Evidențiază termenii cu culori diferite per categorie
```

**Exemplu:**
- **Input**: "Creditul ipotecar are dobândă fixă 5.10% și comision administrare 0 RON."
- **Output JSON**:
```json
{
  "categories": {
    "Products": ["credit ipotecar"],
    "Rates": ["dobândă fixă", "5.10%"],
    "Fees": ["comision administrare"]
  },
  "spans": [
    {"start": 0, "end": 16, "category": "Products", "text": "credit ipotecar"},
    {"start": 22, "end": 34, "category": "Rates", "text": "dobândă fixă"},
    {"start": 35, "end": 40, "category": "Rates", "text": "5.10%"},
    {"start": 44, "end": 65, "category": "Fees", "text": "comision administrare"}
  ]
}
```

---

### 💬 Flow 5: Bedrock Chat Test

```
[USER TYPES MESSAGE]
    ↓
[Bedrock Chat Agent]
    ├── Agent minimal pentru testare conexiune
    ├── Confirmă acces la Claude via Bedrock
    └── Output: Răspuns concis și prietenos
    ↓
[DISPLAY RESPONSE]
    └── Streamlit chat interface
```

**Scop**: Verificare rapidă că API key-ul Bedrock funcționează corect.

---

## Agenții Detaliat

### 1. 🎯 Product Recommendation Agent
**Fișier**: `src/agents/product_recommendation_agent.py`

**Responsabilitate Principală**: 
Calculează și rankează produse bancare după relevanță pentru utilizator.

**Input**:
```python
UserProfile:
  - marital_status: str
  - annual_income: float (RON)
  - age: int
  - employment_status: str
  - has_children: bool
  - risk_tolerance: str (low/medium/high)
  - financial_goals: list[str]
  - education_level: str
```

**Procesare**:
- Folosește scoring rule-based pentru fiecare produs
- Consideră: vârstă, venit, risc, obiective, familie
- Scoruri între 0.0 și 1.0

**Output**:
```python
[
  {"product_id": "depozite_termen", "score": 0.85},
  {"product_id": "cont_economii_super_acces", "score": 0.75},
  ...
]
```

**Produse în Catalog** (13 produse):
1. Card de Cumpărături în Rate
2. Depozite la Termen
3. Cont de Economii Super Acces Plus
4. Card de Debit Visa Platinum
5. Credit Ipotecar Casa Ta
6. Credit de Nevoi Personale Flexicredit
7. Fonduri de Investiții SmartInvest
8. Pensie Privată Raiffeisen Acumulare (Pilon III)
9. Cont Junior pentru Adolescenți (14-17 ani)
10. Asigurare de Viață cu Componentă de Economisire

**Tools Expuse**:
- `get_raiffeisen_products()`: Returnează catalogul complet
- `calculate_product_score()`: Calculează scor pentru un produs

**Utilizare**:
- Pagina: `pages/2_Product_Recommendations_Florea.py`
- Apel direct: `rank_products_for_profile(user_profile_json)`

---

### 2. 📝 User Experience Summary Agent
**Fișier**: `src/agents/user_experience_summary_agent.py`

**Responsabilitate Principală**: 
Creează rezumate hyper-personalizate ale produselor cu sume RON concrete și sfaturi acționabile.

**Filosofie Design**:
- **DEEP PERSONALIZATION**: Fiecare detaliu din profil contează
- **CONCRETE RECOMMENDATIONS**: Sume specifice RON, procente, timeframe-uri
- **EMOTIONAL CONNECTION**: Limbaj relatable și accesibil
- **BANKING ACCURACY**: Nu inventează features - folosește descrieri oficiale

**Input**:
```python
{
  "original_summary": "Cont de economii cu dobândă...",
  "product_name": "Cont de Economii Super Acces Plus",
  "user_profile": UserProfile {...},
  "relevance_score": 0.85
}
```

**Adaptări Bazate Pe**:
- **Vârstă**: Tineri (<30) vs Maturitate (30-45) vs Seniori (45+)
- **Familie**: Single vs Căsătorit vs Cu copii
- **Risc**: Scăzut (siguranță) vs Ridicat (creștere)
- **Obiective**: Economii vs Investiții vs Casă vs Pensionare

**Exemplu Personalizare**:

**Profil A**: 25 ani, student, venit 18K, single, risc mediu
```
"La 25 de ani, în perioada studenților, Contul de Economii Super Acces Plus 
este perfectul punct de start pentru construirea obiceiurilor financiare. 
Cu funcția SavingBox, poți economisi automat 3% din fiecare plată cu cardul - 
în medie 50-80 RON/lună dacă cheltuiești 2.000 RON. Începe cu 500 RON și 
vezi cum crește cu dobândă 2-3% fără să blochezi banii."
```

**Profil B**: 45 ani, angajat, venit 90K, căsătorit cu 2 copii, risc scăzut
```
"Pentru familia dumneavoastră cu doi copii și responsabilități financiare 
clare, Contul de Economii Super Acces Plus oferă siguranța unui fond de 
urgență accesibil instant. La venitul dumneavoastră de 7.500 RON/lună, 
recomandăm să mențineți 22.500 RON (3 luni de cheltuieli) în acest cont, 
beneficiind de dobândă 3% pe suma peste 50.000 RON."
```

**Output**: String text personalizat 150-300 cuvinte

---

### 3. 🏷️ Product Title Generation Agent
**Fișier**: `src/agents/product_title_generation_agent.py`

**Responsabilitate Principală**: 
Generează titluri captivante și personalizate pentru produse (6-12 cuvinte).

**Caracteristici**:
- Titluri în română, formal (dumneavoastră)
- 6-12 cuvinte
- Reflectă obiective, vârstă, familie, risc
- Fără emoji, profesional
- Beneficii concrete, nu promisiuni nerealiste

**Input**:
```python
{
  "product_name": "Depozite la Termen",
  "user_profile": UserProfile {...}
}
```

**Exemple Titluri Generate**:

| Profil | Titlu Generat |
|--------|---------------|
| 28 ani, căsătorit, fără copii | "Depozitul Sigur Pentru Familia Dumneavoastră În Creștere" |
| 22 ani, student, single | "Prima Dumneavoastră Economie Cu Dobândă Garantată" |
| 55 ani, pensionar | "Securitate Financiară Pentru Anii De Pensionare Liniștiți" |
| 35 ani, 2 copii | "Economii Protejate Pentru Educația Copiilor Dumneavoastră" |

**Output**: JSON
```json
{
  "title": "Depozitul Sigur Pentru Familia Dumneavoastră În Creștere"
}
```

---

### 4. 💼 Financial Plan Agent
**Fișier**: `src/agents/financial_plan_agent.py`

**Responsabilitate Principală**: 
Generează planuri financiare comprehensive, structurate, acționabile (800-1200 cuvinte).

**Structură Plan (8 Secțiuni Obligatorii)**:

#### 1. Rezumat Executiv
- Situație financiară actuală (2-3 propoziții)
- Obiective principale
- Produse recomandate și scop

#### 2. Analiza Situației Actuale
- **Profil Financiar**: vârstă, venit, familie, profesie, risc
- **Obiective Financiare**: termen scurt (1-3 ani), mediu (3-7 ani), lung (7+ ani)

#### 3. Strategia de Produse Recomandate
Pentru fiecare produs selectat:
- **De ce acest produs**: alignment cu profil și obiective
- **Beneficii principale**: 3-5 beneficii specifice
- **Mod de utilizare recomandat**: pași concreți, sume, frecvență

#### 4. Timeline de Implementare
- **Luna 1-2**: Fundamentele (deschidere conturi, configurări)
- **Luna 3-6**: Consolidare (obiceiuri, ajustări)
- **Luna 7-12**: Creștere (extindere, evaluare)
- **Anul 2+**: Obiective pe termen lung

#### 5. Analiza Riscurilor și Protecție
- Riscuri identificate pentru profil
- Măsuri de protecție prin produse selectate

#### 6. Rezultate Așteptate
- **Termen scurt (1 an)**: Rezultate măsurabile
- **Termen mediu (3-5 ani)**: Progres către obiective majore
- **Termen lung (7+ ani)**: Securitate și independență

#### 7. Pași Următori Imediați
Lista acțiuni concrete prioritizate

#### 8. Recomandări Finale
- Sfaturi personalizate
- Frecvență revizuire plan
- Când să contactezi consultant

**Input**:
```python
{
  "user_profile": {
    "age": 28,
    "annual_income": 65000,
    "marital_status": "married",
    ...
  },
  "selected_products": [
    {
      "product_id": "cont_economii_super_acces",
      "product_name": "Cont de Economii Super Acces Plus",
      "description": "...",
      "benefits": [...],
      "personalized_summary": "..."
    },
    ...
  ]
}
```

**Model Settings**:
- Temperature: 0.7 (balansat între creativitate și consistență)
- Max tokens: 4000 (pentru plan comprehensive)

**Output**: Markdown text 800-1200 cuvinte, structură clară

**Salvare**: `users.user_plan` în PostgreSQL

---

### 5. 📊 Plan Analysis Agent
**Fișier**: `src/agents/plan_analysis_agent.py`

**Responsabilitate Principală**: 
Analizează și prezintă planul financiar într-un mod extrem de personalizat, creând conexiune emoțională.

**Specializare**: Comunicare financiară adaptată la FIECARE aspect al profilului

**Adaptări Multi-Dimensionale**:

#### A) Adaptare pe Vârstă
- **18-25**: Ton energetic modern, digital tools, start habits, future potential
- **26-35**: Balans creștere/stabilitate, carieră, familie, first home
- **36-50**: Consolidare, educație copii, wealth building, sophisticated concepts
- **51+**: Securitate, pensionare, legacy, ton conservator și formal

#### B) Adaptare pe Educație
- **Fără studii superioare/Liceu**: Limbaj simplu, exemple concrete, fără jargon
- **Facultate**: Termeni financiari cu explicații, profesional dar accesibil
- **Master/Doctorat**: Terminologie sofisticată, analiză nuanțată

#### C) Adaptare pe Venit
- **<30K RON/an**: Fundații, emergency fund, pași mici consistenți
- **30-70K RON/an**: Balans saving/growth, obiective mediu-termen
- **>70K RON/an**: Strategii sofisticate, tax optimization, wealth growth

#### D) Adaptare pe Familie
- **Single**: Creștere personală, flexibilitate, independență
- **Married fără copii**: Partnership planning, shared goals
- **Cu copii**: Educație, securitate familie, legacy, stabilitate

#### E) Adaptare pe Risc
- **Scăzut**: Siguranță, garantii, protecție capital, ton reassuring
- **Mediu**: Balans safety/growth, approached măsurat
- **Ridicat**: Growth potential, long-term gains, opportunity-focused

**5 Tipuri de Conținut Generat**:

1. **Plan Introduction**: Opening personalizat, de ce contează acest plan pentru USER
2. **Key Insights**: 3-5 insight-uri critice conectate la profil
3. **Timeline Narrative**: Poveste de progres financiar în timp
4. **Product Synergy**: Cum produsele lucrează împreună pentru acest user specific
5. **Motivational Summary**: Reinforcement, addressare concernuri, next steps

**Exemplu Adaptare**:

**User**: 28 ani, Master, 65K venit, căsătorit, fără copii, risc mediu
```
"Planul dumneavoastră reflectă o etapă dinamică a vieții - consolidarea 
carierei și pregătirea pentru următorul capitol. Cu un venit solid de 
65.000 RON anual, aveți oportunitatea de a construi o fundație financiară 
robustă înainte de extinderea familiei. Strategia propusă combină creștere 
moderată cu securitate, perfect aliniat cu profilul dumneavoastră de risc 
echilibrat. În următorii 12 luni, veți construi un fond de urgență de 
16.250 RON (3 luni de cheltuieli) și veți începe investiții lunare de 
1.000 RON în SmartInvest..."
```

**User**: 55 ani, Liceu, 35K venit, căsătorit, 2 copii, risc scăzut
```
"Cu o experiență de viață bogată și responsabilități familiale importante, 
planul dumneavoastră pune accent pe siguranță și predictibilitate. Produsele 
selectate asigură protecția economiilor pe care le-ați construit cu trudă, 
oferindu-vă liniștea că familia dumneavoastră este protejată. La un venit 
lunar de 2.900 RON, strategia noastră conservatoare prioritizează Depozitul 
la Termen pentru securitate garantată și Contul de Economii pentru 
accesibilitate imediată..."
```

**Model Settings**:
- Temperature: 0.8 (creativitate mai mare pentru conținut engaging)

**Output**: Text românesc 400-600 cuvinte per secțiune

---

### 6. 📧 Email Summary Agent
**Fișier**: `src/agents/email_summary_agent.py`

**Responsabilitate Principală**: 
Compune și trimite email-uri profesionale cu rezumate de produse recomandate.

**Caracteristici Email**:
- Limba română, fără emoji
- Format formal (dumneavoastră)
- Lungime: 120-200 cuvinte
- Focus: top 3-5 produse cu 1 propoziție fiecare
- Ton: profesional, concis, politicos

**MCP Integration**:
- Folosește **MCP Email Server** (`src/mcp-email/`)
- Tool: `send_email(recipient, subject, body)`
- SMTP configuration din environment variables

**Flow**:
1. Primește profil user + recomandări
2. Compune email structurat
3. Apelează `send_email()` tool
4. Confirmă trimitere

**Template Email**:
```
Subiect: Planul Dumneavoastră Financiar Personalizat - Raiffeisen Bank

Stimată/Stimate [Nume],

Am pregătit un plan financiar personalizat bazat pe profilul și 
obiectivele dumneavoastră.

Produsele recomandate:
- [Produs 1]: [Beneficiu principal într-o propoziție]
- [Produs 2]: [Beneficiu principal într-o propoziție]
- [Produs 3]: [Beneficiu principal într-o propoziție]

Pentru detalii complete, accesați platforma sau contactați-ne.

Cu respect,
Echipa Raiffeisen Bank România
```

**Error Handling**: 
- Retry logic pentru SMTP failures
- Clear error messages pentru user

---

### 7. 🔍 Bank Term Extractor Agent
**Fișier**: `src/agents/bank_term_extractor_agent.py`

**Responsabilitate Principală**: 
Extrage și identifică termeni bancari din text cu span-uri exacte pentru highlighting UI.

**Categorii Suportate** (3 fixe):

#### 1. Products
**Română**: card de credit, card de debit, credit imobiliar, credit ipotecar, credit de nevoi personale, descoperit de cont, cont curent, cont de economii, depozit la termen, fonduri de investiții

**Engleză**: credit card, debit card, mortgage, personal loan, consumer loan, overdraft, checking account, current account, savings account, term deposit, time deposit, investment funds

#### 2. Rates
**Română**: dobândă, rata dobânzii, rată fixă, rată variabilă

**Engleză**: interest rate, fixed rate, variable rate, APR, APY, annual percentage rate, annual percentage yield, compound interest

#### 3. Fees
**Română**: comision, penalități, taxă

**Engleză**: fee, commission, maintenance fee, late fee, penalty, foreclosure penalty

**Output Schema (Strict)**:
```json
{
  "categories": {
    "Products": ["credit ipotecar", "cont de economii"],
    "Rates": ["dobândă fixă", "5.20%"],
    "Fees": ["comision administrare"]
  },
  "spans": [
    {
      "start": 0,
      "end": 16,
      "category": "Products",
      "text": "credit ipotecar"
    },
    {
      "start": 22,
      "end": 34,
      "category": "Rates",
      "text": "dobândă fixă"
    }
  ]
}
```

**Reguli Stricte**:
1. Span-urile sunt **non-overlapping** (preferă match-uri mai lungi)
2. `span.text` TREBUIE să fie exact unul din termenii din `categories`
3. Indices bazate pe 0 (Python string indexing)
4. Span-urile align la cuvinte întregi (nu include punctuație trailing)
5. No commentary, DOAR JSON valid
6. Dacă nimic găsit: arrays goale pentru toate categoriile

**Use Case**: Pagina "Bank Term Highlighter" - user paste text, agentul identifică termeni, UI-ul evidențiază cu culori.

**Model Settings**: Include usage tracking

---

### 8. 💬 Bedrock Chat Agent
**Fișier**: `src/agents/bedrock_chat_agent.py`

**Responsabilitate Principală**: 
Agent minimal pentru testare rapidă conexiune AWS Bedrock + Claude.

**Caracteristici**:
- No tools, doar chat
- Răspunsuri concise și clare
- Confirmă că e powered by Claude via Bedrock
- Helpful pentru developeri Raiffeisen

**Scop**: 
Verificare că API key-ul Bedrock funcționează corect înainte de a folosi agenți complecși.

**Utilizare**: 
Pagina `pages/3_Bedrock_Chat_Test.py` - chat simplu test

**Instructions**:
```
"You are a concise, helpful assistant for Raiffeisen developers. 
Answer briefly and clearly. If asked, confirm that you're powered 
by Claude via AWS Bedrock."
```

**Model Settings**: Include usage tracking

---

## Integrări și Dependencies

### 🗄️ Database Integration (PostgreSQL)

#### Tabele
**1. users**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  age INT,
  marital_status TEXT,
  employment_status TEXT,
  has_children BOOLEAN,
  number_of_children INT,
  user_plan TEXT,  -- Markdown plan generat de Financial Plan Agent
  extra JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

**2. products**
```sql
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  product_name TEXT UNIQUE NOT NULL,
  product_description TEXT NOT NULL,  -- Conținut complet fișier .md
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

#### Funcții Helper (db.py)
- `init_users_table()`: Creare tabelă users
- `init_products_table()`: Creare tabelă products
- `populate_products()`: Populate din fișiere .md
- `upsert_user()`: Insert/update user
- `get_user_by_email()`: Retrieve user
- `save_financial_plan()`: Save plan în users.user_plan
- `get_all_products()`: Lista toate produsele
- `get_product_by_name()`: Get produs specific
- `init_database()`: Initialize complet (all tables + populate)

#### Inițializare
```bash
python init_database.py
```

---

### 🔌 MCP Servers

#### 1. MCP Email Server
**Path**: `src/mcp-email/`

**Funcționalitate**: 
Trimite email-uri prin SMTP folosind Model Context Protocol

**Configuration** (Environment Variables):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Raiffeisen Bank
```

**Tools Expuse**:
- `send_email(recipient: str, subject: str, body: str)` → Success/Failure

**Docker**:
```yaml
# docker-compose.yaml
services:
  mcp-email:
    build: ./src/mcp-email
    environment:
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      ...
```

**Utilizare în Agenți**:
```python
from agents.mcp import MCPServerStdio

agent = Agent(
    name="Email Agent",
    mcp_servers=[MCPServerStdio(get_mcp_email_server_config())],
    ...
)
```

#### 2. MCP Postgres Server
**Path**: `src/mcp-postgres/`

**Funcționalitate**: 
Acces la PostgreSQL database prin MCP (pentru query-uri complexe, analytics)

**Configuration**:
```env
APP_DB_HOST=localhost
APP_DB_PORT=5432
APP_DB_USER=app
APP_DB_PASSWORD=secret
APP_DB_NAME=app
APP_DB_SSLMODE=prefer
```

**Tools Expuse**:
- `query(sql: str)` → Results
- `list_tables()` → Table names
- `describe_table(table_name: str)` → Schema

---

### 🎨 Streamlit Pages

#### 1. Homepage.py
Landing page cu overview proiect

#### 2. 0_Login.py
Autentificare utilizatori (check email + password_hash din DB)

#### 3. 00_Home.py
Dashboard după login

#### 4. 1_Register.py
Înregistrare utilizatori noi → insert în `users` table

#### 5. 2_Product_Recommendations_Florea.py
**Agenți folosiți**:
- Product Recommendation Agent (ranking)
- User Experience Summary Agent (personalizare descrieri)
- Product Title Generation Agent (titluri)

**Flow**:
1. Încarcă profil user din session
2. Rankează produse cu Product Recommendation Agent
3. Pentru top produse: generează descrieri personalizate
4. Generează titluri personalizate
5. Display cards cu produse

#### 6. 3_Bedrock_Chat_Test.py
**Agent folosit**: Bedrock Chat Agent

**Scop**: Test conexiune Bedrock

#### 7. 4_Bank_Term_Highlighter.py
**Agent folosit**: Bank Term Extractor Agent

**Flow**:
1. User paste text
2. Extract termeni + spans
3. Highlight text cu culori per categorie

#### 8. 5_View_Plan.py
**Agenți folosiți**:
- Financial Plan Agent (generare plan)
- Plan Analysis Agent (insights opționale)

**Flow**:
1. User selectează produse
2. Generează plan complet
3. Salvează în DB (users.user_plan)
4. Display plan formatat
5. Opțiune trimitere email (Email Summary Agent)

---

## 📦 Dependencies Principale

### Python Packages
```txt
streamlit==1.32.0
openai-agents-sdk
litellm
anthropic
psycopg[binary]
python-dotenv
pydantic
```

### Environment Variables Necesare
```env
# AWS Bedrock
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_DEFAULT_REGION=us-east-1

# LiteLLM Model
LITELLM_MODEL=bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0

# Database
APP_DB_HOST=localhost
APP_DB_PORT=5432
APP_DB_USER=app
APP_DB_PASSWORD=secret
APP_DB_NAME=app
APP_DB_SSLMODE=prefer

# SMTP (Email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Raiffeisen Bank
```

---

## 🚀 Setup și Rulare

### 1. Instalare Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configurare Environment
```bash
cp .env.example .env
# Edit .env cu credentials tale
```

### 3. Inițializare Database
```bash
# Start PostgreSQL (Docker)
docker-compose up -d postgres

# Initialize tables + populate products
python init_database.py
```

### 4. Start MCP Servers (Opțional)
```bash
docker-compose up -d mcp-email mcp-postgres
```

### 5. Run Streamlit App
```bash
streamlit run Homepage.py
```

### 6. Access Application
```
http://localhost:8501
```

---

## 🎯 Best Practices

### Pentru Agenți
1. **Single Responsibility**: Fiecare agent face un lucru foarte bine
2. **Strict JSON Output**: Schema validată cu Pydantic
3. **No Hallucinations**: Doar informații oficiale din catalog
4. **Deep Personalization**: Fiecare detaliu profil contează
5. **Error Handling**: Graceful degradation, clear error messages

### Pentru Database
1. **User Plan Storage**: Salvează planul complet în `users.user_plan`
2. **Product Catalog**: Populate din markdown files (single source of truth)
3. **Indexing**: Email și product_name indexed pentru performance

### Pentru UI
1. **Session State**: Store user profile în `st.session_state`
2. **Loading States**: Spinners pentru operațiuni agent (pot dura 5-10s)
3. **Error Display**: Clear feedback pentru user
4. **Markdown Rendering**: Plan financiar rendered cu `st.markdown()`

---

## 🔮 Future Enhancements

### Agenți
- [ ] **ML-Based Product Scoring**: Replace rule-based cu sklearn model
- [ ] **RAG Integration**: Vector search peste produse pentru Q&A
- [ ] **Multi-Turn Conversations**: Chat agent cu memorie pentru clarificări
- [ ] **A/B Testing Agent**: Testare variante de personalizare

### Database
- [ ] **User Actions Tracking**: Log toate interacțiunile user
- [ ] **Product Performance Analytics**: Care produse sunt cele mai recomandate
- [ ] **Plan Versioning**: Istoricul planurilor generate pentru user

### Features
- [ ] **PDF Export**: Export plan financiar ca PDF profesional
- [ ] **Calendar Integration**: Adaugă deadline-uri din plan în calendar
- [ ] **Push Notifications**: Remindere pentru pași următori
- [ ] **Multi-Language**: Suport engleză pentru expats

---

## 📞 Contact & Support

**Project**: NEXXT AI Banking Assistant
**Bank**: Raiffeisen Bank România
**Tech Stack**: Python, Streamlit, Claude, PostgreSQL

Pentru întrebări despre arhitectura agenților, contactați echipa de dezvoltare.

---

**Ultima actualizare**: 2 Noiembrie 2025
**Versiune**: 1.0

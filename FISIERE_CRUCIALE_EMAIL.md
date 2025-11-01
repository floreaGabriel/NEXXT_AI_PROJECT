# 📧 FIȘIERE CRUCIALE - SISTEM EMAIL CU MCP SERVER

## Fișiere care se FOLOSESC efectiv în aplicație

### 1️⃣ **SERVER MCP** (subprocess care trimite emailurile)
📁 `src/mcp-email/mcp_email/server.py`
```
ROL: Serverul MCP care primește comenzi și trimite emailuri prin SMTP
FOLOSIT: Pornit ca subprocess Python când agentul îl apelează
EXPUNE: Tool "send_email" accesibil prin protocolul MCP
```

### 2️⃣ **CONFIGURARE MCP CLIENT**
📁 `src/utils/mcp_email_client.py`
```python
ROL: Configurare parametri pentru conectarea la MCP Server
FUNCȚII CHEIE:
  - get_mcp_email_server_config() → returnează MCPServerStdioParams
  - verify_smtp_config() → validare configurare SMTP
FOLOSIT: În Streamlit pentru a crea MCP server connection
```

### 3️⃣ **AGENT EMAIL** (definirea agentului)
📁 `src/agents/email_summary_agent.py`
```python
ROL: Definește agentul care generează și trimite emailuri
CONFIGURARE: Include instrucțiuni pentru agent
FOLOSIT: Instructions folosite când se creează temp_agent în Streamlit
```

### 4️⃣ **UI STREAMLIT** (integrarea în aplicație)
📁 `pages/2_Product_Recommendations_Florea.py`
```python
ROL: Pagina Streamlit care permite trimiterea emailurilor
FLOW:
  1. User click "Trimite Email"
  2. Creează MCP Server cu get_mcp_email_server_config()
  3. Conectează: await mcp_server.connect()
  4. Creează agent temporar cu mcp_servers=[mcp_server]
  5. Rulează: await Runner.run(temp_agent, prompt)
  6. MCP Server procesează și trimite email
```

### 5️⃣ **CONFIGURARE SMTP** (variabile de mediu)
📁 `.env`
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sabinstan19@gmail.com
SMTP_PASSWORD=xqcidlcnevcdrrfz
SMTP_TLS=true
FROM_EMAIL=sabinstan19@gmail.com
```

---

## 🔄 FLOW COMPLET (Cum funcționează totul împreună)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER în Streamlit (2_Product_Recommendations_Florea.py) │
│    - Click "Trimite Email prin Agent AI"                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Funcția _send() (async)                                  │
│    - get_mcp_email_server_config() → citește .env          │
│    - MCPServerStdio(config) → creează client MCP            │
│    - await mcp_server.connect() → pornește subprocess      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SUBPROCESS pornit                                        │
│    python -m mcp_email.server                               │
│    (din src/mcp-email/mcp_email/server.py)                 │
│    - Ascultă pe stdin pentru comenzi JSON-RPC              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Agent creat cu MCP server                                │
│    temp_agent = Agent(                                      │
│        instructions=email_summary_agent.instructions,       │
│        mcp_servers=[mcp_server]                             │
│    )                                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Runner.run(temp_agent, prompt)                           │
│    - LLM generează conținutul emailului                     │
│    - LLM decide să apeleze tool "send_email"                │
│    - Trimite comandă JSON-RPC către MCP Server              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. MCP Server (server.py)                                   │
│    - Primește: send_email(to, subject, body)                │
│    - Execută: _send_email_smtp()                            │
│    - Folosește: smtplib cu config din .env                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. SMTP Server (Gmail)                                      │
│    - smtp.gmail.com:587                                     │
│    - TLS encryption                                          │
│    - Trimite emailul către destinatar                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Răspuns înapoi                                           │
│    - MCP Server → "✓ Email sent successfully"              │
│    - Agent → Confirmă trimiterea                            │
│    - Streamlit UI → Afișează succes                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 DEPENDENȚE (packages necesare)

Din `requirements.txt`:
- `mcp>=1.0.0` - Model Context Protocol SDK
- `litellm` - Pentru LLM API
- `openai-agents` - Agents SDK
- `streamlit` - UI framework
- `python-dotenv` - Citire .env

**NU E NEVOIE DE:**
- ❌ Docker (MCP server = subprocess Python, NU container)
- ❌ mcp_sql sau alte servicii MCP

---

## 🗂️ FIȘIERE CARE **NU** SE FOLOSESC (dar există în proiect)

- `src/utils/emailer.py` - Funcție SMTP directă (înlocuită de MCP)
- `test_smtp.py` - Test vechi
- `test_mcp_simple.py` - Test (nu parte din aplicație)
- `test_mcp_explicit.py` - Test (nu parte din aplicație)
- `src/mcp-email/Dockerfile` - Opțional (pentru deployment)
- `src/mcp-email/docker-compose.yaml` - Opțional (pentru deployment)

---

## ✅ CHECKLIST - Ce trebuie să existe pentru ca emailurile să funcționeze:

- [x] `src/mcp-email/mcp_email/server.py` - SERVER MCP
- [x] `src/mcp-email/mcp_email/__init__.py` - Python package marker
- [x] `src/utils/mcp_email_client.py` - CONFIG helper
- [x] `src/agents/email_summary_agent.py` - AGENT definition
- [x] `pages/2_Product_Recommendations_Florea.py` - UI integration
- [x] `.env` - SMTP credentials
- [x] `requirements.txt` - mcp package instalat

---

## 🎯 REZUMAT

**FIȘIERE CRUCIALE (5):**
1. `src/mcp-email/mcp_email/server.py` - Serverul care trimite emailuri
2. `src/utils/mcp_email_client.py` - Configurare conexiune MCP
3. `src/agents/email_summary_agent.py` - Definirea agentului
4. `pages/2_Product_Recommendations_Florea.py` - UI Streamlit
5. `.env` - Credențiale SMTP

**Toate celelalte** fișiere din `src/mcp-email/` (Dockerfile, docker-compose, README) sunt OPȚIONALE și pentru documentație/deployment.

**SISTEM:** MCP Server (subprocess Python) ← Agents SDK → Streamlit UI

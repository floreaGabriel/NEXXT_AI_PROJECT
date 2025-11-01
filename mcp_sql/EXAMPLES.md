# 📖 Exemple de Utilizare MCP Agent

## CLI - Interfață Linie de Comandă

### Pornire CLI
```bash
python run_cli.py
```

### Exemple de conversație

```
👤 Tu: Salut! Poți să-mi explici ce este inteligența artificială?
🤖 Agent: [răspuns generat de OpenAI]
💾 Conversația a fost salvată în baza de date.

👤 Tu: history
📜 Istoric Conversație (Session: f109ec21...):
============================================================
[10:15:23] 👤 Tu: Salut! Poți să-mi explici ce este inteligența artificială?
[10:15:23] 🤖 Agent: Inteligența artificială (AI) este...
============================================================

👤 Tu: new
✨ Sesiune nouă creată: a7b3c94e-1234-5678-90ab-cdef12345678

👤 Tu: quit
👋 La revedere! Toate conversațiile au fost salvate.
```

## API REST - FastAPI

### Pornire Server
```bash
cd mcp_sql
docker compose up -d
```

Serverul va rula pe `http://localhost:8080`

### 1. Health Check
```bash
curl http://localhost:8080/health
```

**Răspuns:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Chat cu Agentul
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explică-mi conceptul de machine learning"
  }'
```

**Răspuns:**
```json
{
  "response": "Machine learning este un subset al inteligenței artificiale...",
  "session_id": "f109ec21-0392-4f81-b6b9-116098673b88"
}
```

### 3. Continuare Conversație (cu session_id)
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Poți să-mi dai exemple?",
    "session_id": "f109ec21-0392-4f81-b6b9-116098673b88"
  }'
```

### 4. Obținere Istoric Conversație
```bash
curl http://localhost:8080/history/f109ec21-0392-4f81-b6b9-116098673b88
```

**Răspuns:**
```json
{
  "session_id": "f109ec21-0392-4f81-b6b9-116098673b88",
  "count": 3,
  "history": [
    {
      "id": 1,
      "user_message": "Explică-mi conceptul de machine learning",
      "agent_response": "Machine learning este...",
      "timestamp": "2025-11-01T10:15:23.123456"
    },
    {
      "id": 2,
      "user_message": "Poți să-mi dai exemple?",
      "agent_response": "Desigur! Câteva exemple...",
      "timestamp": "2025-11-01T10:16:45.654321"
    }
  ]
}
```

## PostgreSQL - Interogare Directă

### Conectare la baza de date
```bash
docker exec -it mcp_postgres psql -U mcp_user -d mcp_db
```

### Comenzi SQL Utile

#### Vezi toate conversațiile
```sql
SELECT * FROM user_inputs ORDER BY timestamp DESC;
```

#### Vezi conversațiile pentru o sesiune
```sql
SELECT 
    id,
    LEFT(user_message, 50) as message,
    timestamp
FROM user_inputs
WHERE session_id = 'f109ec21-0392-4f81-b6b9-116098673b88'
ORDER BY timestamp;
```

#### Statistici
```sql
-- Număr total de conversații
SELECT COUNT(*) as total_conversations FROM user_inputs;

-- Conversații per sesiune
SELECT 
    session_id,
    COUNT(*) as message_count,
    MIN(timestamp) as first_message,
    MAX(timestamp) as last_message
FROM user_inputs
GROUP BY session_id
ORDER BY last_message DESC;

-- Cele mai recente 10 sesiuni
SELECT DISTINCT 
    session_id,
    MAX(timestamp) as last_activity
FROM user_inputs
GROUP BY session_id
ORDER BY last_activity DESC
LIMIT 10;
```

## Python - Utilizare Programatică

### Exemplu simplu
```python
from app.agent import MCPAgent
from dotenv import load_dotenv

load_dotenv()

# Creează agent
agent = MCPAgent()

# Trimite mesaj
response = agent.chat("Salut! Cum te numești?")
print(response)

# Vezi istoric
history = agent.get_session_history()
for entry in history:
    print(f"User: {entry.user_message}")
    print(f"Agent: {entry.agent_response}")
```

### Exemplu avansat cu mai multe sesiuni
```python
from app.agent import MCPAgent
from app.database import SessionLocal, UserInput
import os

# Sesiune 1
agent1 = MCPAgent()
agent1.chat("Care este capitala României?")
agent1.chat("Mulțumesc!")
session1_id = agent1.session_id

# Sesiune 2 (nou agent)
agent2 = MCPAgent()
agent2.chat("Explică-mi fotosinteza")
session2_id = agent2.session_id

# Interogare bază de date pentru ambele sesiuni
db = SessionLocal()
try:
    # Conversații din sesiunea 1
    conv1 = db.query(UserInput).filter(
        UserInput.session_id == session1_id
    ).all()
    
    print(f"Sesiunea 1 are {len(conv1)} conversații")
    
    # Conversații din sesiunea 2
    conv2 = db.query(UserInput).filter(
        UserInput.session_id == session2_id
    ).all()
    
    print(f"Sesiunea 2 are {len(conv2)} conversații")
finally:
    db.close()
```

## Testare Automată

Rulează testul complet:
```bash
python test_agent.py
```

Output așteptat:
```
============================================================
🧪 TEST MCP AGENT - OpenAI + PostgreSQL
============================================================

1️⃣ Inițializare agent...
   ✅ Agent creat cu session_id: f109ec21-0392-4f81-b6b9-116098673b88

2️⃣ Testare conversație cu OpenAI...
   👤 Mesaj 1: Salut! Cum te numești?
   🤖 Răspuns: Sunt un asistent AI...

3️⃣ Verificare bază de date...
   ✅ 3 conversații salvate în PostgreSQL

4️⃣ Testare obținere istoric...
   ✅ Istoric conține 3 intrări

5️⃣ Testare resetare sesiune...
   ✅ Sesiune schimbată: f109ec21... → a7b3c94e...

============================================================
✅ TOATE TESTELE AU TRECUT CU SUCCES!
============================================================
```

## Tips & Tricks

### 1. Folosește modele diferite
```python
# GPT-4 pentru răspunsuri mai complexe
agent.chat("Explică relativitatea generală", model="gpt-4")

# GPT-3.5 pentru răspunsuri mai rapide și ieftine
agent.chat("Salut!", model="gpt-3.5-turbo")
```

### 2. Monitorizează sesiunile
```sql
-- Vezi cât de active sunt sesiunile
SELECT 
    session_id,
    COUNT(*) as messages,
    MAX(timestamp) - MIN(timestamp) as duration
FROM user_inputs
GROUP BY session_id
ORDER BY messages DESC;
```

### 3. Exportă conversații
```bash
# Exportă toate conversațiile într-un CSV
docker exec -it mcp_postgres psql -U mcp_user -d mcp_db \
  -c "COPY (SELECT * FROM user_inputs) TO STDOUT WITH CSV HEADER" \
  > conversations.csv
```

# MCP Agent - OpenAI + PostgreSQL Integration

Sistem MCP (Model Context Protocol) cu agent OpenAI care stochează automat toate conversațiile în PostgreSQL.

## 📋 Cerințe

- Docker & Docker Compose
- Python 3.11+
- OpenAI API Key

## 🚀 Instalare și Configurare

### 1. Configurare variabile de mediu

Creează un fișier `.env` în directorul `mcp_sql/`:

```bash
cp .env.example .env
```

Editează `.env` și adaugă cheia ta OpenAI (sau lasă cheia existentă dacă este validă):
```
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql+psycopg2://mcp_user:mcp_pass@localhost:5432/mcp_db
```

### 2. Pornire PostgreSQL

```bash
cd mcp_sql
docker compose up -d postgres
```

### 3. Instalare dependențe Python

```bash
# Dacă nu ai un virtual environment
python -m venv .venv
source .venv/bin/activate  # pe Linux/Mac
# sau
.venv\Scripts\activate  # pe Windows

# Instalează dependențele
pip install -r requirements.txt
```

### 4. Rulare CLI

```bash
python run_cli.py
```

### 5. Test automat (opțional)

```bash
python test_agent.py
```

## 💻 Utilizare CLI

După pornirea CLI-ului, vei putea:

- **Chata cu agentul**: Tastează orice mesaj
- **Vezi istoricul**: Tastează `history`
- **Sesiune nouă**: Tastează `new`
- **Ajutor**: Tastează `help`
- **Ieșire**: Tastează `quit` sau `exit`

Exemplu:
```
👤 Tu: Ce este inteligența artificială?
🤖 Agent: [răspuns generat de OpenAI]
💾 Conversația a fost salvată în baza de date.
```

## 🌐 API REST

Serverul FastAPI rulează pe `http://localhost:8080`

### Endpoints disponibile:

#### 1. Health Check
```bash
curl http://localhost:8080/health
```

#### 2. Chat
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Salut! Cum te numești?"}'
```

#### 3. Istoric Conversație
```bash
curl http://localhost:8080/history/{session_id}
```

## 📊 Structura Bazei de Date

Tabel `user_inputs`:
- `id`: Integer (Primary Key)
- `session_id`: String (Session ID unic)
- `user_message`: Text (Mesajul utilizatorului)
- `agent_response`: Text (Răspunsul agentului)
- `timestamp`: DateTime (Timestamp conversație)

## 🛠️ Dezvoltare

### Structura Proiectului

```
mcp_sql/
├── app/
│   ├── agent.py          # Agent OpenAI cu MCP
│   ├── cli.py            # Interfață CLI
│   ├── database.py       # Modele SQLAlchemy
│   └── main.py           # Server FastAPI
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── .env.example
```

### Comenzi Utile

```bash
# Verifică logs
docker-compose logs -f mcp-server

# Resetează baza de date
docker-compose down -v
docker-compose up -d

# Accesează PostgreSQL direct
docker exec -it mcp_postgres psql -U mcp_user -d mcp_db

# Query exemplu în PostgreSQL
SELECT * FROM user_inputs ORDER BY timestamp DESC LIMIT 10;
```

## 🔧 Troubleshooting

### Eroare: "OPENAI_API_KEY nu este setat"
Asigură-te că ai creat fișierul `.env` și ai adăugat cheia API validă.

### Eroare la conectare PostgreSQL
Verifică că containerul PostgreSQL rulează:
```bash
docker-compose ps
```

### Reset complet
```bash
docker-compose down -v
rm -rf data/
docker-compose up -d
```

## 📝 Licență

MIT

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import MCPAgent
from .database import init_db, SessionLocal, UserInput
import os

# Inițializează aplicația FastAPI
app = FastAPI(title="MCP Agent API", version="1.0.0")

# Inițializează baza de date
init_db()

# Modelele Pydantic pentru request/response
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.on_event("startup")
async def startup_event():
    """Event handler la pornirea aplicației"""
    print("🚀 MCP Agent Server pornit!")
    print(f"📊 Database URL: {os.getenv('DATABASE_URL', 'localhost')}")

@app.get("/")
async def root():
    return {
        "message": "MCP Server cu OpenAI Agent și PostgreSQL",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "history": "/history/{session_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Verifică starea serverului și a bazei de date"""
    try:
        db = SessionLocal()
        # Testează conexiunea la baza de date
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint pentru chat cu agentul"""
    try:
        # Verifică dacă există OPENAI_API_KEY
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY nu este setat"
            )
        
        agent = MCPAgent()
        
        # Dacă există session_id, îl folosește
        if request.session_id:
            agent.session_id = request.session_id
        
        response = agent.chat(request.message)
        
        return ChatResponse(
            response=response,
            session_id=agent.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Obține istoricul pentru o sesiune"""
    db = SessionLocal()
    try:
        inputs = db.query(UserInput).filter(
            UserInput.session_id == session_id
        ).order_by(UserInput.timestamp).all()
        
        return {
            "session_id": session_id,
            "count": len(inputs),
            "history": [
                {
                    "id": inp.id,
                    "user_message": inp.user_message,
                    "agent_response": inp.agent_response,
                    "timestamp": inp.timestamp.isoformat()
                }
                for inp in inputs
            ]
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


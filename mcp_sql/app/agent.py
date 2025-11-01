import os
from typing import Optional
from openai import OpenAI
import uuid

# Importuri locale
try:
    from .database import SessionLocal, UserInput, init_db
except ImportError:
    from database import SessionLocal, UserInput, init_db


class MCPAgent:
    """Agent OpenAI cu integrare PostgreSQL prin MCP"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY nu este setat!")
        
        self.client = OpenAI(api_key=self.api_key)
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        
        # Inițializează baza de date
        init_db()
    
    def save_to_database(self, user_message: str, agent_response: str):
        """Salvează conversația în PostgreSQL"""
        db = SessionLocal()
        try:
            user_input = UserInput(
                session_id=self.session_id,
                user_message=user_message,
                agent_response=agent_response
            )
            db.add(user_input)
            db.commit()
            db.refresh(user_input)
            return user_input
        except Exception as e:
            db.rollback()
            print(f"Eroare la salvarea în baza de date: {e}")
            raise
        finally:
            db.close()
    
    def chat(self, user_message: str, model: str = "gpt-4") -> str:
        """Procesează mesajul utilizatorului și returnează răspunsul agentului"""
        
        # Adaugă mesajul utilizatorului la istoric
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Apelează API-ul OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000
            )
            
            agent_response = response.choices[0].message.content
            
            # Adaugă răspunsul agentului la istoric
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            # Salvează în baza de date
            self.save_to_database(user_message, agent_response)
            
            return agent_response
            
        except Exception as e:
            error_msg = f"Eroare la procesarea mesajului: {e}"
            print(error_msg)
            return error_msg
    
    def get_session_history(self):
        """Obține istoricul conversației curente din baza de date"""
        db = SessionLocal()
        try:
            inputs = db.query(UserInput).filter(
                UserInput.session_id == self.session_id
            ).order_by(UserInput.timestamp).all()
            return inputs
        finally:
            db.close()
    
    def reset_session(self):
        """Resetează sesiunea curentă"""
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        print(f"Sesiune nouă creată: {self.session_id}")

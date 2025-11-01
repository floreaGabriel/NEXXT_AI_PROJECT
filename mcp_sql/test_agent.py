#!/usr/bin/env python3
"""
Script de testare pentru MCP Agent
Demonstrează funcționalitatea agentului și salvarea în baza de date
"""
import sys
import os

# Adaugă directorul părinte la path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import MCPAgent
from app.database import SessionLocal, UserInput
from dotenv import load_dotenv

# Încarcă variabilele de mediu
load_dotenv()


def test_agent():
    """Testează funcționalitatea completă a agentului"""
    
    print("=" * 60)
    print("🧪 TEST MCP AGENT - OpenAI + PostgreSQL")
    print("=" * 60)
    
    # Verifică OPENAI_API_KEY
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ EROARE: OPENAI_API_KEY nu este setat!")
        return False
    
    try:
        # 1. Inițializează agentul
        print("\n1️⃣ Inițializare agent...")
        agent = MCPAgent()
        print(f"   ✅ Agent creat cu session_id: {agent.session_id}")
        
        # 2. Testează conversația
        print("\n2️⃣ Testare conversație cu OpenAI...")
        
        test_messages = [
            "Salut! Cum te numești?",
            "Ce zi este azi?",
            "Mulțumesc!"
        ]
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\n   👤 Mesaj {i}: {msg}")
            response = agent.chat(msg, model="gpt-3.5-turbo")
            print(f"   🤖 Răspuns: {response[:100]}...")
        
        # 3. Verifică salvarea în baza de date
        print("\n3️⃣ Verificare bază de date...")
        db = SessionLocal()
        try:
            saved_inputs = db.query(UserInput).filter(
                UserInput.session_id == agent.session_id
            ).count()
            print(f"   ✅ {saved_inputs} conversații salvate în PostgreSQL")
            
            # Afișează ultimele conversații
            latest = db.query(UserInput).filter(
                UserInput.session_id == agent.session_id
            ).order_by(UserInput.timestamp.desc()).limit(3).all()
            
            print("\n   📝 Ultimele conversații din DB:")
            for entry in reversed(latest):
                print(f"      • User: {entry.user_message[:50]}...")
                print(f"        Agent: {entry.agent_response[:50]}...")
        finally:
            db.close()
        
        # 4. Testează istoricul
        print("\n4️⃣ Testare obținere istoric...")
        history = agent.get_session_history()
        print(f"   ✅ Istoric conține {len(history)} intrări")
        
        # 5. Testează resetare sesiune
        print("\n5️⃣ Testare resetare sesiune...")
        old_session = agent.session_id
        agent.reset_session()
        print(f"   ✅ Sesiune schimbată: {old_session[:8]}... → {agent.session_id[:8]}...")
        
        print("\n" + "=" * 60)
        print("✅ TOATE TESTELE AU TRECUT CU SUCCES!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ EROARE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)

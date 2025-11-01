#!/usr/bin/env python3
"""
CLI pentru interacțiune cu MCP Agent folosind OpenAI și PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv

# Importuri locale
try:
    from .agent import MCPAgent
except ImportError:
    from agent import MCPAgent

# Încarcă variabilele de mediu
load_dotenv()


def print_banner():
    """Afișează banner-ul aplicației"""
    banner = """
    ╔════════════════════════════════════════════════╗
    ║   MCP Agent - OpenAI + PostgreSQL Integration  ║
    ║   Toate conversațiile sunt salvate automat     ║
    ╚════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Afișează comenzile disponibile"""
    help_text = """
    Comenzi disponibile:
    - Tastează orice mesaj pentru a chata cu agentul
    - 'history' - Afișează istoricul conversației curente
    - 'new' - Începe o sesiune nouă
    - 'help' - Afișează acest mesaj
    - 'quit' sau 'exit' - Ieșire din aplicație
    """
    print(help_text)


def display_history(agent: MCPAgent):
    """Afișează istoricul conversației"""
    history = agent.get_session_history()
    
    if not history:
        print("\n📝 Nu există istoric pentru această sesiune.\n")
        return
    
    print(f"\n📜 Istoric Conversație (Session: {agent.session_id[:8]}...):")
    print("=" * 60)
    
    for entry in history:
        timestamp = entry.timestamp.strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 👤 Tu: {entry.user_message}")
        print(f"[{timestamp}] 🤖 Agent: {entry.agent_response}")
    
    print("=" * 60 + "\n")


def main():
    """Funcția principală CLI"""
    print_banner()
    
    # Verifică dacă OPENAI_API_KEY este setat
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Eroare: OPENAI_API_KEY nu este setat!")
        print("Te rog să setezi OPENAI_API_KEY în variabilele de mediu sau în fișierul .env")
        sys.exit(1)
    
    try:
        # Inițializează agentul
        agent = MCPAgent()
        print(f"✅ Agent inițializat cu succes!")
        print(f"📊 Session ID: {agent.session_id}")
        print_help()
        
        # Buclă principală
        while True:
            try:
                user_input = input("\n👤 Tu: ").strip()
                
                if not user_input:
                    continue
                
                # Verifică comenzile speciale
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 La revedere! Toate conversațiile au fost salvate.\n")
                    break
                
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                
                elif user_input.lower() == 'history':
                    display_history(agent)
                    continue
                
                elif user_input.lower() == 'new':
                    agent.reset_session()
                    print(f"✨ Sesiune nouă creată: {agent.session_id}")
                    continue
                
                # Procesează mesajul
                print("\n🤖 Agent: ", end="", flush=True)
                response = agent.chat(user_input)
                print(response)
                print(f"\n💾 Conversația a fost salvată în baza de date.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Întrerupt de utilizator. La revedere!\n")
                break
            
            except Exception as e:
                print(f"\n❌ Eroare: {e}")
                print("Încearcă din nou sau tastează 'help' pentru ajutor.\n")
    
    except Exception as e:
        print(f"\n❌ Eroare la inițializarea agentului: {e}")
        print("Verifică configurația și încearcă din nou.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

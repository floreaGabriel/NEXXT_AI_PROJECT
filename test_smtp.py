#!/usr/bin/env python3
"""
Test SMTP Configuration - Verifică dacă setările din .env funcționează
"""

import os
import sys
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def test_smtp_config():
    """Test SMTP configuration from .env"""
    
    print("=" * 60)
    print("🔍 VERIFICARE CONFIGURAȚIE SMTP")
    print("=" * 60)
    
    # Get config
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_tls = os.getenv("SMTP_TLS", "true")
    from_email = os.getenv("FROM_EMAIL")
    
    # Check configuration
    errors = []
    warnings = []
    
    print("\n📋 Configurație detectată:")
    print(f"  SMTP_HOST: {smtp_host or '❌ NU SETAT'}")
    print(f"  SMTP_PORT: {smtp_port or '❌ NU SETAT'}")
    print(f"  SMTP_USER: {smtp_user or '❌ NU SETAT'}")
    
    if smtp_password:
        print(f"  SMTP_PASSWORD: {'*' * len(smtp_password)} ({len(smtp_password)} caractere)")
        
        # Check password length
        if len(smtp_password) != 16:
            errors.append(f"❌ SMTP_PASSWORD are {len(smtp_password)} caractere (ar trebui să fie 16!)")
            if smtp_password.endswith(' '):
                errors.append("   └─> Parolă are spațiu la sfârșit!")
            if ' ' in smtp_password:
                errors.append("   └─> Parolă conține spații în interior!")
    else:
        print(f"  SMTP_PASSWORD: ❌ NU SETAT")
        errors.append("❌ SMTP_PASSWORD nu este setat în .env")
    
    print(f"  SMTP_TLS: {smtp_tls}")
    print(f"  FROM_EMAIL: {from_email or '❌ NU SETAT'}")
    
    # Validation
    if not smtp_host:
        errors.append("❌ SMTP_HOST nu este setat")
    
    if not smtp_user:
        errors.append("❌ SMTP_USER nu este setat")
    
    if smtp_user and from_email and smtp_user != from_email:
        warnings.append(f"⚠️  SMTP_USER ({smtp_user}) diferit de FROM_EMAIL ({from_email})")
        warnings.append("   └─> Gmail necesită să fie identice!")
    
    # Print results
    print("\n" + "=" * 60)
    if errors:
        print("❌ ERORI GĂSITE:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print("\n⚠️  AVERTISMENTE:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("✅ Configurația arată CORECTĂ!")
        print("\n🧪 Testare conexiune SMTP...")
        
        # Test SMTP connection
        try:
            import smtplib
            
            port = int(smtp_port) if smtp_port else 587
            use_tls = smtp_tls.lower() in {'1', 'true', 'yes'}
            
            print(f"  → Conectare la {smtp_host}:{port}...")
            
            if use_tls:
                server = smtplib.SMTP(smtp_host, port, timeout=10)
                print(f"  ✅ Conexiune stabilită")
                print(f"  → Activare TLS...")
                server.starttls()
                print(f"  ✅ TLS activat")
            else:
                server = smtplib.SMTP(smtp_host, port, timeout=10)
                print(f"  ✅ Conexiune stabilită")
            
            if smtp_user and smtp_password:
                print(f"  → Autentificare ca {smtp_user}...")
                server.login(smtp_user, smtp_password)
                print(f"  ✅ Autentificare reușită!")
            
            server.quit()
            print("\n" + "=" * 60)
            print("🎉 SMTP FUNCȚIONEAZĂ PERFECT!")
            print("=" * 60)
            print("\n✅ Poți trimite emailuri din aplicație!")
            return True
            
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"❌ EROARE LA TESTARE SMTP:")
            print(f"  {str(e)}")
            print("=" * 60)
            
            error_msg = str(e).lower()
            
            print("\n💡 SOLUȚII POSIBILE:")
            
            if 'authentication failed' in error_msg or 'username and password not accepted' in error_msg:
                print("  1. Verifică că parola este corectă (16 caractere, fără spații)")
                print("  2. Generează o parolă NOUĂ pentru sabinstan19@gmail.com")
                print("     → https://myaccount.google.com/apppasswords")
                print("  3. Verifică că ai 2-Step Verification activat")
            
            elif 'connection' in error_msg or 'timeout' in error_msg:
                print("  1. Verifică conexiunea la internet")
                print("  2. Verifică firewall-ul")
                print("  3. Încearcă port 465 în loc de 587")
            
            elif 'ssl' in error_msg or 'tls' in error_msg:
                print("  1. Verifică SMTP_TLS=true în .env")
                print("  2. Sau încearcă SMTP_PORT=465 cu SMTP_TLS=false")
            
            else:
                print(f"  → Verifică eroarea de mai sus")
            
            return False
    
    print("=" * 60)
    print("\n⚠️  Repară erorile de mai sus și rulează din nou acest script!")
    return False


if __name__ == "__main__":
    print("\n🔧 Test SMTP pentru NEXXT_AI_PROJECT\n")
    
    if not Path(".env").exists():
        print("❌ Fișierul .env nu există!")
        print("   Copiază .env.example în .env și completează-l.")
        sys.exit(1)
    
    success = test_smtp_config()
    sys.exit(0 if success else 1)

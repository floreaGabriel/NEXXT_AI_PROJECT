# ✅ Checklist Configurare Email

## Verificare Rapidă `.env`

Copiază `.env.example` în `.env` și configurează:

```bash
cp .env.example .env
nano .env  # sau deschide cu orice editor
```

### ✔️ Configurație Corectă pentru Gmail

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=raiffaisent.ai-agent@gmail.com    # Email-ul "bot" (expeditor)
SMTP_PASSWORD=abcd efgh ijkl mnop            # App Password (16 caractere)
SMTP_TLS=true
FROM_EMAIL=raiffaisent.ai-agent@gmail.com   # TREBUIE să fie = SMTP_USER!
```

**⚠️ CRITICAL:** `SMTP_USER` și `FROM_EMAIL` **TREBUIE** să fie identice pentru Gmail!

---

## 🔑 Pași pentru App Password (Gmail)

Dacă folosești `raiffaisent.ai-agent@gmail.com`:

1. **Login** la contul Gmail: https://gmail.com
2. **Activează 2-Step Verification:**
   - Mergi la: https://myaccount.google.com/security
   - Click **2-Step Verification** → Activează

3. **Generează App Password:**
   - Mergi la: https://myaccount.google.com/apppasswords
   - **App:** Mail
   - **Device:** Other (Custom) → scrie "NEXXT_AI"
   - Click **Generate**
   - **Copiază** parola de 16 caractere (ex: `abcd efgh ijkl mnop`)

4. **Adaugă în `.env`:**
   ```bash
   SMTP_PASSWORD=abcdefghijklmnop  # Șterge spațiile!
   ```

---

## 🧪 Test Rapid

### 1. Verifică variabilele sunt setate:

```bash
# În terminal, din directorul proiectului:
source .venv/bin/activate  # Activează virtual env
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('SMTP_HOST:', os.getenv('SMTP_HOST'))
print('SMTP_USER:', os.getenv('SMTP_USER'))
print('FROM_EMAIL:', os.getenv('FROM_EMAIL'))
print('SMTP_PASSWORD:', '***' if os.getenv('SMTP_PASSWORD') else 'NOT SET')
"
```

**Output așteptat:**
```
SMTP_HOST: smtp.gmail.com
SMTP_USER: raiffaisent.ai-agent@gmail.com
FROM_EMAIL: raiffaisent.ai-agent@gmail.com
SMTP_PASSWORD: ***
```

### 2. Test conectare SMTP:

```bash
python -c "
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()
host = os.getenv('SMTP_HOST')
port = int(os.getenv('SMTP_PORT', 587))
user = os.getenv('SMTP_USER')
pwd = os.getenv('SMTP_PASSWORD')

try:
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, pwd)
        print('✅ SMTP login SUCCESS!')
except Exception as e:
    print(f'❌ SMTP login FAILED: {e}')
"
```

**Output așteptat:**
```
✅ SMTP login SUCCESS!
```

### 3. Test trimitere email complet:

```bash
python -c "
from dotenv import load_dotenv
load_dotenv()
from src.utils.emailer import send_email

# Schimbă cu emailul tău de test:
test_email = 'tau.email.personal@gmail.com'

try:
    send_email(
        to=test_email,
        subject='Test NEXXT AI - Email Summary',
        body='Acesta este un test. Dacă primești acest email, configurația funcționează! 🎉'
    )
    print(f'✅ Email trimis cu succes către: {test_email}')
    print('📬 Verifică inbox-ul (și Spam)!')
except Exception as e:
    print(f'❌ Eroare: {e}')
"
```

---

## 📧 Flow-ul Complet în Aplicație

### Când user apasă "Trimite-mi summary-ul pe email":

```
1. User logat ca: john.doe@example.com (din Login/Register)
   ↓
2. Click buton "Trimite-mi summary-ul pe email"
   ↓
3. Aplicația preia: user_email = session_state["auth"]["email"]
   → user_email = "john.doe@example.com"
   ↓
4. Claude AI generează conținutul emailului personalizat
   ↓
5. email_summary_agent apelează send_email() cu:
   - to: "john.doe@example.com"  ← DESTINATAR (user logat)
   - subject: "Recomandările dumneavoastră personalizate"
   - body: <conținut generat de AI>
   ↓
6. emailer.py se conectează la Gmail SMTP cu:
   - SMTP_USER: "raiffaisent.ai-agent@gmail.com"  ← AUTENTIFICARE
   - SMTP_PASSWORD: <app password>
   ↓
7. Email trimis:
   - From: raiffaisent.ai-agent@gmail.com  ← EXPEDITOR (FROM_EMAIL)
   - To: john.doe@example.com              ← DESTINATAR (user logat)
   ↓
8. john.doe@example.com primește emailul în inbox! 📬
```

---

## ❌ Erori Comune & Soluții

### "Authentication failed (535-5.7.8)"
**Cauză:** Parola incorectă sau nu folosești App Password  
**Soluție:** Generează App Password nou și adaugă în `.env`

### "SMTP_USER and FROM_EMAIL must match"
**Cauză:** Ai setat FROM_EMAIL diferit de SMTP_USER  
**Soluție:** Setează ambele la `raiffaisent.ai-agent@gmail.com`

### "Less secure app access"
**Cauză:** Gmail blochează aplicații fără 2FA  
**Soluție:** Activează 2-Step Verification + folosește App Password

### "Connection refused"
**Cauză:** Port greșit sau firewall  
**Soluție:** Verifică `SMTP_PORT=587` și `SMTP_TLS=true`

---

## 🎯 Rezumat

- ✅ **SMTP_USER** = Email BOT (raiffaisent.ai-agent@gmail.com)
- ✅ **FROM_EMAIL** = Email BOT (ACELAȘI ca SMTP_USER!)
- ✅ **Destinatar** = Email user logat (din session_state)
- ✅ **App Password** = 16 caractere (NU parola normală)

**Configurația ta `raiffaisent.ai-agent@gmail.com` este PERFECTĂ dacă:**
1. Ai acces la acel cont Gmail
2. Ai activat 2-Step Verification pe el
3. Ai generat App Password pentru el
4. Ai setat corect `SMTP_USER = FROM_EMAIL`

---

**Succes! 🚀**

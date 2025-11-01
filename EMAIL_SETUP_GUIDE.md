# 📧 Ghid Configurare Email (SMTP)

Acest ghid explică cum să configurezi funcționalitatea de trimitere email pentru pagina de **Recomandări Produse**.

## 🎯 Ce Face Email-ul?

Când un utilizator autentificat apasă butonul **"Trimite-mi summary-ul pe email"**, aplicația:
1. Generează un email personalizat în limba română cu top 3-5 recomandări
2. Folosește AI (Claude via Bedrock) pentru a compune textul
3. Trimite emailul prin SMTP la adresa utilizatorului autentificat

## ⚙️ Configurare Necesară

### 1. Copiază fișierul `.env.example` în `.env`

```bash
cp .env.example .env
```

### 2. Configurează Variabilele SMTP în `.env`

Trebuie să setezi următoarele variabile în fișierul `.env`:

```bash
SMTP_HOST=smtp.gmail.com              # Server SMTP
SMTP_PORT=587                          # Port (587 pentru TLS)
SMTP_USER=your.email@gmail.com         # Username SMTP (de obicei emailul tău)
SMTP_PASSWORD=your_app_password        # Parola SMTP (vezi mai jos!)
SMTP_TLS=true                          # Folosește TLS (recomandat)
FROM_EMAIL=your.email@gmail.com        # Adresa "From" (opțional)
```

---

## 📮 Opțiuni SMTP Recomandate

### 🅰️ **Gmail (Recomandat pentru Testare)**

#### Pas 1: Activează 2-Step Verification
1. Accesează: https://myaccount.google.com/security
2. Activează **2-Step Verification**

#### Pas 2: Generează App Password
1. Mergi la: https://myaccount.google.com/apppasswords
2. Selectează **App**: Mail
3. Selectează **Device**: Other (Custom name) - scrie "NEXXT_AI"
4. Click **Generate**
5. Copiază parola de **16 caractere** (fără spații)

#### Pas 3: Configurează `.env`
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tau.email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop    # Parola de 16 caractere de la pas 2
SMTP_TLS=true
FROM_EMAIL=tau.email@gmail.com
```

**⚠️ IMPORTANT:** 
- **NU** folosi parola normală Gmail! Folosește **App Password**!
- App Password-ul funcționează chiar dacă ai 2FA activat

---

### 🅱️ **Outlook / Office 365**

```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=tau.email@outlook.com
SMTP_PASSWORD=parola_ta_outlook
SMTP_TLS=true
FROM_EMAIL=tau.email@outlook.com
```

**Note:**
- Outlook permite folosirea parolei normale (nu necesită app password)
- Asigură-te că contul nu are restricții de securitate care blochează SMTP

---

### 🅲 **SendGrid (Recomandat pentru Producție)**

SendGrid oferă 100 emailuri/zi gratuit.

#### Pas 1: Creează Cont SendGrid
1. Mergi la: https://signup.sendgrid.com/
2. Creează cont gratuit

#### Pas 2: Generează API Key
1. Dashboard → Settings → API Keys
2. Click **Create API Key**
3. Name: "NEXXT_AI_SMTP"
4. Permissions: **Full Access** (sau doar Mail Send)
5. Copiază API Key-ul (se afișează o singură dată!)

#### Pas 3: Configurează `.env`
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey                           # Literal "apikey" - NU schimba!
SMTP_PASSWORD=SG.xxx_your_api_key_xxx     # API Key-ul tău
SMTP_TLS=true
FROM_EMAIL=tau.email@exemplu.com           # Email-ul tău verificat în SendGrid
```

**⚠️ IMPORTANT:**
- `SMTP_USER` trebuie să fie literal **"apikey"** (nu emailul tău)
- Trebuie să verifici domeniul/emailul în SendGrid pentru a trimite

---

### 🅳 **Amazon SES (AWS Simple Email Service)**

Ideal dacă folosești deja AWS.

#### Pas 1: Configurează SES
1. AWS Console → SES → SMTP Settings
2. Click **Create SMTP Credentials**
3. Notează: `SMTP Endpoint`, `Port`, `Username`, `Password`

#### Pas 2: Verifică Email Sender
1. SES → Email Addresses → Verify a New Email Address
2. Verifică emailul din care vrei să trimiți

#### Pas 3: Configurează `.env`
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com    # Depinde de regiunea ta
SMTP_PORT=587
SMTP_USER=your_smtp_username                     # De la Pas 1
SMTP_PASSWORD=your_smtp_password                 # De la Pas 1
SMTP_TLS=true
FROM_EMAIL=verified@yourdomain.com               # Email verificat în SES
```

---

## 🧪 Testare Email

### 1. Asigură-te că `.env` este configurat corect

```bash
# Verifică că fișierul .env există și conține variabilele SMTP
cat .env | grep SMTP
```

### 2. Restart Aplicația Streamlit

```bash
# Oprește aplicația (Ctrl+C) și repornește-o
streamlit run Homepage.py
```

### 3. Testează Trimiterea

1. Autentifică-te în aplicație (Login sau Register)
2. Mergi la pagina **Recomandări Produse**
3. Generează recomandări
4. Scroll down la secțiunea **✉️ Primește sumarul pe email**
5. Click **"Trimite-mi summary-ul pe email"**

### 4. Verifică Rezultatul

**Succes:** ✅ Mesaj verde: "Email trimis (dacă SMTP este configurat corect)."

**Eroare:** ❌ Mesaj roșu cu detalii - verifică:
- Variabilele SMTP din `.env`
- App Password pentru Gmail
- Conexiunea la internet
- Logs în terminal

---

## 🔍 Debugging - Erori Comune

### Eroare: "SMTP_HOST is not configured"
**Cauză:** Variabila `SMTP_HOST` lipsește din `.env`  
**Soluție:** Adaugă `SMTP_HOST=smtp.gmail.com` în `.env` și restart

---

### Eroare: "Authentication failed" (Gmail)
**Cauză:** Folosești parola normală în loc de App Password  
**Soluție:** 
1. Activează 2-Step Verification
2. Generează App Password (vezi secțiunea Gmail)
3. Folosește app password în `SMTP_PASSWORD`

---

### Eroare: "Connection timed out"
**Cauză:** Port blocat de firewall sau ISP  
**Soluție:**
- Încearcă port `465` (SSL) în loc de `587` (TLS)
- Setează `SMTP_TLS=false` dacă folosești port 465
- Verifică firewall-ul

---

### Eroare: "Sender address rejected"
**Cauză:** `FROM_EMAIL` nu este verificat/autorizat  
**Soluție:**
- Pentru Gmail: folosește același email ca `SMTP_USER`
- Pentru SendGrid/SES: verifică domeniul/emailul în dashboard

---

## 📝 Variabile SMTP - Referință Completă

| Variabilă | Descriere | Exemplu | Obligatorie? |
|-----------|-----------|---------|--------------|
| `SMTP_HOST` | Server SMTP | `smtp.gmail.com` | ✅ DA |
| `SMTP_PORT` | Port SMTP | `587` (TLS) sau `465` (SSL) | Nu (default: 587) |
| `SMTP_USER` | Username autentificare | `your.email@gmail.com` | Nu (dar recomandat) |
| `SMTP_PASSWORD` | Parola/API key | App password sau API key | Nu (dar recomandat) |
| `SMTP_TLS` | Folosește TLS/STARTTLS | `true` sau `false` | Nu (default: true) |
| `FROM_EMAIL` | Adresa expeditor | `your.email@gmail.com` | Nu (default: SMTP_USER) |

---

## 🎓 Cum Funcționează Codul?

### Flow-ul Email

```
1. User apasă "Trimite-mi summary-ul pe email"
   ↓
2. Aplicația preia emailul user-ului din session_state
   ↓
3. Generează un prompt pentru email_summary_agent (Claude AI)
   ↓
4. Claude compune emailul în română (120-200 cuvinte)
   ↓
5. Claude apelează tool-ul send_email() cu to/subject/body
   ↓
6. src/utils/emailer.py se conectează la SMTP_HOST
   ↓
7. Trimite emailul prin SMTP
   ↓
8. Utilizatorul primește emailul în inbox
```

### Fișiere Implicate

- **`src/utils/emailer.py`** - Funcția de bază `send_email()` care folosește `smtplib`
- **`src/agents/email_summary_agent.py`** - Agent AI care compune emailul personalizat
- **`pages/2_Product_Recommendations_Florea.py`** - UI pentru trimitere email (linia ~537)

---

## 🚀 Quick Start (Gmail)

Pentru testare rapidă cu Gmail:

```bash
# 1. Copiază .env
cp .env.example .env

# 2. Editează .env și adaugă:
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=tau.email@gmail.com
# SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App Password (16 caractere)
# SMTP_TLS=true
# FROM_EMAIL=tau.email@gmail.com

# 3. Restart aplicația
streamlit run Homepage.py
```

---

## 💡 Tips

- **Testare locală:** Gmail este cea mai simplă opțiune
- **Producție:** Folosește SendGrid sau Amazon SES pentru rate limits mai mari
- **Securitate:** **NICIODATĂ** nu face commit la `.env` în Git! (este deja în `.gitignore`)
- **Email-uri spam:** Primele emailuri pot ajunge în Spam - verifică folder-ul Spam

---

## ❓ Întrebări Frecvente

**Q: De ce am nevoie de App Password pentru Gmail?**  
A: Google blochează aplicațiile care folosesc parola normală din motive de securitate. App Password-ul este specific pentru aplicații terțe.

**Q: Pot trimite emailuri fără SMTP?**  
A: Nu. SMTP este protocolul standard pentru trimitere emailuri. Alternativele (API-uri email) necesită cod diferit.

**Q: Câte emailuri pot trimite?**  
A: 
- **Gmail:** ~500/zi (limită Google)
- **SendGrid Free:** 100/zi
- **Amazon SES:** 200/zi (în sandbox), apoi pay-as-you-go

**Q: Emailul nu ajunge - ce verific?**  
A: 
1. Verifică folder-ul Spam
2. Verifică logs în terminal
3. Testează conexiunea SMTP cu telnet: `telnet smtp.gmail.com 587`

---

## 📞 Support

Dacă întâmpini probleme:
1. Verifică logs-urile în terminal (detalii despre erori)
2. Testează setările SMTP cu un tool extern (ex: [SMTP Tester](https://www.smtper.net/))
3. Verifică documentația provider-ului SMTP (Gmail, SendGrid, etc.)

---

**Succes cu configurarea! 🎉**

# ALsistem NC Portal — Pacchetto completo

## Contenuto
```
alsistem-backend/
├── app.py              ← Server Flask (Python) — API complete
├── requirements.txt    ← Dipendenze Python
├── Procfile            ← Configurazione avvio server
├── railway.toml        ← Configurazione Railway
├── static/
│   └── index.html      ← Front-end completo (HTML/CSS/JS)
├── alsistem.db         ← Database SQLite con dati demo
├── DEPLOY_WINDOWS.bat  ← Deploy automatico Windows ← PARTI DA QUI
├── deploy.sh           ← Deploy automatico Mac/Linux
└── README.md           ← Questo file
```

---

## DEPLOY IN PRODUZIONE (link pubblico gratis)

### Windows — doppio click su DEPLOY_WINDOWS.bat

Prerequisiti: Node.js → https://nodejs.org

Il file fa tutto da solo:
1. Installa Railway CLI
2. Apre browser per login (gratis, usa GitHub)
3. Deploy automatico
4. Ti dà link pubblico tipo: https://alsistem-nc-portal.up.railway.app

### Mac/Linux
```bash
chmod +x deploy.sh && ./deploy.sh
```

---

## TEST IN LOCALE

```bash
pip install -r requirements.txt
python app.py
```
Apri: http://localhost:5000

---

## API Endpoints

| Metodo | URL | Descrizione |
|--------|-----|-------------|
| POST | /api/login | Login utente |
| GET | /api/nc | Lista NC |
| POST | /api/nc | Crea nuova NC |
| PUT | /api/nc/:id | Aggiorna NC |
| GET | /api/stats | KPI dashboard |
| GET | /api/fornitori | Lista fornitori |
| POST | /api/fornitori | Crea fornitore |

---

## Credenziali demo

- mario.rossi / password123
- admin / admin
- oppure qualsiasi username (modalita demo)

## Stack tecnico
- Backend: Python 3 + Flask
- Database: SQLite
- Frontend: HTML/CSS/JS puro
- Hosting: Railway.app (gratuito)

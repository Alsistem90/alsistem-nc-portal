from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os, json
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

DB = 'alsistem.db'

# ═══════════════════════════════════════
# DATABASE INIT
# ═══════════════════════════════════════
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS utenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        consociata TEXT NOT NULL,
        ruolo TEXT DEFAULT 'operatore'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS fornitori (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        consociata TEXT NOT NULL,
        stato TEXT DEFAULT 'Attivo',
        piva TEXT,
        referente TEXT,
        telefono TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS nc (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        tipo TEXT NOT NULL,
        desc TEXT NOT NULL,
        fornitore TEXT DEFAULT '—',
        fornitore_email TEXT DEFAULT '',
        cc_emails TEXT DEFAULT '[]',
        sev TEXT NOT NULL,
        area TEXT NOT NULL,
        causa TEXT NOT NULL,
        trattamento TEXT NOT NULL,
        assegnatario TEXT NOT NULL,
        scadenza TEXT NOT NULL,
        stato TEXT DEFAULT 'Aperta',
        articolo TEXT DEFAULT '—',
        qty INTEGER DEFAULT 0,
        consociata TEXT NOT NULL,
        note TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )''')

    # Seed utenti
    users = [
        ('mario.rossi', 'password123', 'Fresia Alluminio s.p.a.', 'admin'),
        ('anna.verdi', 'password123', 'Alca s.r.l.', 'operatore'),
        ('luca.bianchi', 'password123', 'Aluroma Metalli s.r.l.', 'operatore'),
        ('sara.neri', 'password123', 'CMP s.r.l.', 'operatore'),
        ('admin', 'admin', 'Fresia Alluminio s.p.a.', 'admin'),
    ]
    for u in users:
        try:
            c.execute('INSERT INTO utenti (username, password_hash, consociata, ruolo) VALUES (?,?,?,?)',
                      (u[0], hashlib.sha256(u[1].encode()).hexdigest(), u[2], u[3]))
        except: pass

    # Seed fornitori
    forn = [
        ('VEND001','Alpha Metalli S.p.A.','qualita@alpha.it','Fresia Alluminio s.p.a.','Attivo'),
        ('VEND002','Beta Alloys s.r.l.','qc@beta.it','Alca s.r.l.','Sospeso'),
        ('VEND003','Gamma Metals','qa@gamma.com','EdilSider s.p.a.','Attivo'),
        ('VEND004','Delta Aluminium','quality@delta.com','Meral s.p.a.','Attivo'),
    ]
    for f in forn:
        try:
            c.execute('INSERT INTO fornitori (codice,nome,email,consociata,stato) VALUES (?,?,?,?,?)', f)
        except: pass

    # Seed NC
    ncs = [
        ('NC-2024-001','2024-10-15','Fornitore','Difetto dimensionale profili alluminio 25x25','Alpha Metalli S.p.A.','qualita@alpha.it','[]','Critica','Produzione','Difetto dimensionale','Reso','Mario Rossi','2024-10-22','In lavorazione','Profilo AL 25x25',120,'Fresia Alluminio s.p.a.','Lotto completamente non conforme alle specifiche di tolleranza.'),
        ('NC-2024-002','2024-10-18','Fornitore','Ossidazione superficiale maniglie zama NF pZ','Beta Alloys s.r.l.','qc@beta.it','[]','Alta','Qualità','Ossidazione','Rottamazione','Anna Verdi','2024-10-25','In approvazione','Maniglia zama NF pZ',50,'Fresia Alluminio s.p.a.',''),
        ('NC-2024-003','2024-10-20','Interna','Graffiatura superficiale su profili verniciati','—','','[]','Media','Produzione','Difetto verniciatura','Rilavorazione','Luca Bianchi','2024-10-30','Aperta','Profilo verniciato RAL 9016',35,'Fresia Alluminio s.p.a.',''),
        ('NC-2024-004','2024-09-28','Fornitore','Imballo danneggiato durante trasporto — merce bagnata','Gamma Metals','qa@gamma.com','[]','Alta','Logistica','Imballo danneggiato','Deroga','Sara Neri','2024-10-05','Chiusa','Barre alluminio 6060',200,'Fresia Alluminio s.p.a.','Risolto con accordo forfettario.'),
        ('NC-2024-005','2024-10-21','Fornitore','Errore prelievo grezzo — materiale errato in spedizione','Delta Aluminium','quality@delta.com','[]','Alta','Acquisti','Errore prelievo grezzo','Reso','Mario Rossi','2024-10-28','Assegnata','Lingotto AL 6082',400,'Fresia Alluminio s.p.a.',''),
        ('NC-2024-006','2024-10-22','Fornitore','Materiale grezzo fuori specifica — durezza HB > tolleranza','Alpha Metalli S.p.A.','qualita@alpha.it','[]','Critica','Produzione','Materiale grezzo NC','Rottamazione','Anna Verdi','2024-10-29','Aperta','Billetta AL 6063',80,'Fresia Alluminio s.p.a.',''),
    ]
    for n in ncs:
        try:
            c.execute('''INSERT INTO nc (id,date,tipo,desc,fornitore,fornitore_email,cc_emails,sev,area,causa,
                trattamento,assegnatario,scadenza,stato,articolo,qty,consociata,note,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (*n, datetime.now().isoformat()))
        except: pass

    conn.commit()
    conn.close()

# ═══════════════════════════════════════
# AUTH
# ═══════════════════════════════════════
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username','').strip()
    password = data.get('password','').strip()
    consociata = data.get('consociata','').strip()

    if not username or not consociata:
        return jsonify({'error': 'Username e consociata richiesti'}), 400

    conn = get_db()
    # Se password vuota, accettiamo qualsiasi utente (demo mode)
    if password:
        ph = hashlib.sha256(password.encode()).hexdigest()
        user = conn.execute('SELECT * FROM utenti WHERE username=? AND password_hash=?', (username, ph)).fetchone()
    else:
        user = conn.execute('SELECT * FROM utenti WHERE username=?', (username,)).fetchone()
        if not user:
            # crea utente al volo (demo)
            conn.execute('INSERT OR IGNORE INTO utenti (username,password_hash,consociata,ruolo) VALUES (?,?,?,?)',
                         (username, '', consociata, 'operatore'))
            conn.commit()
            user = conn.execute('SELECT * FROM utenti WHERE username=?', (username,)).fetchone()

    conn.close()
    if not user:
        return jsonify({'error': 'Credenziali non valide'}), 401

    initials = ''.join(p[0].upper() for p in username.split('.')[:2])
    return jsonify({
        'user': username,
        'consociata': consociata,
        'ruolo': user['ruolo'] if user else 'operatore',
        'initials': initials or username[:2].upper()
    })

# ═══════════════════════════════════════
# NC ENDPOINTS
# ═══════════════════════════════════════
@app.route('/api/nc', methods=['GET'])
def get_nc():
    consociata = request.args.get('consociata')
    stato = request.args.get('stato')
    sev = request.args.get('sev')
    tipo = request.args.get('tipo')
    q = request.args.get('q','')

    conn = get_db()
    sql = 'SELECT * FROM nc WHERE 1=1'
    params = []
    if consociata:
        sql += ' AND consociata=?'; params.append(consociata)
    if stato and stato != 'Tutti':
        sql += ' AND stato=?'; params.append(stato)
    if sev and sev != 'Tutte':
        sql += ' AND sev=?'; params.append(sev)
    if tipo and tipo != 'Tutti':
        sql += ' AND tipo=?'; params.append(tipo)
    if q:
        sql += ' AND (desc LIKE ? OR fornitore LIKE ? OR id LIKE ?)'
        params += [f'%{q}%', f'%{q}%', f'%{q}%']
    sql += ' ORDER BY date DESC'

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['ccEmails'] = json.loads(d.get('cc_emails','[]') or '[]')
        d['fornitoreEmail'] = d.pop('fornitore_email','')
        result.append(d)
    return jsonify(result)

@app.route('/api/nc', methods=['POST'])
def create_nc():
    data = request.json
    conn = get_db()

    # Generate ID
    count = conn.execute('SELECT COUNT(*) FROM nc WHERE consociata=?', (data['consociata'],)).fetchone()[0]
    year = datetime.now().year
    nc_id = f"NC-{year}-{str(count+1).zfill(3)}"

    scadenza = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    conn.execute('''INSERT INTO nc (id,date,tipo,desc,fornitore,fornitore_email,cc_emails,sev,area,causa,
        trattamento,assegnatario,scadenza,stato,articolo,qty,consociata,note,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        nc_id,
        datetime.now().strftime('%Y-%m-%d'),
        data.get('tipo','Fornitore'),
        data['desc'],
        data.get('fornitore','—'),
        data.get('fornitoreEmail',''),
        json.dumps(data.get('ccEmails',[])),
        data.get('sev','Alta'),
        data.get('area','Produzione'),
        data.get('causa',''),
        data.get('trattamento',''),
        data.get('assegnatario',''),
        scadenza,
        'Aperta',
        data.get('articolo','—'),
        int(data.get('qty',0)),
        data['consociata'],
        data.get('note',''),
        datetime.now().isoformat()
    ))
    conn.commit()
    row = conn.execute('SELECT * FROM nc WHERE id=?', (nc_id,)).fetchone()
    conn.close()
    d = dict(row)
    d['ccEmails'] = json.loads(d.get('cc_emails','[]') or '[]')
    d['fornitoreEmail'] = d.pop('fornitore_email','')
    return jsonify(d), 201

@app.route('/api/nc/<nc_id>', methods=['PUT'])
def update_nc(nc_id):
    data = request.json
    conn = get_db()
    fields = []
    params = []
    allowed = ['stato','note','assegnatario','trattamento','sev']
    for f in allowed:
        if f in data:
            fields.append(f'{f}=?')
            params.append(data[f])
    if not fields:
        return jsonify({'error': 'Nessun campo da aggiornare'}), 400
    params.append(nc_id)
    conn.execute(f'UPDATE nc SET {", ".join(fields)} WHERE id=?', params)
    conn.commit()
    row = conn.execute('SELECT * FROM nc WHERE id=?', (nc_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'NC non trovata'}), 404
    d = dict(row)
    d['ccEmails'] = json.loads(d.get('cc_emails','[]') or '[]')
    d['fornitoreEmail'] = d.pop('fornitore_email','')
    return jsonify(d)

@app.route('/api/nc/<nc_id>', methods=['DELETE'])
def delete_nc(nc_id):
    conn = get_db()
    conn.execute('DELETE FROM nc WHERE id=?', (nc_id,))
    conn.commit()
    conn.close()
    return jsonify({'deleted': nc_id})

# ═══════════════════════════════════════
# STATS / DASHBOARD
# ═══════════════════════════════════════
@app.route('/api/stats', methods=['GET'])
def get_stats():
    consociata = request.args.get('consociata')
    conn = get_db()
    p = [consociata] if consociata else []
    w = 'WHERE consociata=?' if consociata else ''

    tot    = conn.execute(f'SELECT COUNT(*) FROM nc {w}', p).fetchone()[0]
    aperte = conn.execute(f'SELECT COUNT(*) FROM nc {w} {"AND" if w else "WHERE"} stato="Aperta"', p + ([] if not w else [])).fetchone()[0] if w else conn.execute('SELECT COUNT(*) FROM nc WHERE stato="Aperta"').fetchone()[0]

    # Ricalcola con filtri corretti
    base = 'SELECT COUNT(*) FROM nc WHERE consociata=?' if consociata else 'SELECT COUNT(*) FROM nc WHERE 1=1'
    def count(extra, extra_p=[]):
        sql = base + extra
        return conn.execute(sql, p + extra_p).fetchone()[0]

    stats = {
        'totale': count(''),
        'aperte': count(' AND stato="Aperta"'),
        'approvazione': count(' AND stato="In approvazione"'),
        'lavorazione': count(' AND (stato="In lavorazione" OR stato="Assegnata")'),
        'chiuse': count(' AND stato="Chiusa"'),
    }

    # Cause (Pareto)
    rows = conn.execute(f'SELECT causa, COUNT(*) as n FROM nc {"WHERE consociata=?" if consociata else ""} GROUP BY causa ORDER BY n DESC LIMIT 6', p).fetchall()
    stats['cause'] = [{'causa': r['causa'], 'count': r['n']} for r in rows]

    # Severità distribution
    rows2 = conn.execute(f'SELECT sev, COUNT(*) as n FROM nc {"WHERE consociata=?" if consociata else ""} GROUP BY sev', p).fetchall()
    stats['severita'] = {r['sev']: r['n'] for r in rows2}

    conn.close()
    return jsonify(stats)

# ═══════════════════════════════════════
# FORNITORI
# ═══════════════════════════════════════
@app.route('/api/fornitori', methods=['GET'])
def get_fornitori():
    consociata = request.args.get('consociata')
    conn = get_db()
    if consociata:
        rows = conn.execute('SELECT * FROM fornitori WHERE consociata=? ORDER BY nome', (consociata,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM fornitori ORDER BY nome').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/fornitori', methods=['POST'])
def create_fornitore():
    data = request.json
    conn = get_db()
    try:
        conn.execute('INSERT INTO fornitori (codice,nome,email,consociata,stato,piva,referente,telefono) VALUES (?,?,?,?,?,?,?,?)',
            (data['codice'], data['nome'], data['email'], data['consociata'],
             data.get('stato','Attivo'), data.get('piva',''), data.get('referente',''), data.get('telefono','')))
        conn.commit()
        row = conn.execute('SELECT * FROM fornitori WHERE codice=?', (data['codice'],)).fetchone()
        conn.close()
        return jsonify(dict(row)), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

# ═══════════════════════════════════════
# SERVE FRONTEND
# ═══════════════════════════════════════
@app.route('/')
def index():
    if os.path.exists('static/index.html'):
        return send_from_directory('static', 'index.html')
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

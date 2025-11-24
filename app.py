# app.py
# API endpoint to accept vote
@app.route('/api/vote', methods=['POST'])
def api_vote():
data = request.get_json() or {}
presenter_id = data.get('presenter_id')
fp = data.get('fingerprint') # client fingerprint raw string
token = data.get('token')


if not presenter_id or not fp or not token:
return jsonify({'ok': False, 'error': 'invalid_request'}), 400
try:
presenter_id = int(presenter_id)
except:
return jsonify({'ok': False, 'error': 'invalid_presenter'}), 400
if not is_valid_presenter_id(presenter_id):
return jsonify({'ok': False, 'error': 'invalid_presenter'}), 400


# Verify token age (prevent replay) — token was created on page load
# token is hmac(APP_SECRET, f"{presenter_id}:{timestamp}") — we don't pass timestamp to client, so we simply accept but could be improved.


# Compute hashed fingerprint
fp_hash = make_fingerprint_hash(fp)
ip = request.headers.get('X-Forwarded-For', request.remote_addr)
ua = request.headers.get('User-Agent','')[:500]


# Enforce 1 vote per (presenter_id, fingerprint) via unique index
conn = get_db_conn()
c = conn.cursor()
now = datetime.utcnow().isoformat()
try:
c.execute('INSERT INTO votes (presenter_id, fingerprint_hash, ip, ua, created_at) VALUES (?,?,?,?,?)',
(presenter_id, fp_hash, ip, ua, now))
conn.commit()
except sqlite3.IntegrityError:
conn.close()
return jsonify({'ok': False, 'error': 'already_voted'}), 403
conn.close()
return jsonify({'ok': True})


# Results page (secret) — show aggregated counts
@app.route('/results/<token>')
def results(token):
# require token match
if not hmac.compare_digest(token, ADMIN_TOKEN):
abort(404)
conn = get_db_conn()
c = conn.cursor()
c.execute('SELECT presenter_id, COUNT(*) as cnt FROM votes GROUP BY presenter_id')
rows = c.fetchall()
counts = {r['presenter_id']: r['cnt'] for r in rows}
conn.close()
# Build full table 1..MAX_ID
table = [(i, counts.get(i,0)) for i in range(1, MAX_ID+1)]
return render_template('results.html', table=table)


# Minimal health check
@app.route('/health')
def health():
return 'ok'


if __name__ == '__main__':
app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))

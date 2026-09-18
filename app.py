import os, sqlite3, datetime, json, uuid
from flask import Flask, request, jsonify, g, render_template, session, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, 'appstore.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'admin123')
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'appstore-secret-key-2024')
CORS(app)

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
        try: db.execute('PRAGMA journal_mode=WAL')
        except: pass
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_db', None)
    if db is not None: db.close()

def get_admin_password():
    try:
        with sqlite3.connect(DB) as db:
            row = db.execute("SELECT value FROM config WHERE key='admin_password'").fetchone()
            if row and row[0]: return row[0]
    except: pass
    return ADMIN_TOKEN

def set_admin_password(new_pwd):
    try:
        with sqlite3.connect(DB) as db:
            db.execute("INSERT OR REPLACE INTO config(key,value) VALUES('admin_password', ?)", (new_pwd,))
            db.commit()
    except: pass

def init_admin_pwd():
    try:
        with sqlite3.connect(DB) as db:
            row = db.execute("SELECT value FROM config WHERE key='admin_password'").fetchone()
            if not row:
                db.execute("INSERT INTO config(key,value) VALUES('admin_password', ?)", (ADMIN_TOKEN,))
                db.commit()
    except: pass

def init_db():
    with sqlite3.connect(DB) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS apps(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,description TEXT DEFAULT '',icon_url TEXT DEFAULT '',download_url TEXT DEFAULT '',category TEXT DEFAULT '工具',downloads INTEGER DEFAULT 0,featured INTEGER DEFAULT 0,created_at TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY,value TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, token TEXT, created_at TEXT)''')
        try: db.execute('ALTER TABLE users ADD COLUMN stats TEXT DEFAULT ""')
        except: pass
        if db.execute('SELECT COUNT(*) FROM apps').fetchone()[0] == 0:
            db.execute("INSERT INTO apps(name,description,category,featured,created_at) VALUES(?,?,?,?,?)", ('示例应用','这是一个示例应用','工具',1,datetime.datetime.utcnow().isoformat()))
        defaults = {
            'home_title':'首页','home_subtitle':'欢迎使用应用库',
            'apps_title':'软件','apps_subtitle':'免费【破解软件】',
            'tools_title':'工具','tools_subtitle':'聚合工具箱',
            'my_title':'我的','my_subtitle':'人生不过三万天，请做个向前冲锋的勇士。',
            'notice_text':'欢迎使用应用库',
            'share_link':'http://localhost:8000/store',
            'home_banners':json.dumps([{"image":"","title":"应用库","desc":"破解软件 永久免费","link":"","color":"#1a1a1a"}]),
            'notice_cards':json.dumps([{"title":"无法下载软件\n【教程】","color":"#f0f0f0"}]),
            'software_tabs':'全部,工具,影音,社交',
            'tools_tabs':json.dumps([{"name":"工具","type":"cards","cards":[]}]),
            'tools_cards':json.dumps([]),
            'my_page':json.dumps({"avatar":"A","title":"应用库","tag1":"v1.0","tag2":"免费","cards":[{"icon":"star","title":"永久地址","sub":"收藏起来","content":"请收藏本页"}]})
        }
        for k,v in defaults.items():
            db.execute('INSERT OR IGNORE INTO config(key,value) VALUES(?,?)',(k,v))

def is_admin():
    if session.get('admin'): return True
    token = request.headers.get('X-Admin-Token') or request.args.get('token')
    return token == get_admin_password()

ADMIN_LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>后台登录</title><style>*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,sans-serif}body{background:linear-gradient(135deg,#1a1d23 0%,#2d3340 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}.box{background:#fff;border-radius:20px;padding:32px 24px;width:100%;max-width:360px;box-shadow:0 20px 60px rgba(0,0,0,.3)}.box h1{font-size:22px;font-weight:800;color:#1a1d23;margin-bottom:6px;text-align:center}.box p{font-size:13px;color:#999;text-align:center;margin-bottom:24px}.box input{width:100%;padding:14px 16px;border:1.5px solid #e8eaf0;border-radius:12px;font-size:15px;outline:none;background:#fafbfd;margin-bottom:14px}.box input:focus{border-color:#1a1d23}.box button{width:100%;padding:14px;background:#1a1d23;color:#fff;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer}.err{color:#ff4757;font-size:13px;text-align:center;margin-bottom:10px;display:none}.err.show{display:block}</style></head><body><div class="box"><h1>后台登录</h1><p>请输入管理密码</p><div class="err" id="err">密码错误</div><input type="password" id="pwd" placeholder="管理密码" onkeydown="if(event.key==='Enter')doLogin()"><button onclick="doLogin()">登录</button></div><script>async function doLogin(){const pwd=document.getElementById('pwd').value;if(!pwd){showErr('请输入密码');return}const res=await fetch('/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pwd})});if(res.ok){window.location.href='/admin'}else{showErr('密码错误')}}function showErr(m){const e=document.getElementById('err');e.innerText=m;e.classList.add('show')}</script></body></html>"""

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return ADMIN_LOGIN_HTML
    d = request.get_json() or {}
    if (d.get('password') or '') == get_admin_password():
        session['admin'] = True
        return jsonify({'ok': True})
    return jsonify({'error': '密码错误'}), 401

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')

@app.route('/api/admin/change-password', methods=['POST'])
def api_change_password():
    if not session.get('admin'): return jsonify({'error':'unauthorized'}), 401
    d = request.get_json() or {}
    if (d.get('old_password') or '') != get_admin_password():
        return jsonify({'error': '原密码错误'}), 400
    new_pwd = d.get('new_password') or ''
    if len(new_pwd) < 4:
        return jsonify({'error': '新密码至少4位'}), 400
    set_admin_password(new_pwd)
    return jsonify({'ok': True})

@app.route('/api/admin/users')
def api_admin_users():
    if not is_admin(): return jsonify({'error':'unauthorized'}), 401
    rows = get_db().execute('SELECT id, username, created_at FROM users ORDER BY id DESC').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if not is_admin(): return jsonify({'error':'unauthorized'}), 401
    if 'file' not in request.files: return jsonify({'error':'没有文件'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error':'文件为空'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'png'
    new_filename = f"{int(datetime.datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}.{ext}"
    file.save(os.path.join(UPLOAD_DIR, new_filename))
    return jsonify({'url': f'/static/uploads/{new_filename}'})

@app.route('/api/config', methods=['GET'])
def get_config():
    rows = get_db().execute('SELECT key,value FROM config').fetchall()
    config = {r['key']: r['value'] for r in rows}
    for k in ['home_banners','notice_cards','tools_cards','tools_tabs','my_page']:
        if k in config and isinstance(config[k], str):
            try: config[k] = json.loads(config[k])
            except: pass
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def set_config():
    if not is_admin(): return jsonify({'error':'unauthorized'}), 401
    db = get_db()
    for k, v in (request.get_json() or {}).items():
        val = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else str(v)
        db.execute('INSERT OR REPLACE INTO config(key,value) VALUES(?,?)', (k, val))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/apps', methods=['GET', 'POST'])
def api_apps():
    db = get_db()
    if request.method == 'GET':
        search, category = request.args.get('search',''), request.args.get('category')
        sql, args, conds = 'SELECT * FROM apps', [], []
        if search: conds.append('name LIKE ?'); args.append('%'+search+'%')
        if category and category != '全部': conds.append('category = ?'); args.append(category)
        if conds: sql += ' WHERE ' + ' AND '.join(conds)
        sql += ' ORDER BY id DESC'
        return jsonify([dict(r) for r in db.execute(sql, args).fetchall()])
    if not is_admin(): return jsonify({'error':'unauthorized'}), 401
    d = request.get_json() or {}
    db.execute("INSERT INTO apps(name,description,icon_url,download_url,category,featured,created_at) VALUES(?,?,?,?,?,?,?)",
               (d.get('name',''),d.get('description',''),d.get('icon_url',''),d.get('download_url',''),
                d.get('category','工具'),1 if d.get('featured') else 0,datetime.datetime.utcnow().isoformat()))
    db.commit()
    return jsonify({'ok': True}), 201

@app.route('/api/apps/<int:app_id>', methods=['GET', 'PUT', 'DELETE'])
def api_app_detail(app_id):
    db = get_db()
    if request.method == 'GET':
        db.execute('UPDATE apps SET downloads=downloads+1 WHERE id=?', (app_id,)); db.commit()
        return jsonify(dict(db.execute('SELECT * FROM apps WHERE id=?', (app_id,)).fetchone()))
    if not is_admin(): return jsonify({'error':'unauthorized'}), 401
    if request.method == 'PUT':
        d = request.get_json() or {}
        for f in ['name','description','icon_url','download_url','category']:
            if f in d: db.execute(f'UPDATE apps SET {f}=? WHERE id=?', (d[f], app_id))
        if 'featured' in d: db.execute('UPDATE apps SET featured=? WHERE id=?', (1 if d['featured'] else 0, app_id))
        db.commit()
        return jsonify({'ok': True})
    db.execute('DELETE FROM apps WHERE id=?', (app_id,)); db.commit()
    return jsonify({'ok': True})

@app.route('/api/categories')
def api_categories():
    return jsonify([r['category'] for r in get_db().execute('SELECT DISTINCT category FROM apps WHERE category IS NOT NULL AND category != ""').fetchall()])

@app.route('/api/register', methods=['POST'])
def api_register():
    d = request.get_json() or {}
    username = (d.get('username') or '').strip()
    password = d.get('password') or ''
    if not username or not password: return jsonify({'error':'用户名和密码不能为空'}), 400
    if len(username) < 2: return jsonify({'error':'用户名至少2个字符'}), 400
    if len(password) < 4: return jsonify({'error':'密码至少4位'}), 400
    db = get_db()
    if db.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone():
        return jsonify({'error':'用户名已存在'}), 400
    token = uuid.uuid4().hex
    db.execute('INSERT INTO users(username,password,token,created_at) VALUES(?,?,?,?)',
               (username, generate_password_hash(password), token, datetime.datetime.utcnow().isoformat()))
    db.commit()
    return jsonify({'ok': True, 'token': token, 'username': username})

@app.route('/api/login', methods=['POST'])
def api_login():
    d = request.get_json() or {}
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username=?', ((d.get('username') or '').strip(),)).fetchone()
    if not user or not check_password_hash(user['password'], d.get('password') or ''):
        return jsonify({'error':'用户名或密码错误'}), 401
    token = uuid.uuid4().hex
    db.execute('UPDATE users SET token=? WHERE id=?', (token, user['id']))
    db.commit()
    return jsonify({'ok': True, 'token': token, 'username': user['username']})

@app.route('/api/me')
def api_me():
    token = request.headers.get('X-User-Token') or request.args.get('token')
    if not token: return jsonify({'error':'unauthorized'}), 401
    user = get_db().execute('SELECT id, username, created_at FROM users WHERE token=?', (token,)).fetchone()
    if not user: return jsonify({'error':'invalid token'}), 401
    return jsonify(dict(user))

@app.route('/api/logout', methods=['POST'])
def api_logout():
    token = request.headers.get('X-User-Token') or request.args.get('token')
    if token:
        db = get_db()
        db.execute('UPDATE users SET token=NULL WHERE token=?', (token,))
        db.commit()
    return jsonify({'ok': True})

@app.route('/api/user/stats', methods=['GET', 'POST'])
def api_user_stats():
    token = request.headers.get('X-User-Token') or request.args.get('token')
    if not token: return jsonify({'error':'unauthorized'}), 401
    db = get_db()
    user = db.execute('SELECT id, stats FROM users WHERE token=?', (token,)).fetchone()
    if not user: return jsonify({'error':'invalid'}), 401
    if request.method == 'GET':
        try: return jsonify(json.loads(user['stats'] or '{}'))
        except: return jsonify({})
    d = request.get_json() or {}
    db.execute('UPDATE users SET stats=? WHERE id=?', (json.dumps(d, ensure_ascii=False), user['id']))
    db.commit()
    return jsonify({'ok': True})

@app.route('/admin')
def admin():
    if not session.get('admin'): return redirect('/admin/login')
    return render_template('admin.html')

@app.route('/store')
def store(): return render_template('store.html')

@app.route('/')
def index(): return jsonify({'name': 'AppStore API', 'status': 'ok'})

@app.errorhandler(500)
def err500(e): return jsonify({'error':'server error','detail':str(e)}), 500

@app.errorhandler(404)
def err404(e):
    if request.path.startswith('/api/'): return jsonify({'error':'not found'}), 404
    return e

init_db()
init_admin_pwd()

if __name__ == '__main__':
    print('\n  应用库启动: http://0.0.0.0:8000\n')
    app.run(host='0.0.0.0', port=8000)

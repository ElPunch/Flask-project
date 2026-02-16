from flask import Flask, render_template, redirect, url_for, request, g, session
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secreto_cambiar_en_produccion'

DATABASE = 'bestiario.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email    TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS criptidos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre        TEXT NOT NULL,
                especie       TEXT,
                habitat       TEXT,
                descripcion   TEXT,
                nivel_peligro INTEGER,
                usuario_id    INTEGER,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS avistamientos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha      TEXT,
                ubicacion  TEXT,
                detalles   TEXT,
                criptido_id INTEGER,
                FOREIGN KEY(criptido_id) REFERENCES criptidos(id)
            );
        ''')
        db.commit()

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM usuarios WHERE id = ?', (user_id,)
        ).fetchone()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    db = get_db()
    criptidos = db.execute('SELECT * FROM criptidos ORDER BY id DESC').fetchall()
    return render_template('index.html', criptidos=criptidos)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nombre        = request.form['nombre']
        especie       = request.form['especie']
        habitat       = request.form['habitat']
        descripcion   = request.form['descripcion']
        nivel_peligro = request.form['nivel_peligro']

        db = get_db()
        db.execute(
            '''INSERT INTO criptidos (nombre, especie, habitat, descripcion, nivel_peligro)
               VALUES (?, ?, ?, ?, ?)''',
            (nombre, especie, habitat, descripcion, nivel_peligro)
        )
        db.commit()
        return redirect(url_for('index'))

    return render_template('create_criptido.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    db = get_db()

    if request.method == 'POST':
        nombre        = request.form['nombre']
        especie       = request.form['especie']
        habitat       = request.form['habitat']
        descripcion   = request.form['descripcion']
        nivel_peligro = request.form['nivel_peligro']

        db.execute(
            '''UPDATE criptidos
               SET nombre=?, especie=?, habitat=?, descripcion=?, nivel_peligro=?
               WHERE id=?''',
            (nombre, especie, habitat, descripcion, nivel_peligro, id)
        )
        db.commit()
        return redirect(url_for('index'))

    criptido = db.execute('SELECT * FROM criptidos WHERE id = ?', (id,)).fetchone()
    return render_template('edit_criptido.html', criptido=criptido)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM avistamientos WHERE criptido_id = ?', (id,))
    db.execute('DELETE FROM criptidos WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']

        db = get_db()
        existente = db.execute(
            'SELECT id FROM usuarios WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()

        if existente:
            error = 'El usuario o email ya está registrado.'
        else:
            db.execute(
                'INSERT INTO usuarios (username, password, email) VALUES (?, ?, ?)',
                (username, password, email)
            )
            db.commit()
            return redirect(url_for('login'))

    return render_template('registro.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        usuario = db.execute(
            'SELECT * FROM usuarios WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()

        if usuario:
            session.clear()
            session['user_id'] = usuario['id']
            return redirect(url_for('index'))
        else:
            error = 'Credenciales incorrectas. Acceso denegado.'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
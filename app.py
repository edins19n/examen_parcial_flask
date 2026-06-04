from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'clave_secreta_examen_aplicada'

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        # Crear tabla usuarios
        conn.execute('''
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                nombre TEXT NOT NULL
            )
        ''')
        # Crear tabla productos
        conn.execute('''
            CREATE TABLE productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                categoria TEXT
            )
        ''')
        
        # Insertar datos de prueba para simular el sistema
        conn.execute("INSERT INTO usuarios (username, password, nombre) VALUES ('admin', 'admin123', 'Axel Porras')")
        
        productos_demo = [
            ('P001', 'Laptop Gamer Halion', 'Core i7, 16GB RAM, 512GB SSD', 3499.00, 10, 'Tecnología'),
            ('P002', 'Teclado Mecánico DSD6', 'Teclado RGB con switches mecánicos', 180.00, 25, 'Periféricos'),
            ('P003', 'Monitor 24 Pulgadas', 'Full HD 144Hz para desarrollo y gaming', 750.00, 15, 'Monitores'),
            ('P004', 'Mouse Óptico Inalámbrico', 'Alta precisión ajustable DPI', 90.00, 40, 'Periféricos')
        ]
        conn.executemany("INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES (?, ?, ?, ?, ?, ?)", productos_demo)
        
        conn.commit()
        conn.close()

# Inicializar la base de datos automáticamente al arrancar
init_db()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['nombre'] = user['nombre']
            return redirect(url_for('principal'))
        else:
            return render_template('login.html', error='Credenciales incorrectas. Intente de nuevo.')
            
    return render_template('login.html')

@app.route('/principal')
def principal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('principal.html', nombre=session['nombre'])

@app.route('/buscador')
def buscador():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('buscador.html')

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    data = request.get_json()
    codigo_buscar = data.get('codigo', '').strip()
    
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo_buscar,)).fetchone()
    conn.close()
    
    if producto:
        return jsonify({
            'encontrado': True,
            'codigo': producto['codigo'],
            'nombre': producto['nombre'],
            'descripcion': producto['descripcion'],
            'precio': producto['precio'],
            'stock': producto['stock'],
            'categoria': producto['categoria']
        })
    else:
        return jsonify({'encontrado': False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
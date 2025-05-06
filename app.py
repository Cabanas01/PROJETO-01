import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import logging
# Corrigir o import para refletir a estrutura atual
# Substituir ou remover se o módulo não for necessário
# from routes.api import api_blueprint

app = Flask(__name__, 
    static_folder='assets',
    template_folder='.')

CORS(app)

logging.basicConfig(level=logging.INFO)
DATABASE = os.path.join(os.path.dirname(__file__), 'database.sqlite')

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nome TEXT NOT NULL,
                    Email TEXT NOT NULL UNIQUE,
                    Senha TEXT NOT NULL
                )
            ''')
            conn.commit()
            logging.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin/login.html')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/dashboard.html')
def admin_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Nome, Telefone, Email, CPF, CNH, RENAVAM, Placa FROM Clientes')
        clientes = cursor.fetchall()
        conn.close()
        return render_template('admin/dashboard.html', clientes=clientes)
    except Exception as e:
        logging.error(f"Erro ao carregar dados para o dashboard: {e}")
        return render_template('admin/dashboard.html', clientes=[])

@app.route('/cliente/login.html')
def cliente_login():
    return render_template('cliente/login.html')

@app.route('/cliente/dashboard.html')
def cliente_dashboard():
    return render_template('cliente/dashboard.html')

@app.route('/cliente/cliente - dashboard.html')
def cliente_dashboard_completo():
    return render_template('cliente/cliente - dashboard.html')

@app.route('/cliente/cadastro.html')
def cliente_cadastro():
    return render_template('cliente/cadastro.html')

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory('uploads', filename, as_attachment=True)
    except Exception as e:
        return str(e), 404

@app.route('/view/<filename>')
def view_file(filename):
    try:
        return send_from_directory('uploads', filename)
    except Exception as e:
        return str(e), 404

import sqlite3

@app.route("/admin/dashboard.html")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")  # Ajuste para sua tabela real
    clientes = cursor.fetchall()
    conn.close()
    return render_template("admin/dashboard.html", clientes=clientes)

# app.register_blueprint(api_blueprint, url_prefix='/api')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import logging

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
    return render_template('admin/dashboard.html')

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

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, Nome, Email FROM Usuarios')
            usuarios = [dict(row) for row in cursor.fetchall()]
            return jsonify({"usuarios": usuarios})
    except Exception as e:
        logging.error(f"Erro ao buscar usuários: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    try:
        data = request.get_json()
        required_fields = ['Nome', 'Email', 'Senha']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Usuarios (Nome, Email, Senha) VALUES (?, ?, ?)',
                (data['Nome'], data['Email'], data['Senha'])
            )
            conn.commit()
            return jsonify({"message": "Usuário criado com sucesso"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email já cadastrado"}), 400
    except Exception as e:
        logging.error(f"Erro ao criar usuário: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/andamentos/cliente/<cpf>', methods=['GET'])
def get_andamentos_cliente(cpf):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Primeiro verifica se o cliente existe
            cursor.execute('SELECT id FROM Clientes WHERE cpf = ?', (cpf,))
            cliente = cursor.fetchone()
            
            if not cliente:
                return jsonify({"error": "Cliente não encontrado"}), 404
            cursor.execute('''
                SELECT 
                    a.id,
                    a.processo_numero,
                    a.descricao,
                    a.prazo,
                    a.sobre,
                    a.status,
                    c.nome as cliente_nome,
                    c.cpf as cliente_cpf
                FROM Andamentos a
                JOIN Clientes c ON a.cliente_id = c.id
                WHERE c.cpf = ?
            ''', (cpf,))
            andamentos = [dict(row) for row in cursor.fetchall()]
            return jsonify({"andamentos": andamentos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nome, cpf FROM Clientes')
            clientes = [dict(row) for row in cursor.fetchall()]
            return jsonify({"clientes": clientes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/meus-processos/<cpf>', methods=['GET'])
def get_meus_processos(cpf):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    a.processo_numero,
                    a.descricao,
                    a.prazo,
                    a.sobre,
                    a.status,
                    c.nome as nome_cliente
                FROM Andamentos a
                JOIN Clientes c ON a.cliente_id = c.id
                WHERE c.cpf = ?
            ''', (cpf,))
            processos = [dict(row) for row in cursor.fetchall()]
            return jsonify({"processos": processos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/andamentos/all', methods=['GET'])
def get_all_andamentos():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    a.*,
                    c.nome as cliente_nome
                FROM Andamentos a
                LEFT JOIN Clientes c ON a.cliente_id = c.id
                ORDER BY a.data DESC
            ''')
            andamentos = [dict(row) for row in cursor.fetchall()]
            return jsonify({"andamentos": andamentos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/andamentos', methods=['POST'])
def create_andamento():
    try:
        data = request.get_json()
        print("Dados recebidos:", data)  # Debug
        
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Primeiro busca o cliente pelo CPF
            cursor.execute('SELECT id FROM Clientes WHERE cpf = ?', (data['cpf'],))
            cliente = cursor.fetchone()
            
            if not cliente:
                # Tentar inserir o cliente se não existir
                cursor.execute('''
                    INSERT INTO Clientes (cpf, nome)
                    VALUES (?, ?)
                ''', (data['cpf'], 'Cliente ' + data['cpf']))
                conn.commit()
                cliente_id = cursor.lastrowid
            else:
                cliente_id = cliente['id']
                
            # Insere o andamento com o ID do cliente
            cursor.execute('''
                INSERT INTO Andamentos (
                    processo_numero, descricao, prazo, sobre, status, cliente_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['processo_numero'],
                data['descricao'],
                data['prazo'],
                data['sobre'],
                'Em andamento',  # Status padrão
                cliente_id
            ))
            conn.commit()
            return jsonify({"message": "Andamento criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
import sys
import os
import sqlite3
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask import request, jsonify
from flask import session
app = Flask(__name__,
    static_folder='assets',
    template_folder='.')

CORS(app)

logging.basicConfig(level=logging.INFO)
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", None)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", None)


def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route('/cadastro', methods=['POST'])
def cadastrar_cliente():
    try:
        data = request.get_json()
        name = data.get('nome')
        cpf = data.get('cpf')
        email = data.get('email')
        senha = data.get('senha')

        if not name or not cpf or not email or not senha:
            return jsonify({'error': 'Nome, CPF, Email e Senha são obrigatórios.'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO Client (name, cpf, email) VALUES (?, ?, ?)', (name, cpf, email))
        conn.commit()

        return jsonify({'success': True, 'message': 'Cliente cadastrado com sucesso!'}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({'error': 'CPF ou email já cadastrado.'}), 400
    except Exception as e:
        logging.error(f'Erro ao cadastrar cliente: {e}')
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/login_cliente', methods=['POST'])
def login_cliente():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')

        if not email or not senha:
            return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Client WHERE email = ?', (email,))
        cliente = cursor.fetchone()
        conn.close()

        if not cliente:
            return jsonify({'error': 'Usuário não encontrado.'}), 404

        session['cliente_id'] = cliente['id']
        session['tipo'] = 'cliente'

        return jsonify({'success': True, 'message': 'Login realizado com sucesso!'}), 200
    except Exception as e:
        logging.error(f'Erro ao fazer login do cliente: {e}')
        return jsonify({'error': 'Erro interno do servidor.'}), 500

@app.route('/login_admin', methods=['POST'])
def login_admin():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')

        if not email or not senha:
            return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

        if email == ADMIN_EMAIL and senha == ADMIN_PASSWORD:
            session['tipo'] = 'admin'
            return jsonify({'success': True, 'message': 'Login realizado com sucesso!'}), 200
        else:
            return jsonify({'error': 'Credenciais inválidas.'}), 401
    except Exception as e:
        logging.error(f'Erro ao fazer login do administrador: {e}')
        return jsonify({'error': 'Erro interno do servidor.'}), 500

@app.route('/cliente/dados', methods=['GET'])
def dados_cliente():
    try:
        if 'cliente_id' in session and session['tipo'] == 'cliente':
            cliente_id = session['cliente_id']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Client WHERE id = ?', (cliente_id,))
            cliente = cursor.fetchone()
            conn.close()

            if not cliente:
                return jsonify({'error': 'Cliente não encontrado.'}), 404

            return jsonify({'success': True, 'data': dict(cliente)}), 200
        else:
            return jsonify({'error': 'Não autorizado.'}), 403
    except Exception as e:
        logging.error(f'Erro ao obter dados do cliente: {e}')
        return jsonify({'error': 'Erro interno do servidor.'}), 500

@app.route('/admin/dados', methods=['GET'])
def dados_admin():
    try:
        if session['tipo'] == 'admin':
            return jsonify({'success': True, 'message': 'Admin autorizado.'}), 200
        else:
            return jsonify({'error': 'Não autorizado.'}), 403
    except Exception as e:
        logging.error(f'Erro ao obter dados do administrador: {e}')
        return jsonify({'error': 'Erro interno do servidor.'}), 500

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Client (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    cpf TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Process (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_cpf TEXT NOT NULL,
                    sobre TEXT,
                    process_number TEXT NOT NULL UNIQUE,
                    prazo DATE,
                    result TEXT,
                    status TEXT DEFAULT 'Em Andamento',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_cpf) REFERENCES Client(cpf)
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ProcessUpdate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_id INTEGER,
                    update_text TEXT NOT NULL,
                    observation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (process_id) REFERENCES Process(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Expense (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    description TEXT,
                    value REAL NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Payment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_id INTEGER,
                    value REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    FOREIGN KEY (process_id) REFERENCES Process(id)
                )
            ''')
           conn.commit()
            logging.info("Tabela Processo atualizado")
        except Exception as e:
            logging.error(f"Erro ao inicializar tabela Processo: {e}")
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Document (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES Client(id)
        )
    ''')
        conn.commit()
        logging.info("Tabela Documento atualizada")
    except Exception as e:
        logging.error(f"Erro ao inicializar tabela Documento: {e}")

@app.route('/api/login-admin', methods=['POST'])
def api_admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios.'}), 400
        
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Erro ao fazer login.'}), 401
    
    except Exception as e:
        logging.error(f"Erro ao processar login: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500

@app.route('/api/clientes', methods=['GET', 'POST'])
def api_clientes():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()

    try:
        if request.method == 'GET':
            cursor.execute('SELECT * FROM Client')
            clientes = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': clientes})

        elif request.method == 'POST':
            data = request.get_json()
            name = data.get('nome')
            cpf = data.get('cpf')
            email = data.get('email')
            phone = data.get('telefone')
            address = data.get('endereco')

            if not name or not cpf:
                return jsonify({'error': 'Nome e CPF são obrigatórios.'}), 400

            cursor.execute('INSERT INTO Client (name, cpf, email, phone, address) VALUES (?, ?, ?, ?, ?)',
                           (name, cpf, email, phone, address))
            conn.commit()
            return jsonify({'success': True, 'message': 'Cliente adicionado com sucesso!'}), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'CPF ou E-mail já cadastrado.'}), 400
    except Exception as e:
        logging.error(f"Erro ao processar clientes: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/clientes/<int:id>', methods=['PUT', 'DELETE'])
def api_cliente_id(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()
    
    try:
        if request.method == 'PUT':
            data = request.get_json()
            name = data.get('nome')
            cpf = data.get('cpf')
            email = data.get('email')
            phone = data.get('telefone')
            address = data.get('endereco')

            if not name or not cpf:
                return jsonify({'error': 'Nome e CPF são obrigatórios.'}), 400
            
            cursor.execute('UPDATE Client SET name = ?, cpf = ?, email = ?, phone = ?, address = ? WHERE id = ?',
                       (name, cpf, email, phone, address, id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Cliente atualizado com sucesso!'})

        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM Client WHERE id = ?', (id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Cliente removido com sucesso!'})

    except Exception as e:
        logging.error(f"Erro ao processar cliente com ID {id}: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/andamentos', methods=['GET', 'POST'])
def api_andamentos():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()

    try:
        if request.method == 'GET':
            cursor.execute('''
                SELECT p.id, c.name as nome, p.process_number as processo_numero, p.status, p.created_at
                 FROM Process p
                JOIN Client c ON p.client_cpf = c.cpf
            ''')
            andamentos = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': andamentos})

        elif request.method == 'POST':
            data = request.get_json()
            cpf = data.get('cpf')
            processo_numero = data.get('processo_numero')
            prazo = data.get('prazo')
            sobre = data.get('sobre')
            result = data.get('result')
            descricao = data.get('descricao')
            status = data.get('status')            

            if not cpf or not processo_numero:
                return jsonify({'error': 'CPF e Número do Processo são obrigatórios.'}), 400

            cursor.execute('INSERT INTO Process (client_cpf, process_number, prazo, sobre, status) VALUES (?, ?, ?, ?, ?)',
                           (cpf, processo_numero, prazo, sobre, status))
            conn.commit()
            return jsonify({'success': True, 'message': 'Andamento adicionado com sucesso!'}), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'Número de Processo já cadastrado.'}), 400
    except Exception as e:
        logging.error(f"Erro ao processar andamentos: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/andamentos/<int:id>', methods=['PUT', 'DELETE'])
def api_andamento_id(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()

    try:
        if request.method == 'PUT':
            data = request.get_json()
            cpf = data.get('cpf')
            processo_numero = data.get('processo_numero')
            prazo = data.get('prazo')
            sobre = data.get('sobre')
            result = data.get('result')

            if not cpf or not processo_numero:
                return jsonify({'error': 'CPF e Número do Processo são obrigatórios.'}), 400
            
            cursor.execute('UPDATE Process SET client_cpf = ?, process_number = ?, prazo = ?, sobre = ?, status = ? WHERE id = ?',
                           (cpf, processo_numero, prazo, sobre, status, id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Andamento atualizado com sucesso!'})

        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM Process WHERE id = ?', (id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Andamento removido com sucesso!'})

    except Exception as e:
        logging.error(f"Erro ao processar andamento com ID {id}: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/andamentos/<int:id>/finalizar', methods=['PUT'])
def api_andamento_finalizar(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Process SET status = ? WHERE id = ?', ('Finalizado', id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Andamento finalizado com sucesso!'})
    except Exception as e:
        logging.error(f"Erro ao finalizar andamento com ID {id}: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/finalizados', methods=['GET'])
def api_finalizados():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT p.id, c.name as nome_cliente, p.process_number as numero_processo, p.status
             FROM Process p
             JOIN Client c ON p.client_cpf = c.cpf
            WHERE p.status = 'Finalizado'
        ''')
        finalizados = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'data': finalizados})

    except Exception as e:
        logging.error(f"Erro ao carregar processos finalizados: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/finalizados/<int:id>/valor', methods=['POST'])
def api_finalizado_valor(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()
    try:
        data = request.get_json()
        valor = data.get('valor')
        if not valor:
            return jsonify({'error': 'Valor é obrigatório.'}), 400
        cursor.execute('INSERT INTO Payment (process_id, value, payment_date) VALUES (?, ?, DATE(\'now\'))', (id, valor))
        conn.commit()
        return jsonify({'success': True, 'message': 'Valor adicionado com sucesso!'})
    except Exception as e:
        logging.error(f"Erro ao adicionar valor ao processo finalizado com ID {id}: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/financeiro/dados', methods=['GET'])
def api_financeiro_dados():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM Expense')
        expenses = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'data': expenses})
    except Exception as e:
        logging.error(f"Erro ao carregar dados financeiros: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/financeiro/gastos', methods=['POST'])
def api_financeiro_gastos():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados.'}), 500
    cursor = conn.cursor()
    try:
        data = request.get_json()
        date = data.get('data')
        description = data.get('descricao')
        value = data.get('valor')
        if not date or not value:
            return jsonify({'error': 'Data e Valor são obrigatórios.'}), 400
        cursor.execute('INSERT INTO Expense (date, description, value) VALUES (?, ?, ?)', (date, description, value))
        conn.commit()
        return jsonify({'success': True, 'message': 'Gasto adicionado com sucesso!'})
    except Exception as e:
        logging.error(f"Erro ao adicionar gasto: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500
    finally:
        conn.close()

@app.route('/api/financeiro/valores-semana', methods=['GET'])
def api_financeiro_valores_semana():
    return jsonify({'success': True, 'data': [{"teste": "1"}]})

@app.route('/api/financeiro/valores-mes', methods=['GET'])
def api_financeiro_valores_mes():
    return jsonify({'success': True, 'data': [{"teste": "2"}]})

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
        if conn:
            cursor = conn.cursor()
            clientes = cursor.execute('SELECT * FROM Client').fetchall()
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

@app.route('/cliente/cadastro.html')
def cliente_cadastro():
    return render_template('cliente/cadastro.html')

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory('uploads', filename, as_attachment=True)
    except:
        return "", 404

@app.route('/view/<filename>')
def view_file(filename):
    try:
        return send_from_directory('uploads', filename)
    except:
        return "", 404


# app.register_blueprint(api_blueprint, url_prefix='/api')

if __name__ == '__main__':
    init_db()
    #Testando as rotas GET
    with app.test_request_context():
        # Testando /api/clientes
        with app.test_client() as client:
            response = client.get('/api/clientes')
            logging.info(f"Teste /api/clientes: {response.get_json()}")
        
        # Testando /api/andamentos
        with app.test_client() as client:
            response = client.get('/api/andamentos')
            logging.info(f"Teste /api/andamentos: {response.get_json()}")

        # Testando /api/finalizados
        with app.test_client() as client:
            response = client.get('/api/finalizados')
            logging.info(f"Teste /api/finalizados: {response.get_json()}")

        # Testando /api/financeiro/dados
        with app.test_client() as client:
            response = client.get('/api/financeiro/dados')
            logging.info(f"Teste /api/financeiro/dados: {response.get_json()}")

        # Testando /api/financeiro/valores-semana
        with app.test_client() as client:
            response = client.get('/api/financeiro/valores-semana')
            logging.info(f"Teste /api/financeiro/valores-semana: {response.get_json()}")
        
        # Testando /api/financeiro/valores-mes
        with app.test_client() as client:
            response = client.get('/api/financeiro/valores-mes')
            logging.info(f"Teste /api/financeiro/valores-mes: {response.get_json()}")

    app.run(host='0.0.0.0', port=5002, debug=True)
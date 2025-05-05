import sqlite3
import os

def init_db():
    DATABASE = os.path.join(os.path.dirname(__file__), 'database.sqlite')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Tabela de Usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Email TEXT NOT NULL UNIQUE,
                Senha TEXT NOT NULL,
                TipoUsuario TEXT NOT NULL
            )
        ''')

        # Tabela de Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                cpf TEXT UNIQUE,
                rg TEXT,
                cnh TEXT,
                renavam TEXT,
                placa TEXT,
                endereco TEXT,
                arquivos TEXT
            )
        ''')

        # Tabela de Processos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_processo TEXT UNIQUE,
                cliente_id INTEGER,
                status TEXT,
                descricao TEXT,
                prazo DATE,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES Clientes (id)
            )
        ''')

        # Tabela de Andamentos
        cursor.execute('''
            DROP TABLE IF EXISTS Andamentos;
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Andamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_numero TEXT NOT NULL,
                descricao TEXT,
                data DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                prazo TEXT,
                sobre TEXT,
                cliente_id INTEGER NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES Clientes (id)
            )
        ''')

        # Tabela de Arquivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Arquivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT,
                caminho TEXT NOT NULL,
                cliente_id INTEGER,
                processo_id INTEGER,
                data_upload DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES Clientes (id),
                FOREIGN KEY (processo_id) REFERENCES Processos (id)
            )
        ''')

        # Tabela de Notificações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                mensagem TEXT NOT NULL,
                lida BOOLEAN DEFAULT 0,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES Usuarios (id)
            )
        ''')

        conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
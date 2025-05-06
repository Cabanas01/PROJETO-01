const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err);
    } else {
        console.log('Conectado ao banco SQLite');
    }
});

const initializeDatabase = () => {
    db.serialize(() => {
        // Criar tabelas necessárias
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )`);
    });
};

// Function to get andamentos by clienteId
function getAndamentosByClienteId(clienteId) {
    return new Promise((resolve, reject) => {
        const query = `
            SELECT a.id, a.processo_numero, a.descricao, a.data, a.status, a.prazo, a.sobre,
                   c.nome AS cliente_nome
            FROM Andamentos a
            LEFT JOIN Clientes c ON a.cliente_id = c.id
            WHERE c.id = ?
            ORDER BY a.data DESC;
        `;
        db.all(query, [clienteId], (err, rows) => {
            if (err) {
                reject(err);
            } else {
                resolve(rows);
            }
        });
    });
}

module.exports = {
    db,
    initializeDatabase,
    getAndamentosByClienteId
};
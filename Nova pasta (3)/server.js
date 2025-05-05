const express = require('express');
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Inicialização do banco de dados
(async () => {
  const db = await open({
    filename: './database.db',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL
    )
  `);

  console.log('Banco de dados pronto 🚀');

  // Rotas de exemplo
  app.get('/users', async (req, res) => {
    const users = await db.all('SELECT * FROM users');
    res.json(users);
  });

  app.post('/users', async (req, res) => {
    const { name } = req.body;
    const result = await db.run('INSERT INTO users (name) VALUES (?)', [name]);
    res.json({ id: result.lastID, name });
  });

  // Iniciar o servidor só depois que o banco estiver pronto
  app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
  });
})();

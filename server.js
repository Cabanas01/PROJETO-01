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

  // Rota para cadastro de cliente
  app.post('/clientes', async (req, res) => {
    const { nome, telefone, email, cpf, endereco } = req.body;
    try {
      const result = await db.run(
        'INSERT INTO Clientes (nome, telefone, email, cpf, endereco) VALUES (?, ?, ?, ?, ?)',
        [nome, telefone, email, cpf, endereco]
      );
      res.status(201).json({ id: result.lastID, nome, telefone, email, cpf, endereco });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao cadastrar cliente.' });
    }
  });

  // Rota para atualizar perfil do cliente
  app.put('/clientes/:id', async (req, res) => {
    const { id } = req.params;
    const { nome, telefone, email, endereco } = req.body;
    try {
      await db.run(
        'UPDATE Clientes SET nome = ?, telefone = ?, email = ?, endereco = ? WHERE id = ?',
        [nome, telefone, email, endereco, id]
      );
      res.status(200).json({ message: 'Perfil atualizado com sucesso.' });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao atualizar perfil.' });
    }
  });

  // Rota para upload de arquivos
  app.post('/clientes/:id/arquivos', async (req, res) => {
    const { id } = req.params;
    const { nome, tipo, caminho } = req.body; // Supondo que o upload já foi tratado
    try {
      const result = await db.run(
        'INSERT INTO Arquivos (nome, tipo, caminho, cliente_id) VALUES (?, ?, ?, ?)',
        [nome, tipo, caminho, id]
      );
      res.status(201).json({ id: result.lastID, nome, tipo, caminho });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao enviar arquivo.' });
    }
  });

  // Rota para cadastrar andamento de processo
  app.post('/processos/andamentos', async (req, res) => {
    const { processo_numero, descricao, status, prazo, sobre, cliente_id } = req.body;
    try {
      const result = await db.run(
        'INSERT INTO Andamentos (processo_numero, descricao, status, prazo, sobre, cliente_id) VALUES (?, ?, ?, ?, ?, ?)',
        [processo_numero, descricao, status, prazo, sobre, cliente_id]
      );
      res.status(201).json({ id: result.lastID, processo_numero, descricao, status, prazo, sobre, cliente_id });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao cadastrar andamento do processo.' });
    }
  });

  // Rota para marcar processo como finalizado
  app.put('/processos/:id/finalizar', async (req, res) => {
    const { id } = req.params;
    try {
      await db.run('UPDATE Processos SET status = ? WHERE id = ?', ['FINALIZADO', id]);
      res.status(200).json({ message: 'Processo finalizado com sucesso.' });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao finalizar processo.' });
    }
  });

  // Rota para adicionar gasto
  app.post('/financeiro/gastos', async (req, res) => {
    const { descricao, valor, data } = req.body;
    try {
      const result = await db.run(
        'INSERT INTO Gastos (descricao, valor, data) VALUES (?, ?, ?)',
        [descricao, valor, data]
      );
      res.status(201).json({ id: result.lastID, descricao, valor, data });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao adicionar gasto.' });
    }
  });

  // Rota para registrar pagamento
  app.post('/financeiro/pagamentos', async (req, res) => {
    const { cliente_id, valor, data } = req.body;
    try {
      const result = await db.run(
        'INSERT INTO Pagamentos (cliente_id, valor, data) VALUES (?, ?, ?)',
        [cliente_id, valor, data]
      );
      res.status(201).json({ id: result.lastID, cliente_id, valor, data });
    } catch (error) {
      res.status(500).json({ error: 'Erro ao registrar pagamento.' });
    }
  });

  // Iniciar o servidor só depois que o banco estiver pronto
  app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
  });
})();

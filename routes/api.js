const express = require('express');
const { 
  getAllItems, 
  getItemById, 
  createItem, 
  updateItem, 
  deleteItem,
  getAndamentosByClienteId,
  getClienteByCPF,
  addAndamento,
  getProcessosByClienteId,
  getFinalizados,
  addValorPago
} = require('../db');

const router = express.Router();

// Get all items
router.get('/items', async (req, res, next) => {
  try {
    const items = await getAllItems();
    res.json({ success: true, data: items });
  } catch (err) {
    next(err);
  }
});

// Get a single item
router.get('/items/:id', async (req, res, next) => {
  try {
    const id = parseInt(req.params.id);
    const item = await getItemById(id);
    
    if (!item) {
      return res.status(404).json({ 
        success: false, 
        message: 'Item not found' 
      });
    }
    
    res.json({ success: true, data: item });
  } catch (err) {
    next(err);
  }
});

// Create a new item
router.post('/items', async (req, res, next) => {
  try {
    const { name, description, category } = req.body;
    
    // Basic validation
    if (!name || name.trim() === '') {
      return res.status(400).json({ 
        success: false, 
        message: 'Name is required' 
      });
    }
    
    const newItem = await createItem({ name, description, category });
    res.status(201).json({ success: true, data: newItem });
  } catch (err) {
    next(err);
  }
});

// Update an item
router.put('/items/:id', async (req, res, next) => {
  try {
    const id = parseInt(req.params.id);
    const { name, description, category } = req.body;
    
    // Basic validation
    if (!name || name.trim() === '') {
      return res.status(400).json({ 
        success: false, 
        message: 'Name is required' 
      });
    }
    
    const updatedItem = await updateItem(id, { name, description, category });
    res.json({ success: true, data: updatedItem });
  } catch (err) {
    if (err.message === 'Item not found') {
      return res.status(404).json({ 
        success: false, 
        message: 'Item not found' 
      });
    }
    next(err);
  }
});

// Delete an item
router.delete('/items/:id', async (req, res, next) => {
  try {
    const id = parseInt(req.params.id);
    await deleteItem(id);
    res.json({ success: true, message: 'Item deleted successfully' });
  } catch (err) {
    if (err.message === 'Item not found') {
      return res.status(404).json({ 
        success: false, 
        message: 'Item not found' 
      });
    }
    next(err);
  }
});

// Rota para obter os andamentos de um cliente
router.get('/dashboard/andamentos/:clienteId', async (req, res, next) => {
  try {
    const clienteId = parseInt(req.params.clienteId);
    const andamentos = await getAndamentosByClienteId(clienteId);

    if (!andamentos || andamentos.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Nenhum andamento encontrado para este cliente.'
      });
    }

    res.json({ success: true, data: andamentos });
  } catch (err) {
    next(err);
  }
});

// Rota para adicionar um andamento
router.post('/andamentos', async (req, res, next) => {
  try {
    const { cpf, numero_processo, descricao, prazo, status, sobre } = req.body;

    // Verificar se o cliente existe
    const cliente = await getClienteByCPF(cpf);
    if (!cliente) {
      return res.status(404).json({ success: false, message: 'Cliente não encontrado.' });
    }

    // Adicionar o andamento ao banco de dados
    const novoAndamento = await addAndamento({
      cliente_id: cliente.id,
      processo_numero: numero_processo,
      descricao,
      prazo,
      status,
      sobre
    });

    res.status(201).json({ success: true, data: novoAndamento });
  } catch (err) {
    next(err);
  }
});

// Rota para obter os processos de um cliente por CPF
router.get('/meus-processos/:cpf', async (req, res, next) => {
  try {
    const { cpf } = req.params;

    // Verificar se o cliente existe
    const cliente = await getClienteByCPF(cpf);
    if (!cliente) {
      return res.status(404).json({ success: false, message: 'Cliente não encontrado.' });
    }

    // Obter os processos vinculados ao cliente
    const processos = await getProcessosByClienteId(cliente.id);

    res.json({ success: true, data: processos });
  } catch (err) {
    next(err);
  }
});

// Rota para cadastrar um cliente
router.post('/clientes', async (req, res, next) => {
  try {
    const { nome, telefone, email, cpf, rg, cnh, renavam, placa, endereco } = req.body;

    // Verificar se o cliente já existe
    const clienteExistente = await getClienteByCPF(cpf);
    if (clienteExistente) {
      return res.status(400).json({ success: false, message: 'Cliente já cadastrado.' });
    }

    // Cadastrar o cliente
    const novoCliente = await addCliente({
      nome,
      telefone,
      email,
      cpf,
      rg,
      cnh,
      renavam,
      placa,
      endereco
    });

    res.status(201).json({ success: true, data: novoCliente });
  } catch (err) {
    next(err);
  }
});

// Rota para editar os dados de um cliente
router.put('/clientes/:cpf', async (req, res, next) => {
  try {
    const { cpf } = req.params;
    const { nome, telefone, email, rg, cnh, renavam, placa, endereco } = req.body;

    // Verificar se o cliente existe
    const cliente = await getClienteByCPF(cpf);
    if (!cliente) {
      return res.status(404).json({ success: false, message: 'Cliente não encontrado.' });
    }

    // Atualizar os dados do cliente
    const clienteAtualizado = await updateCliente(cpf, {
      nome,
      telefone,
      email,
      rg,
      cnh,
      renavam,
      placa,
      endereco
    });

    res.json({ success: true, data: clienteAtualizado });
  } catch (err) {
    next(err);
  }
});

// Rota para upload de arquivos
router.post('/clientes/:cpf/arquivos', async (req, res, next) => {
  try {
    const { cpf } = req.params;
    const arquivos = req.files; // Supondo que o middleware de upload esteja configurado

    // Verificar se o cliente existe
    const cliente = await getClienteByCPF(cpf);
    if (!cliente) {
      return res.status(404).json({ success: false, message: 'Cliente não encontrado.' });
    }

    // Salvar os arquivos no banco de dados
    const arquivosSalvos = await saveArquivos(cliente.id, arquivos);

    res.status(201).json({ success: true, data: arquivosSalvos });
  } catch (err) {
    next(err);
  }
});

// Rota para listar processos finalizados
router.get('/finalizados', async (req, res, next) => {
  try {
    const finalizados = await getFinalizados();
    res.json({ success: true, data: finalizados });
  } catch (err) {
    next(err);
  }
});

// Rota para adicionar valor pago por um cliente
router.post('/finalizados/:id/valor', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { valor } = req.body;

    const atualizado = await addValorPago(id, valor);
    if (!atualizado) {
      return res.status(404).json({ success: false, message: 'Processo não encontrado.' });
    }

    res.json({ success: true, message: 'Valor adicionado com sucesso.' });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
const express = require('express');
const { 
  getAllItems, 
  getItemById, 
  createItem, 
  updateItem, 
  deleteItem 
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

module.exports = router;
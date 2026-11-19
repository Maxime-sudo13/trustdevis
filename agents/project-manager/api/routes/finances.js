const express = require('express');
const router = express.Router();
const { FinanceService, ProjectService } = require('../../services');

// GET /api/finances/project/:projectId - Transactions d'un projet
router.get('/project/:projectId', async (req, res) => {
  try {
    const transactions = await FinanceService.findByProject(req.params.projectId);
    res.json({ success: true, data: transactions });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/finances/project/:projectId/summary - Résumé financier
router.get('/project/:projectId/summary', async (req, res) => {
  try {
    const summary = await FinanceService.getSummary(req.params.projectId);
    const remaining = await FinanceService.getRemainingToPay(req.params.projectId);
    
    res.json({ 
      success: true, 
      data: { ...summary, remaining_to_pay: remaining }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/finances/project/:projectId/deposits - Acomptes
router.get('/project/:projectId/deposits', async (req, res) => {
  try {
    const deposits = await FinanceService.getDeposits(req.params.projectId);
    res.json({ success: true, data: deposits });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/finances - Créer une transaction
router.post('/', async (req, res) => {
  try {
    const required = ['project_id', 'type', 'amount'];
    const missing = required.filter(field => !req.body[field]);
    
    if (missing.length > 0) {
      return res.status(400).json({ 
        success: false, 
        error: `Champs requis manquants: ${missing.join(', ')}` 
      });
    }

    const transaction = await FinanceService.create(req.body);
    
    // Mettre à jour le budget dépensé si c'est une dépense
    if (req.body.type === 'expense') {
      await ProjectService.updateBudgetSpent(req.body.project_id, req.body.amount);
    }
    
    res.status(201).json({ success: true, data: transaction });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// DELETE /api/finances/:id - Supprimer une transaction
router.delete('/:id', async (req, res) => {
  try {
    const result = await FinanceService.delete(req.params.id);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

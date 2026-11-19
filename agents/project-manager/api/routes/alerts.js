const express = require('express');
const router = express.Router();
const { AlertService } = require('../../services');

// GET /api/alerts - Toutes les alertes actives
router.get('/', async (req, res) => {
  try {
    const alerts = await AlertService.findAllActive();
    res.json({ success: true, data: alerts });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/alerts/project/:projectId - Alertes d'un projet
router.get('/project/:projectId', async (req, res) => {
  try {
    const options = {
      unreadOnly: req.query.unread === 'true',
      unresolvedOnly: req.query.unresolved === 'true'
    };
    
    const alerts = await AlertService.findByProject(req.params.projectId, options);
    res.json({ success: true, data: alerts });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// PUT /api/alerts/:id/read - Marquer comme lue
router.put('/:id/read', async (req, res) => {
  try {
    const result = await AlertService.markAsRead(req.params.id);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// PUT /api/alerts/:id/resolve - Résoudre une alerte
router.put('/:id/resolve', async (req, res) => {
  try {
    const result = await AlertService.resolve(req.params.id);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

const express = require('express');
const router = express.Router();
const { ProjectStepService } = require('../../services');

// GET /api/steps/project/:projectId - Étapes d'un projet
router.get('/project/:projectId', async (req, res) => {
  try {
    const steps = await ProjectStepService.findByProject(req.params.projectId);
    res.json({ success: true, data: steps });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/steps/:id - Détails d'une étape
router.get('/:id', async (req, res) => {
  try {
    const step = await ProjectStepService.findById(req.params.id);
    if (!step) {
      return res.status(404).json({ success: false, error: 'Étape non trouvée' });
    }
    res.json({ success: true, data: step });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/steps - Créer une étape
router.post('/', async (req, res) => {
  try {
    const required = ['project_id', 'name'];
    const missing = required.filter(field => !req.body[field]);
    
    if (missing.length > 0) {
      return res.status(400).json({ 
        success: false, 
        error: `Champs requis manquants: ${missing.join(', ')}` 
      });
    }

    const step = await ProjectStepService.create(req.body);
    res.status(201).json({ success: true, data: step });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// PUT /api/steps/:id - Mettre à jour une étape
router.put('/:id', async (req, res) => {
  try {
    const step = await ProjectStepService.update(req.params.id, req.body);
    res.json({ success: true, data: step });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/steps/:id/start - Démarrer une étape
router.post('/:id/start', async (req, res) => {
  try {
    const step = await ProjectStepService.startStep(req.params.id);
    res.json({ success: true, data: step });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/steps/:id/complete - Terminer une étape
router.post('/:id/complete', async (req, res) => {
  try {
    const step = await ProjectStepService.completeStep(req.params.id);
    res.json({ success: true, data: step });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/steps/:id/validate - Valider une étape (client)
router.post('/:id/validate', async (req, res) => {
  try {
    const step = await ProjectStepService.validateStep(req.params.id);
    res.json({ success: true, data: step });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// DELETE /api/steps/:id - Supprimer une étape
router.delete('/:id', async (req, res) => {
  try {
    const result = await ProjectStepService.delete(req.params.id);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

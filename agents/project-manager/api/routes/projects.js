const express = require('express');
const router = express.Router();
const { ProjectService } = require('../../services');
const { AlertChecker } = require('../../utils');

// GET /api/projects - Liste tous les projets
router.get('/', async (req, res) => {
  try {
    const filters = {};
    if (req.query.status) filters.status = req.query.status;
    if (req.query.client_id) filters.client_id = req.query.client_id;
    
    const projects = await ProjectService.findAll(filters);
    res.json({ success: true, data: projects });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/projects - Créer un projet
router.post('/', async (req, res) => {
  try {
    const required = ['name', 'address', 'work_type', 'budget_total'];
    const missing = required.filter(field => !req.body[field]);
    
    if (missing.length > 0) {
      return res.status(400).json({ 
        success: false, 
        error: `Champs requis manquants: ${missing.join(', ')}` 
      });
    }

    const project = await ProjectService.create(req.body);
    res.status(201).json({ success: true, data: project });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/projects/:id - Détails d'un projet
router.get('/:id', async (req, res) => {
  try {
    const project = await ProjectService.findById(req.params.id);
    if (!project) {
      return res.status(404).json({ success: false, error: 'Projet non trouvé' });
    }
    
    // Récupérer les artisans associés
    const artisans = await ProjectService.getArtisans(req.params.id);
    
    res.json({ 
      success: true, 
      data: { ...project, artisans } 
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// PUT /api/projects/:id - Mettre à jour un projet
router.put('/:id', async (req, res) => {
  try {
    const project = await ProjectService.update(req.params.id, req.body);
    res.json({ success: true, data: project });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// DELETE /api/projects/:id - Supprimer un projet
router.delete('/:id', async (req, res) => {
  try {
    const result = await ProjectService.delete(req.params.id);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/projects/:id/artisans - Ajouter un artisan
router.post('/:id/artisans', async (req, res) => {
  try {
    const { artisan_id, role } = req.body;
    if (!artisan_id) {
      return res.status(400).json({ success: false, error: 'artisan_id requis' });
    }
    
    const result = await ProjectService.addArtisan(req.params.id, artisan_id, role);
    res.status(201).json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// PUT /api/projects/:id/status - Changer le statut
router.put('/:id/status', async (req, res) => {
  try {
    const { status } = req.body;
    if (!status) {
      return res.status(400).json({ success: false, error: 'status requis' });
    }
    
    const project = await ProjectService.updateStatus(req.params.id, status);
    res.json({ success: true, data: project });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/projects/:id/check-alerts - Vérifier les alertes
router.post('/:id/check-alerts', async (req, res) => {
  try {
    const project = await ProjectService.findById(req.params.id);
    if (!project) {
      return res.status(404).json({ success: false, error: 'Projet non trouvé' });
    }
    
    await AlertChecker.checkProjectAlerts(project);
    res.json({ success: true, message: 'Alertes vérifiées' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

const express = require('express');
const router = express.Router();
const path = require('path');
const { DocumentService } = require('../../services');
const { upload } = require('../../utils');

// GET /api/documents/project/:projectId - Documents d'un projet
router.get('/project/:projectId', async (req, res) => {
  try {
    const options = {};
    if (req.query.type) options.type = req.query.type;
    
    const documents = await DocumentService.findByProject(req.params.projectId, options);
    res.json({ success: true, data: documents });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/documents/:id - Détails d'un document
router.get('/:id', async (req, res) => {
  try {
    const document = await DocumentService.findById(req.params.id);
    if (!document) {
      return res.status(404).json({ success: false, error: 'Document non trouvé' });
    }
    res.json({ success: true, data: document });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/documents/upload - Upload un document
router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, error: 'Aucun fichier fourni' });
    }

    const { project_id, type, artisan_id } = req.body;
    if (!project_id || !type) {
      return res.status(400).json({ 
        success: false, 
        error: 'project_id et type sont requis' 
      });
    }

    const document = await DocumentService.create({
      project_id,
      type,
      filename: req.file.filename,
      original_name: req.file.originalname,
      path: req.file.path,
      artisan_id
    });

    res.status(201).json({ 
      success: true, 
      data: document,
      file: {
        filename: req.file.filename,
        size: req.file.size,
        mimetype: req.file.mimetype
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/documents/project/:projectId/required - Vérifier documents requis
router.get('/project/:projectId/required', async (req, res) => {
  try {
    const check = await DocumentService.checkRequiredDocuments(req.params.projectId);
    res.json({ success: true, data: check });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/documents/project/:projectId/dossier - Générer dossier final
router.get('/project/:projectId/dossier', async (req, res) => {
  try {
    const dossier = await DocumentService.generateFinalDossier(req.params.projectId);
    res.json({ success: true, data: dossier });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// DELETE /api/documents/:id - Supprimer un document
router.delete('/:id', async (req, res) => {
  try {
    const result = await DocumentService.delete(req.params.id);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

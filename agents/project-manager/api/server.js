const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const { initDatabase } = require('../database/connection');
const projectRoutes = require('./routes/projects');
const stepRoutes = require('./routes/steps');
const financeRoutes = require('./routes/finances');
const documentRoutes = require('./routes/documents');
const alertRoutes = require('./routes/alerts');
const dashboardRoutes = require('./routes/dashboard');

const app = express();
const PORT = process.env.PORT || 3003;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir les fichiers statiques (uploads)
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Routes
app.use('/api/projects', projectRoutes);
app.use('/api/steps', stepRoutes);
app.use('/api/finances', financeRoutes);
app.use('/api/documents', documentRoutes);
app.use('/api/alerts', alertRoutes);
app.use('/api/dashboard', dashboardRoutes);

// Route de santé
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'project-manager', timestamp: new Date().toISOString() });
});

// Route racine
app.get('/', (req, res) => {
  res.json({
    service: 'TrustDevis Project Manager API',
    version: '1.0.0',
    endpoints: {
      projects: '/api/projects',
      steps: '/api/steps',
      finances: '/api/finances',
      documents: '/api/documents',
      alerts: '/api/alerts',
      dashboard: '/api/dashboard'
    }
  });
});

// Gestion des erreurs
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: err.message || 'Une erreur est survenue' });
});

// Initialisation et démarrage
async function startServer() {
  try {
    // Initialiser la base de données
    initDatabase();
    console.log('Base de données initialisée');

    // Démarrer le serveur
    app.listen(PORT, () => {
      console.log(`🚀 Project Manager API démarré sur le port ${PORT}`);
    });
  } catch (error) {
    console.error('Erreur démarrage serveur:', error);
    process.exit(1);
  }
}

startServer();

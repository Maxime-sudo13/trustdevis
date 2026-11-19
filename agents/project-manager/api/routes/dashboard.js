const express = require('express');
const router = express.Router();
const { DashboardService } = require('../../services');

// GET /api/dashboard - Dashboard global
router.get('/', async (req, res) => {
  try {
    const dashboard = await DashboardService.getGlobalDashboard();
    res.json({ success: true, data: dashboard });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/dashboard/project/:projectId - Dashboard d'un projet
router.get('/project/:projectId', async (req, res) => {
  try {
    const dashboard = await DashboardService.getProjectDashboard(req.params.projectId);
    res.json({ success: true, data: dashboard });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/dashboard/calendar - Calendrier des projets
router.get('/calendar', async (req, res) => {
  try {
    const { start, end } = req.query;
    const calendar = await DashboardService.getCalendar(start, end);
    res.json({ success: true, data: calendar });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/dashboard/attention - Projets nécessitant attention
router.get('/attention', async (req, res) => {
  try {
    const attention = await DashboardService.getProjectsNeedingAttention();
    res.json({ success: true, data: attention });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

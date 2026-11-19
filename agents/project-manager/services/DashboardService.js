const ProjectService = require('./ProjectService');
const ProjectStepService = require('./ProjectStepService');
const AlertService = require('./AlertService');
const FinanceService = require('./FinanceService');
const DocumentService = require('./DocumentService');

class DashboardService {
  constructor() {
    this.projectService = ProjectService;
    this.stepService = ProjectStepService;
    this.alertService = AlertService;
    this.financeService = FinanceService;
    this.documentService = DocumentService;
  }

  // Dashboard global
  async getGlobalDashboard() {
    const projects = await this.projectService.findAll();
    const alerts = await this.alertService.findAllActive();

    const statusCounts = projects.reduce((acc, project) => {
      acc[project.status] = (acc[project.status] || 0) + 1;
      return acc;
    }, {});

    const totalBudget = projects.reduce((sum, p) => sum + p.budget_total, 0);
    const totalSpent = projects.reduce((sum, p) => sum + p.budget_spent, 0);

    return {
      summary: {
        total_projects: projects.length,
        projects_by_status: statusCounts,
        total_budget: totalBudget,
        total_spent: totalSpent,
        budget_usage_percent: totalBudget > 0 ? (totalSpent / totalBudget * 100).toFixed(2) : 0,
        active_alerts: alerts.length
      },
      recent_projects: projects.slice(0, 5),
      active_alerts: alerts.slice(0, 10)
    };
  }

  // Dashboard d'un projet spécifique
  async getProjectDashboard(projectId) {
    const [project, steps, finances, documents, alerts] = await Promise.all([
      this.projectService.findById(projectId),
      this.stepService.findByProject(projectId),
      this.financeService.getSummary(projectId),
      this.documentService.findByProject(projectId),
      this.alertService.findByProject(projectId, { unresolvedOnly: true })
    ]);

    if (!project) {
      throw new Error('Projet non trouvé');
    }

    const completedSteps = steps.filter(s => s.status === 'completed').length;
    const progressPercent = steps.length > 0 ? (completedSteps / steps.length * 100).toFixed(1) : 0;

    return {
      project,
      progress: {
        total_steps: steps.length,
        completed_steps: completedSteps,
        progress_percent: progressPercent,
        current_step: steps.find(s => s.status === 'in_progress') || null
      },
      finances,
      documents_count: documents.length,
      documents_by_type: documents.reduce((acc, doc) => {
        acc[doc.type] = (acc[doc.type] || 0) + 1;
        return acc;
      }, {}),
      alerts
    };
  }

  // Calendrier des projets
  async getCalendar(startDate, endDate) {
    const projects = await this.projectService.findAll();
    
    const events = [];
    
    projects.forEach(project => {
      // Date de début prévue
      if (project.start_date) {
        events.push({
          type: 'project_start',
          date: project.start_date,
          project_id: project.id,
          project_name: project.name,
          title: `Début: ${project.name}`
        });
      }

      // Date de fin prévue
      if (project.end_date) {
        events.push({
          type: 'project_end',
          date: project.end_date,
          project_id: project.id,
          project_name: project.name,
          title: `Fin: ${project.name}`
        });
      }
    });

    // Récupérer les étapes pour plus de détails
    for (const project of projects) {
      const steps = await this.stepService.findByProject(project.id);
      steps.forEach(step => {
        if (step.planned_start_date) {
          events.push({
            type: 'step_start',
            date: step.planned_start_date,
            project_id: project.id,
            project_name: project.name,
            step_id: step.id,
            step_name: step.name,
            title: `${project.name} - ${step.name}`
          });
        }
      });
    }

    // Filtrer par date si spécifié
    let filteredEvents = events;
    if (startDate) {
      filteredEvents = filteredEvents.filter(e => e.date >= startDate);
    }
    if (endDate) {
      filteredEvents = filteredEvents.filter(e => e.date <= endDate);
    }

    return filteredEvents.sort((a, b) => new Date(a.date) - new Date(b.date));
  }

  // Projets nécessitant attention
  async getProjectsNeedingAttention() {
    const projects = await this.projectService.findAll();
    const attentionNeeded = [];

    for (const project of projects) {
      const needsAttention = {
        project_id: project.id,
        project_name: project.name,
        issues: []
      };

      if (project.is_over_budget) {
        needsAttention.issues.push({
          type: 'budget',
          severity: 'critical',
          message: `Budget dépassé de ${(project.budget_usage_percent - 100).toFixed(1)}%`
        });
      } else if (project.budget_usage_percent >= 90) {
        needsAttention.issues.push({
          type: 'budget',
          severity: 'warning',
          message: `Budget à ${project.budget_usage_percent.toFixed(1)}%`
        });
      }

      if (project.is_delayed) {
        needsAttention.issues.push({
          type: 'delay',
          severity: 'critical',
          message: 'Projet en retard'
        });
      }

      const steps = await this.stepService.findByProject(project.id);
      const delayedSteps = steps.filter(s => s.is_delayed);
      if (delayedSteps.length > 0) {
        needsAttention.issues.push({
          type: 'step_delay',
          severity: 'warning',
          message: `${delayedSteps.length} étape(s) en retard`
        });
      }

      if (needsAttention.issues.length > 0) {
        attentionNeeded.push(needsAttention);
      }
    }

    return attentionNeeded;
  }
}

module.exports = new DashboardService();

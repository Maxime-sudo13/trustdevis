const { initDatabase } = require('../database/connection');
const { 
  ProjectService, 
  ProjectStepService, 
  AlertService,
  FinanceService,
  DocumentService,
  DashboardService 
} = require('../services');

class AlertChecker {
  constructor() {
    this.projectService = ProjectService;
    this.stepService = ProjectStepService;
    this.alertService = AlertService;
    this.financeService = FinanceService;
  }

  // Vérifier toutes les alertes
  async checkAllAlerts() {
    console.log('Vérification des alertes...');
    const projects = await this.projectService.findAll();
    
    for (const project of projects) {
      await this.checkProjectAlerts(project);
    }
    
    console.log('Vérification des alertes terminée');
  }

  // Vérifier les alertes d'un projet
  async checkProjectAlerts(project) {
    await Promise.all([
      this.checkBudgetAlerts(project),
      this.checkDelayAlerts(project)
    ]);
  }

  // Vérifier les alertes de budget
  async checkBudgetAlerts(project) {
    const threshold = parseInt(process.env.BUDGET_ALERT_THRESHOLD) || 90;
    const usagePercent = project.budget_usage_percent;

    if (usagePercent >= 100) {
      // Vérifier si une alerte existe déjà
      const alerts = await this.alertService.findByProject(project.id);
      const existingAlert = alerts.find(a => a.type === 'budget_exceeded');
      
      if (!existingAlert) {
        await this.alertService.createBudgetAlert(project.id, usagePercent, threshold);
        console.log(`Alerte budget dépassé créée pour le projet ${project.name}`);
      }
    } else if (usagePercent >= threshold) {
      const alerts = await this.alertService.findByProject(project.id);
      const existingAlert = alerts.find(a => a.type === 'budget_warning');
      
      if (!existingAlert) {
        await this.alertService.createBudgetAlert(project.id, usagePercent, threshold);
        console.log(`Alerte budget warning créée pour le projet ${project.name}`);
      }
    }
  }

  // Vérifier les alertes de retard
  async checkDelayAlerts(project) {
    const delayThreshold = parseInt(process.env.DELAY_ALERT_DAYS) || 3;
    const steps = await this.stepService.findByProject(project.id);
    
    for (const step of steps) {
      if (step.is_delayed && step.planned_end_date) {
        const today = new Date();
        const plannedEnd = new Date(step.planned_end_date);
        const daysDelayed = Math.ceil((today - plannedEnd) / (1000 * 60 * 60 * 24));

        if (daysDelayed >= delayThreshold) {
          const alerts = await this.alertService.findByProject(project.id);
          const existingAlert = alerts.find(a => 
            a.type.includes('delay') && a.message.includes(step.name)
          );

          if (!existingAlert) {
            await this.alertService.createDelayAlert(project.id, step.name, daysDelayed);
            console.log(`Alerte retard créée pour l'étape ${step.name}`);
          }
        }
      }
    }
  }
}

module.exports = new AlertChecker();

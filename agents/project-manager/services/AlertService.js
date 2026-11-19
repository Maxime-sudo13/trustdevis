const { getDatabase } = require('../database/connection');
const { v4: uuidv4 } = require('uuid');
const { ProjectAlert } = require('../models');

class AlertService {
  constructor() {
    this.db = getDatabase();
  }

  // Créer une alerte
  async create(alertData) {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const { project_id, type, severity, message } = alertData;

      const sql = `
        INSERT INTO project_alerts (id, project_id, type, severity, message)
        VALUES (?, ?, ?, ?, ?)
      `;

      this.db.run(sql, [id, project_id, type, severity, message], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...alertData });
        }
      });
    });
  }

  // Récupérer les alertes d'un projet
  async findByProject(projectId, options = {}) {
    return new Promise((resolve, reject) => {
      let sql = 'SELECT * FROM project_alerts WHERE project_id = ?';
      const params = [projectId];

      if (options.unreadOnly) {
        sql += ' AND is_read = 0';
      }

      if (options.unresolvedOnly) {
        sql += ' AND resolved_at IS NULL';
      }

      sql += ' ORDER BY created_at DESC';

      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => new ProjectAlert(row).toJSON()));
        }
      });
    });
  }

  // Récupérer toutes les alertes actives
  async findAllActive() {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT a.*, p.name as project_name 
        FROM project_alerts a
        JOIN projects p ON a.project_id = p.id
        WHERE a.resolved_at IS NULL
        ORDER BY a.created_at DESC
      `;

      this.db.all(sql, [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Marquer une alerte comme lue
  async markAsRead(id) {
    return new Promise((resolve, reject) => {
      const sql = 'UPDATE project_alerts SET is_read = 1 WHERE id = ?';
      
      this.db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ updated: this.changes > 0 });
        }
      });
    });
  }

  // Résoudre une alerte
  async resolve(id) {
    return new Promise((resolve, reject) => {
      const sql = 'UPDATE project_alerts SET resolved_at = CURRENT_TIMESTAMP WHERE id = ?';
      
      this.db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ updated: this.changes > 0 });
        }
      });
    });
  }

  // Créer une alerte de dépassement budget
  async createBudgetAlert(projectId, currentPercent, threshold) {
    const severity = currentPercent >= 100 ? 'critical' : 'warning';
    const message = currentPercent >= 100 
      ? `Budget dépassé ! Utilisation: ${currentPercent.toFixed(1)}%`
      : `Budget presque épuisé. Utilisation: ${currentPercent.toFixed(1)}%`;

    return this.create({
      project_id: projectId,
      type: currentPercent >= 100 ? ProjectAlert.TYPES.BUDGET_EXCEEDED : ProjectAlert.TYPES.BUDGET_WARNING,
      severity,
      message
    });
  }

  // Créer une alerte de retard
  async createDelayAlert(projectId, stepName, daysDelayed) {
    return this.create({
      project_id: projectId,
      type: daysDelayed > 7 ? ProjectAlert.TYPES.DELAY_EXCEEDED : ProjectAlert.TYPES.DELAY_WARNING,
      severity: daysDelayed > 7 ? 'critical' : 'warning',
      message: `Retard sur l'étape "${stepName}" : ${daysDelayed} jour(s)`
    });
  }

  // Supprimer les alertes d'un projet
  async deleteByProject(projectId) {
    return new Promise((resolve, reject) => {
      const sql = 'DELETE FROM project_alerts WHERE project_id = ?';
      
      this.db.run(sql, [projectId], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ deleted: this.changes });
        }
      });
    });
  }
}

module.exports = new AlertService();

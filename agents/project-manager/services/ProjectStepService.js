const { getDatabase } = require('../database/connection');
const { v4: uuidv4 } = require('uuid');
const { ProjectStep } = require('../models');

class ProjectStepService {
  constructor() {
    this.db = getDatabase();
  }

  // Créer une étape
  async create(stepData) {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const {
        project_id, name, description, planned_start_date, planned_end_date, order_index
      } = stepData;

      const sql = `
        INSERT INTO project_steps (id, project_id, name, description, planned_start_date, planned_end_date, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;

      this.db.run(sql, [id, project_id, name, description, planned_start_date, planned_end_date, order_index || 0], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...stepData });
        }
      });
    });
  }

  // Récupérer les étapes d'un projet
  async findByProject(projectId) {
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM project_steps WHERE project_id = ? ORDER BY order_index ASC';
      
      this.db.all(sql, [projectId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => new ProjectStep(row).toJSON()));
        }
      });
    });
  }

  // Récupérer une étape par ID
  async findById(id) {
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM project_steps WHERE id = ?';
      
      this.db.get(sql, [id], (err, row) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          resolve(new ProjectStep(row).toJSON());
        }
      });
    });
  }

  // Mettre à jour une étape
  async update(id, updates) {
    return new Promise((resolve, reject) => {
      const fields = [];
      const values = [];

      Object.keys(updates).forEach(key => {
        if (key !== 'id') {
          fields.push(`${key} = ?`);
          values.push(updates[key]);
        }
      });

      values.push(id);
      const sql = `UPDATE project_steps SET ${fields.join(', ')} WHERE id = ?`;

      this.db.run(sql, values, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...updates });
        }
      });
    });
  }

  // Démarrer une étape
  async startStep(id) {
    const updates = {
      status: 'in_progress',
      actual_start_date: new Date().toISOString().split('T')[0]
    };
    return this.update(id, updates);
  }

  // Terminer une étape
  async completeStep(id) {
    const updates = {
      status: 'completed',
      actual_end_date: new Date().toISOString().split('T')[0]
    };
    return this.update(id, updates);
  }

  // Valider une étape par le client
  async validateStep(id) {
    const updates = {
      client_validated: true,
      validated_at: new Date().toISOString()
    };
    return this.update(id, updates);
  }

  // Supprimer une étape
  async delete(id) {
    return new Promise((resolve, reject) => {
      const sql = 'DELETE FROM project_steps WHERE id = ?';
      
      this.db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ deleted: this.changes > 0 });
        }
      });
    });
  }

  // Récupérer les étapes en retard
  async getDelayedSteps(projectId) {
    const steps = await this.findByProject(projectId);
    return steps.filter(step => step.is_delayed);
  }
}

module.exports = new ProjectStepService();

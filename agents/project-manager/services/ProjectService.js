const { getDatabase } = require('../database/connection');
const { v4: uuidv4 } = require('uuid');
const { Project } = require('../models');

class ProjectService {
  constructor() {
    this.db = getDatabase();
  }

  // Créer un projet
  async create(projectData) {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const {
        name, address, work_type, budget_total, start_date, end_date,
        client_id, description
      } = projectData;

      const sql = `
        INSERT INTO projects (id, name, address, work_type, budget_total, start_date, end_date, client_id, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `;

      this.db.run(sql, [id, name, address, work_type, budget_total, start_date, end_date, client_id, description], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...projectData });
        }
      });
    });
  }

  // Récupérer tous les projets
  async findAll(filters = {}) {
    return new Promise((resolve, reject) => {
      let sql = 'SELECT * FROM projects';
      const params = [];

      if (filters.status) {
        sql += ' WHERE status = ?';
        params.push(filters.status);
      }

      if (filters.client_id) {
        sql += params.length ? ' AND' : ' WHERE';
        sql += ' client_id = ?';
        params.push(filters.client_id);
      }

      sql += ' ORDER BY created_at DESC';

      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => new Project(row).toJSON()));
        }
      });
    });
  }

  // Récupérer un projet par ID
  async findById(id) {
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM projects WHERE id = ?';
      
      this.db.get(sql, [id], (err, row) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          resolve(new Project(row).toJSON());
        }
      });
    });
  }

  // Mettre à jour un projet
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

      fields.push('updated_at = CURRENT_TIMESTAMP');
      values.push(id);

      const sql = `UPDATE projects SET ${fields.join(', ')} WHERE id = ?`;

      this.db.run(sql, values, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...updates });
        }
      });
    });
  }

  // Supprimer un projet
  async delete(id) {
    return new Promise((resolve, reject) => {
      const sql = 'DELETE FROM projects WHERE id = ?';
      
      this.db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ deleted: this.changes > 0 });
        }
      });
    });
  }

  // Ajouter un artisan au projet
  async addArtisan(projectId, artisanId, role = null) {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const sql = `
        INSERT INTO project_artisans (id, project_id, artisan_id, role)
        VALUES (?, ?, ?, ?)
      `;

      this.db.run(sql, [id, projectId, artisanId, role], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, project_id: projectId, artisan_id: artisanId, role });
        }
      });
    });
  }

  // Récupérer les artisans d'un projet
  async getArtisans(projectId) {
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM project_artisans WHERE project_id = ?';
      
      this.db.all(sql, [projectId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Mettre à jour le budget dépensé
  async updateBudgetSpent(projectId, amount) {
    return new Promise((resolve, reject) => {
      const sql = `
        UPDATE projects 
        SET budget_spent = budget_spent + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `;

      this.db.run(sql, [amount, projectId], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ updated: this.changes > 0 });
        }
      });
    });
  }

  // Changer le statut du projet
  async updateStatus(projectId, status) {
    const updates = { status };
    
    if (status === 'in_progress') {
      updates.actual_start_date = new Date().toISOString().split('T')[0];
    } else if (status === 'completed') {
      updates.actual_end_date = new Date().toISOString().split('T')[0];
    }

    return this.update(projectId, updates);
  }
}

module.exports = new ProjectService();

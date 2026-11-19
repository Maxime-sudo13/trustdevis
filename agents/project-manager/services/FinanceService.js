const { getDatabase } = require('../database/connection');
const { v4: uuidv4 } = require('uuid');
const { ProjectFinance } = require('../models');

class FinanceService {
  constructor() {
    this.db = getDatabase();
  }

  // Créer une transaction
  async create(transactionData) {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const {
        project_id, type, amount, description, date, artisan_id, document_id
      } = transactionData;

      const sql = `
        INSERT INTO project_finances (id, project_id, type, amount, description, date, artisan_id, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `;

      this.db.run(sql, [id, project_id, type, amount, description, date || new Date().toISOString().split('T')[0], artisan_id, document_id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...transactionData });
        }
      });
    });
  }

  // Récupérer les transactions d'un projet
  async findByProject(projectId) {
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM project_finances WHERE project_id = ? ORDER BY date DESC';
      
      this.db.all(sql, [projectId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => new ProjectFinance(row).toJSON()));
        }
      });
    });
  }

  // Récupérer un résumé financier
  async getSummary(projectId) {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT 
          SUM(CASE WHEN type IN ('deposit', 'progress_payment', 'final_payment') THEN amount ELSE 0 END) as total_income,
          SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expenses,
          SUM(CASE WHEN type = 'estimate' THEN amount ELSE 0 END) as total_estimates
        FROM project_finances
        WHERE project_id = ?
      `;

      this.db.get(sql, [projectId], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve({
            total_income: row.total_income || 0,
            total_expenses: row.total_expenses || 0,
            total_estimates: row.total_estimates || 0,
            balance: (row.total_income || 0) - (row.total_expenses || 0)
          });
        }
      });
    });
  }

  // Récupérer les acomptes versés
  async getDeposits(projectId) {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT * FROM project_finances 
        WHERE project_id = ? AND type = 'deposit'
        ORDER BY date DESC
      `;
      
      this.db.all(sql, [projectId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => new ProjectFinance(row).toJSON()));
        }
      });
    });
  }

  // Calculer le reste à payer
  async getRemainingToPay(projectId) {
    const summary = await this.getSummary(projectId);
    return summary.total_estimates - summary.total_income;
  }

  // Supprimer une transaction
  async delete(id) {
    return new Promise((resolve, reject) => {
      const sql = 'DELETE FROM project_finances WHERE id = ?';
      
      this.db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ deleted: this.changes > 0 });
        }
      });
    });
  }
}

module.exports = new FinanceService();

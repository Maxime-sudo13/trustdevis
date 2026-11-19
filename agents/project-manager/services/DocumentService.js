const { getDatabase } = require('../database/connection');
const { v4: uuidv4 } = require('uuid');
const { ProjectDocument } = require('../models');

class DocumentService {
  constructor() {
    this.db = getDatabase();
  }

  // Créer un document
  async create(documentData) {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const {
        project_id, type, filename, original_name, path, artisan_id
      } = documentData;

      const sql = `
        INSERT INTO project_documents (id, project_id, type, filename, original_name, path, artisan_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;

      this.db.run(sql, [id, project_id, type, filename, original_name, path, artisan_id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, ...documentData });
        }
      });
    });
  }

  // Récupérer les documents d'un projet
  async findByProject(projectId, options = {}) {
    return new Promise((resolve, reject) => {
      let sql = 'SELECT * FROM project_documents WHERE project_id = ?';
      const params = [projectId];

      if (options.type) {
        sql += ' AND type = ?';
        params.push(options.type);
      }

      sql += ' ORDER BY uploaded_at DESC';

      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => new ProjectDocument(row).toJSON()));
        }
      });
    });
  }

  // Récupérer un document par ID
  async findById(id) {
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM project_documents WHERE id = ?';
      
      this.db.get(sql, [id], (err, row) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          resolve(new ProjectDocument(row).toJSON());
        }
      });
    });
  }

  // Récupérer les documents par type
  async findByType(projectId, type) {
    return this.findByProject(projectId, { type });
  }

  // Vérifier si tous les documents requis sont présents
  async checkRequiredDocuments(projectId) {
    const requiredTypes = ['contract', 'insurance'];
    const documents = await this.findByProject(projectId);
    
    const presentTypes = documents.map(doc => doc.type);
    const missingTypes = requiredTypes.filter(type => !presentTypes.includes(type));

    return {
      complete: missingTypes.length === 0,
      missing: missingTypes,
      present: presentTypes
    };
  }

  // Supprimer un document
  async delete(id) {
    return new Promise((resolve, reject) => {
      const sql = 'DELETE FROM project_documents WHERE id = ?';
      
      this.db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ deleted: this.changes > 0 });
        }
      });
    });
  }

  // Générer le dossier final
  async generateFinalDossier(projectId) {
    const documents = await this.findByProject(projectId);
    const requiredCheck = await this.checkRequiredDocuments(projectId);

    return {
      project_id: projectId,
      is_complete: requiredCheck.complete,
      missing_documents: requiredCheck.missing,
      documents_count: documents.length,
      documents_by_type: documents.reduce((acc, doc) => {
        acc[doc.type] = (acc[doc.type] || 0) + 1;
        return acc;
      }, {}),
      generated_at: new Date().toISOString()
    };
  }
}

module.exports = new DocumentService();

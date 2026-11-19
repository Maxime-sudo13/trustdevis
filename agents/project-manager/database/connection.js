const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = process.env.DATABASE_URL || path.join(__dirname, 'project_manager.db');

let db = null;

function getDatabase() {
  if (!db) {
    db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('Erreur connexion base de données:', err);
      } else {
        console.log('Connecté à la base de données SQLite');
      }
    });
  }
  return db;
}

function initDatabase() {
  const database = getDatabase();
  
  database.serialize(() => {
    // Table des projets
    database.run(`
      CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        work_type TEXT NOT NULL,
        budget_total REAL NOT NULL,
        budget_spent REAL DEFAULT 0,
        start_date DATE,
        end_date DATE,
        actual_start_date DATE,
        actual_end_date DATE,
        status TEXT DEFAULT 'planning',
        client_id TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Table des artisans sur un projet
    database.run(`
      CREATE TABLE IF NOT EXISTS project_artisans (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        artisan_id TEXT NOT NULL,
        role TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      )
    `);

    // Table des étapes de chantier
    database.run(`
      CREATE TABLE IF NOT EXISTS project_steps (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        planned_start_date DATE,
        planned_end_date DATE,
        actual_start_date DATE,
        actual_end_date DATE,
        client_validated BOOLEAN DEFAULT 0,
        validated_at DATETIME,
        order_index INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      )
    `);

    // Table des photos
    database.run(`
      CREATE TABLE IF NOT EXISTS project_photos (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        step_id TEXT,
        filename TEXT NOT NULL,
        original_name TEXT,
        path TEXT NOT NULL,
        description TEXT,
        taken_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (step_id) REFERENCES project_steps(id) ON DELETE SET NULL
      )
    `);

    // Table des transactions financières
    database.run(`
      CREATE TABLE IF NOT EXISTS project_finances (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date DATE DEFAULT CURRENT_DATE,
        artisan_id TEXT,
        document_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      )
    `);

    // Table des documents
    database.run(`
      CREATE TABLE IF NOT EXISTS project_documents (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        type TEXT NOT NULL,
        filename TEXT NOT NULL,
        original_name TEXT,
        path TEXT NOT NULL,
        artisan_id TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      )
    `);

    // Table des alertes
    database.run(`
      CREATE TABLE IF NOT EXISTS project_alerts (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        type TEXT NOT NULL,
        severity TEXT DEFAULT 'info',
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      )
    `);

    // Table des devis
    database.run(`
      CREATE TABLE IF NOT EXISTS project_estimates (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        artisan_id TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        valid_until DATE,
        accepted_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      )
    `);
  });

  console.log('Base de données initialisée avec succès');
  return database;
}

function closeDatabase() {
  if (db) {
    db.close((err) => {
      if (err) {
        console.error('Erreur fermeture base de données:', err);
      } else {
        console.log('Base de données fermée');
      }
    });
    db = null;
  }
}

module.exports = {
  getDatabase,
  initDatabase,
  closeDatabase
};

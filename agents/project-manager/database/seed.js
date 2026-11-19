const { v4: uuidv4 } = require('uuid');
const { getDatabase } = require('./connection');

function seed() {
  console.log('Seeding de la base de données...');
  const db = getDatabase();

  const sampleProjects = [
    {
      id: uuidv4(),
      name: 'Rénovation cuisine M. Dupont',
      address: '12 Rue de la Paix, 75002 Paris',
      work_type: 'rénovation',
      budget_total: 25000,
      budget_spent: 5000,
      start_date: '2025-04-01',
      end_date: '2025-05-15',
      status: 'planning',
      description: 'Rénovation complète cuisine avec électroménager'
    },
    {
      id: uuidv4(),
      name: 'Extension maison Mme Martin',
      address: '45 Avenue des Champs, 75008 Paris',
      work_type: 'extension',
      budget_total: 85000,
      budget_spent: 15000,
      start_date: '2025-03-15',
      end_date: '2025-08-30',
      status: 'in_progress',
      description: 'Extension de 30m2 avec terrasse'
    }
  ];

  const sampleSteps = [
    { name: 'Planning', description: 'Étude et planification du chantier' },
    { name: 'Démolition', description: 'Démontage des éléments existants' },
    { name: 'Gros œuvre', description: 'Travaux structurels' },
    { name: 'Second œuvre', description: 'Finitions et aménagements' },
    { name: 'Livraison', description: 'Réception et validation finale' }
  ];

  db.serialize(() => {
    // Insérer les projets
    const projectStmt = db.prepare(`
      INSERT OR IGNORE INTO projects 
      (id, name, address, work_type, budget_total, budget_spent, start_date, end_date, status, description)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    sampleProjects.forEach(project => {
      projectStmt.run([
        project.id,
        project.name,
        project.address,
        project.work_type,
        project.budget_total,
        project.budget_spent,
        project.start_date,
        project.end_date,
        project.status,
        project.description
      ]);
    });
    projectStmt.finalize();

    // Insérer les étapes pour chaque projet
    const stepStmt = db.prepare(`
      INSERT OR IGNORE INTO project_steps 
      (id, project_id, name, description, order_index)
      VALUES (?, ?, ?, ?, ?)
    `);

    sampleProjects.forEach(project => {
      sampleSteps.forEach((step, index) => {
        stepStmt.run([uuidv4(), project.id, step.name, step.description, index]);
      });
    });
    stepStmt.finalize();

    console.log('Seeding terminé');
  });

  setTimeout(() => process.exit(0), 1000);
}

seed();

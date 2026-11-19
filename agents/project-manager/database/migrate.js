const { initDatabase } = require('./connection');

function migrate() {
  console.log('Migration de la base de données...');
  initDatabase();
  console.log('Migration terminée');
  process.exit(0);
}

migrate();

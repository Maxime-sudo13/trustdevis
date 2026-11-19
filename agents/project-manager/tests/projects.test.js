const request = require('supertest');
const express = require('express');

// Mock de la base de données
jest.mock('../database/connection', () => ({
  getDatabase: jest.fn(() => ({})),
  initDatabase: jest.fn()
}));

// Mock des services
jest.mock('../services/ProjectService', () => ({
  findAll: jest.fn(),
  findById: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
  addArtisan: jest.fn(),
  updateStatus: jest.fn(),
  getArtisans: jest.fn()
}));

const ProjectService = require('../services/ProjectService');

describe('Project API', () => {
  let app;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    app.use('/api/projects', require('../api/routes/projects'));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /api/projects', () => {
    it('should return all projects', async () => {
      const mockProjects = [
        { id: '1', name: 'Projet 1', status: 'planning' },
        { id: '2', name: 'Projet 2', status: 'in_progress' }
      ];
      ProjectService.findAll.mockResolvedValue(mockProjects);

      const response = await request(app)
        .get('/api/projects')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toEqual(mockProjects);
    });
  });

  describe('POST /api/projects', () => {
    it('should create a new project', async () => {
      const newProject = {
        name: 'Nouveau projet',
        address: '123 Rue Test',
        work_type: 'rénovation',
        budget_total: 25000
      };
      
      ProjectService.create.mockResolvedValue({ id: '123', ...newProject });

      const response = await request(app)
        .post('/api/projects')
        .send(newProject)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe('123');
    });

    it('should return 400 if required fields are missing', async () => {
      const response = await request(app)
        .post('/api/projects')
        .send({ name: 'Test' })
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });
});

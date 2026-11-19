// mock_api.js - Simulation temps réel des données agents avec tâches

class MockAPI {
  constructor() {
    this.agents = JSON.parse(JSON.stringify(AGENTS_DATA.agents));
    this.globalStats = { ...AGENTS_DATA.globalStats };
    this.globalStats.totalAgents = this.agents.length;
    this.globalStats.startTime = Date.now();
    this.simulationInterval = null;
    this.listeners = [];
    this.activityLog = [];
    this.maxActivities = 50;
    this.recentScores = []; // Pour calculer le score moyen sur les 100 derniers
    
    // Configuration des tâches par agent
    this.agentTasks = {
      'agent-ocr': { name: 'Extraction OCR', duration: [2000, 5000], xp: 15 },
      'agent-normalizer': { name: 'Classification', duration: [1000, 3000], xp: 12 },
      'agent-pricing': { name: 'Calcul prix', duration: [1000, 2000], xp: 10 },
      'agent-marketscore': { name: 'Analyse scoring', duration: [3000, 5000], xp: 20 },
      'agent-leadfinder': { name: 'Scraping leads', duration: [5000, 10000], xp: 25 },
      'agent-crm': { name: 'Gestion client', duration: [2000, 4000], xp: 15 },
      'agent-compliance': { name: 'Vérification RGPD', duration: [1000, 2000], xp: 10 },
      'agent-billing': { name: 'Traitement paiement', duration: [2000, 3000], xp: 18 },
      'agent-ux': { name: 'Analyse conversion', duration: [4000, 6000], xp: 22 },
      'agent-bizdev': { name: 'Prospection', duration: [3000, 5000], xp: 20 },
      'agent-mobile': { name: 'Compilation app', duration: [5000, 8000], xp: 30 },
      'agent-ml': { name: 'Prédiction ML', duration: [4000, 7000], xp: 28 },
      'agent-artisans': { name: 'Matching artisans', duration: [2000, 4000], xp: 15 },
      'agent-project': { name: 'Suivi projet', duration: [3000, 5000], xp: 18 },
      'agent-quote': { name: 'Génération devis', duration: [3000, 6000], xp: 25 }
    };
    
    // Initialiser les agents avec des propriétés temps réel
    this.agents.forEach(agent => {
      agent.currentTask = null;
      agent.taskProgress = 0;
      agent.tasksCompletedToday = Math.floor(Math.random() * 50) + 10;
      agent.lastActivity = Date.now() - Math.floor(Math.random() * 3600000);
      agent.isProcessing = false;
    });
    
    // Initialiser les scores récents
    for (let i = 0; i < 50; i++) {
      this.recentScores.push(Math.floor(Math.random() * 20) + 80);
    }
    this.updateAvgScore();
  }

  // Démarrer la simulation temps réel
  startSimulation(intervalMs = 500) {
    if (this.simulationInterval) return;
    
    this.simulationInterval = setInterval(() => {
      this.simulateRealtimeActivity();
    }, intervalMs);
    
    console.log('🎮 Simulation temps réel démarrée (500ms polling)');
  }

  // Arrêter la simulation
  stopSimulation() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = null;
      console.log('⏹️ Simulation arrêtée');
    }
  }

  // Simuler l'activité temps réel
  simulateRealtimeActivity() {
    const now = Date.now();
    
    // Mettre à jour le uptime
    this.updateUptime();
    
    // Mettre à jour les agents
    this.agents.forEach(agent => {
      if (agent.status === 'offline') return;
      
      if (agent.isProcessing) {
        // Continuer la tâche en cours
        this.updateTaskProgress(agent, now);
      } else if (agent.status === 'online') {
        // Décider si l'agent commence une nouvelle tâche
        if (Math.random() < 0.15) { // 15% de chance par cycle
          this.startTask(agent);
        }
      }
    });
    
    // Mettre à jour les stats globales
    this.updateGlobalStats();
    
    // Notifier les listeners
    this.notifyListeners();
  }

  // Démarrer une tâche pour un agent
  startTask(agent) {
    const taskConfig = this.agentTasks[agent.id];
    if (!taskConfig) return;
    
    const duration = Math.floor(
      Math.random() * (taskConfig.duration[1] - taskConfig.duration[0]) + 
      taskConfig.duration[0]
    );
    
    agent.status = 'busy';
    agent.isProcessing = true;
    agent.currentTask = {
      name: taskConfig.name,
      startTime: Date.now(),
      duration: duration,
      xpReward: taskConfig.xp
    };
    agent.taskProgress = 0;
    
    // Ajouter au log d'activité
    this.addActivity('🚀', `${agent.name} a commencé ${taskConfig.name}`, 'start');
  }

  // Mettre à jour la progression d'une tâche
  updateTaskProgress(agent, now) {
    if (!agent.currentTask) return;
    
    const elapsed = now - agent.currentTask.startTime;
    const progress = Math.min((elapsed / agent.currentTask.duration) * 100, 100);
    agent.taskProgress = progress;
    
    if (progress >= 100) {
      this.completeTask(agent);
    }
  }

  // Terminer une tâche
  completeTask(agent) {
    if (!agent.currentTask) return;
    
    const task = agent.currentTask;
    const xpGained = task.xpReward + Math.floor(Math.random() * 10);
    
    // Mettre à jour l'agent
    agent.status = 'online';
    agent.isProcessing = false;
    agent.tasksCompletedToday++;
    agent.lastActivity = Date.now();
    agent.currentTask = null;
    agent.taskProgress = 0;
    
    // Mettre à jour les stats
    agent.stats.devisAnalyzed++;
    this.globalStats.totalDevis++;
    
    // Calculer un score pour ce devis
    const score = Math.floor(Math.random() * 20) + 80;
    this.recentScores.push(score);
    if (this.recentScores.length > 100) {
      this.recentScores.shift();
    }
    this.updateAvgScore();
    
    // Mettre à jour le score moyen de l'agent
    const totalScore = agent.stats.avgScore * (agent.stats.devisAnalyzed - 1) + score;
    agent.stats.avgScore = Math.round((totalScore / agent.stats.devisAnalyzed) * 10) / 10;
    
    // Ajouter XP
    this.addXP(agent.id, xpGained);
    
    // Ajouter au log d'activité
    const time = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    this.addActivity('✅', `${agent.name} a terminé ${task.name} (+${xpGained} XP)`, 'complete', time);
    
    // Vérifier les badges
    this.checkBadges(agent);
  }

  // Mettre à jour le score moyen global
  updateAvgScore() {
    const sum = this.recentScores.reduce((a, b) => a + b, 0);
    this.globalStats.avgScore = Math.round((sum / this.recentScores.length) * 10) / 10;
  }

  // Mettre à jour l'uptime
  updateUptime() {
    const elapsed = Date.now() - this.globalStats.startTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    if (hours > 0) {
      this.globalStats.uptime = `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      this.globalStats.uptime = `${minutes}m ${seconds}s`;
    } else {
      this.globalStats.uptime = `${seconds}s`;
    }
  }

  // Mettre à jour les stats globales
  updateGlobalStats() {
    this.globalStats.activeAgents = this.agents.filter(a => a.status === 'busy').length;
    this.globalStats.onlineAgents = this.agents.filter(a => a.status === 'online').length;
  }

  // Ajouter une activité au log
  addActivity(icon, text, type = 'info', time = null) {
    const activityTime = time || new Date().toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
    
    this.activityLog.unshift({
      icon,
      text,
      time: activityTime,
      type,
      timestamp: Date.now()
    });
    
    if (this.activityLog.length > this.maxActivities) {
      this.activityLog.pop();
    }
  }

  // Ajouter de l'XP
  addXP(agentId, amount) {
    const agent = this.agents.find(a => a.id === agentId);
    if (!agent) return;

    agent.xp += amount;
    this.globalStats.totalXP += amount;

    // Vérifier level up
    if (agent.xp >= agent.xpToNextLevel && agent.level < 10) {
      this.levelUp(agent);
    }

    return agent;
  }

  // Level up
  levelUp(agent) {
    agent.level++;
    agent.xp = agent.xp - agent.xpToNextLevel;
    agent.xpToNextLevel = Math.floor(agent.xpToNextLevel * 1.5);
    
    this.addActivity('🎉', `${agent.name} est passé niveau ${agent.level}!`, 'levelup');
    
    // Badge légendaire au niveau 10
    if (agent.level === 10) {
      this.addBadge(agent, 'legend');
    }

    return agent;
  }

  // Ajouter un badge
  addBadge(agent, badgeId) {
    if (!agent.badges.includes(badgeId)) {
      agent.badges.push(badgeId);
      const badge = AGENTS_DATA.badges[badgeId];
      this.addActivity('🏆', `${agent.name} a débloqué ${badge?.name || badgeId}!`, 'badge');
    }
  }

  // Vérifier les badges
  checkBadges(agent) {
    const devis = agent.stats.devisAnalyzed;
    
    if (devis >= 1) this.addBadge(agent, 'first_blood');
    if (devis >= 50) this.addBadge(agent, 'fifty_deals');
    if (devis >= 100) this.addBadge(agent, 'century');
    if (agent.stats.responseTime < 1) this.addBadge(agent, 'speed_demon');
    if (agent.stats.accuracy >= 95) this.addBadge(agent, 'precision_master');
    if (devis >= 500) this.addBadge(agent, 'data_miner');
    if (agent.stats.streak >= 7) this.addBadge(agent, 'perfect_week');
    if (agent.stats.streak >= 30) this.addBadge(agent, 'perfect_month');
    if (devis >= 1000 && agent.id === 'agent-rapport') this.addBadge(agent, 'report_god');
    if (agent.id === 'agent-amelioration' && agent.level >= 8) this.addBadge(agent, 'ml_wizard');
    if (agent.id === 'agent-securite' && agent.stats.accuracy >= 99) this.addBadge(agent, 'guardian');
  }

  // Changer le statut manuellement
  toggleStatus(agentId) {
    const agent = this.agents.find(a => a.id === agentId);
    if (!agent) return;

    const statuses = ['online', 'busy', 'offline'];
    const currentIndex = statuses.indexOf(agent.status);
    agent.status = statuses[(currentIndex + 1) % statuses.length];
    
    if (agent.status !== 'busy') {
      agent.isProcessing = false;
      agent.currentTask = null;
      agent.taskProgress = 0;
    }
    
    this.updateGlobalStats();
    this.notifyListeners();

    return agent;
  }

  // Souscrire aux mises à jour
  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  // Notifier tous les listeners
  notifyListeners() {
    this.listeners.forEach(callback => {
      callback({
        agents: this.agents,
        globalStats: this.globalStats,
        activityLog: this.activityLog
      });
    });
  }

  // Obtenir les données actuelles
  getData() {
    return {
      agents: this.agents,
      globalStats: this.globalStats,
      activityLog: this.activityLog
    };
  }

  // Obtenir le leaderboard
  getLeaderboard() {
    return [...this.agents]
      .sort((a, b) => {
        if (b.level !== a.level) return b.level - a.level;
        return b.xp - a.xp;
      })
      .map((agent, index) => ({
        rank: index + 1,
        ...agent
      }));
  }

  // Obtenir un agent par ID
  getAgent(agentId) {
    return this.agents.find(a => a.id === agentId);
  }
  
  // Obtenir le temps écoulé depuis la dernière activité
  getTimeSinceLastActivity(agent) {
    const elapsed = Date.now() - agent.lastActivity;
    const seconds = Math.floor(elapsed / 1000);
    
    if (seconds < 60) return `il y a ${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `il y a ${minutes}m`;
    const hours = Math.floor(minutes / 60);
    return `il y a ${hours}h`;
  }
}

// Créer l'instance globale
const mockAPI = new MockAPI();

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MockAPI, mockAPI };
}
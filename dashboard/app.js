// app.js - TrustDevis Command Center - Realtime Dashboard v3.0

let currentAgentId = null;

class TrustDevisDashboard {
  constructor() {
    this.api = mockAPI;
    this.init();
  }

  init() {
    this.renderGlobalStats();
    this.renderAgents();
    this.renderLeaderboard();
    this.renderActivityFeed();
    this.setupNavigation();
    this.setupWorkloadSlider();
    this.setupChat();
    this.startRealtimeUpdates();
  }

  // Setup chat widget
  setupChat() {
    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const chatClose = document.getElementById('chat-close');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatToggle) return;

    chatToggle.addEventListener('click', () => {
      chatWidget.classList.toggle('hidden');
      if (!chatWidget.classList.contains('hidden')) {
        chatInput.focus();
      }
    });

    chatClose.addEventListener('click', () => {
      chatWidget.classList.add('hidden');
    });

    const sendMessage = () => {
      const message = chatInput.value.trim();
      if (!message) return;

      // Add user message
      const userMsg = document.createElement('div');
      userMsg.className = 'chat-message user';
      userMsg.innerHTML = `<p>${this.escapeHtml(message)}</p>`;
      chatMessages.appendChild(userMsg);

      chatInput.value = '';
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // Simulate bot response
      setTimeout(() => {
        const botMsg = document.createElement('div');
        botMsg.className = 'chat-message bot';
        botMsg.innerHTML = `<p>Message reçu ! Je transmets à l'Agent Directeur. Utilise Telegram pour une réponse rapide.</p>`;
        chatMessages.appendChild(botMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }, 1000);
    };

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Setup navigation
  setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const page = btn.dataset.page;
        this.switchPage(page);
        
        navButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  // Switch page
  switchPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
      targetPage.classList.add('active');
    }
  }

  // Setup workload slider
  setupWorkloadSlider() {
    const slider = document.getElementById('workload-slider');
    const valueDisplay = document.getElementById('workload-percent');
    
    if (slider && valueDisplay) {
      slider.addEventListener('input', (e) => {
        valueDisplay.textContent = e.target.value + '%';
      });
    }
  }

  // Rendu des statistiques globales
  renderGlobalStats() {
    const stats = this.api.getData().globalStats;
    const container = document.getElementById('global-stats');
    
    if (!container) return;
    
    container.innerHTML = `
      <div class="stat-card">
        <div class="stat-icon">📋</div>
        <div class="stat-value" id="stat-devis">${stats.totalDevis.toLocaleString()}</div>
        <div class="stat-label">Devis Analysés</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-value" id="stat-score">${stats.avgScore}%</div>
        <div class="stat-label">Score Moyen (100 derniers)</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🤖</div>
        <div class="stat-value" id="stat-agents">${stats.activeAgents}/${stats.totalAgents}</div>
        <div class="stat-label">Agents Occupés</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-value" id="stat-uptime">${stats.uptime}</div>
        <div class="stat-label">Uptime</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-value" id="stat-xp">${(stats.totalXP / 1000).toFixed(1)}k</div>
        <div class="stat-label">XP Total</div>
      </div>
    `;
  }

  // Rendu des cartes agents
  renderAgents() {
    const agents = this.api.getData().agents;
    const container = document.getElementById('agents-grid');
    
    if (!container) return;
    
    container.innerHTML = agents.map(agent => this.createAgentCard(agent)).join('');
    
    // Ajouter les event listeners pour ouvrir le modal
    const agentCards = container.querySelectorAll('.agent-card');
    agentCards.forEach((card, index) => {
      card.addEventListener('click', () => {
        openAgentModal(agents[index].id);
      });
    });
  }

  // Créer une carte agent avec indicateurs temps réel
  createAgentCard(agent) {
    const xpPercent = (agent.xp / agent.xpToNextLevel) * 100;
    const statusClass = `status-${agent.status}`;
    const isBusy = agent.status === 'busy';
    const pulseClass = isBusy ? 'pulse-busy' : '';
    const timeSince = this.api.getTimeSinceLastActivity(agent);
    
    // Barre de progression de tâche
    let taskProgressHtml = '';
    if (isBusy && agent.currentTask) {
      taskProgressHtml = `
        <div class="task-progress-container">
          <div class="task-progress-bar" style="width: ${agent.taskProgress}%"></div>
          <div class="task-progress-text">${agent.currentTask.name} - ${Math.round(agent.taskProgress)}%</div>
        </div>
      `;
    }
    
    return `
      <div class="agent-card ${pulseClass}" style="--agent-color: ${agent.color}" data-agent-id="${agent.id}">
        <div class="agent-header">
          <div class="agent-avatar">
            ${agent.emoji}
            ${isBusy ? '<div class="task-indicator"></div>' : ''}
          </div>
          <div class="agent-info">
            <h3>${agent.name}</h3>
            <div class="agent-role">${agent.role}</div>
          </div>
          <div class="agent-status ${statusClass}">${agent.status}</div>
        </div>
        
        ${taskProgressHtml}
        
        <div class="agent-level">
          <span class="level-badge">LVL ${agent.level}</span>
          <span class="level-text">Niveau ${agent.level}/10</span>
        </div>
        
        <div class="xp-bar-container">
          <div class="xp-bar" style="width: ${xpPercent}%"></div>
        </div>
        <div class="xp-text">${agent.xp.toLocaleString()} / ${agent.xpToNextLevel.toLocaleString()} XP</div>
        
        <div class="agent-stats">
          <div class="agent-stat">
            <div class="agent-stat-value">${agent.stats.devisAnalyzed}</div>
            <div class="agent-stat-label">Devis</div>
          </div>
          <div class="agent-stat">
            <div class="agent-stat-value">${agent.stats.avgScore}%</div>
            <div class="agent-stat-label">Score</div>
          </div>
          <div class="agent-stat">
            <div class="agent-stat-value">${agent.tasksCompletedToday}</div>
            <div class="agent-stat-label">Aujourd'hui</div>
          </div>
          <div class="agent-stat">
            <div class="agent-stat-value">${agent.stats.responseTime}s</div>
            <div class="agent-stat-label">Réponse</div>
          </div>
        </div>
        
        <div class="agent-last-activity">
          <span class="activity-dot ${isBusy ? 'active' : ''}"></span>
          ${isBusy ? 'En cours...' : `Dernière activité: ${timeSince}`}
        </div>
        
        <div class="agent-badges">
          ${agent.badges.map(badgeId => this.createBadge(badgeId)).join('')}
        </div>
      </div>
    `;
  }

  // Créer un badge
  createBadge(badgeId) {
    const badge = AGENTS_DATA.badges[badgeId];
    if (!badge) return '';
    
    return `
      <div class="badge badge-${badge.rarity}" data-name="${badge.name}: ${badge.desc}" title="${badge.name}: ${badge.desc}">
        ${badge.icon}
      </div>
    `;
  }

  // Rendu du leaderboard
  renderLeaderboard() {
    const leaderboard = this.api.getLeaderboard();
    const container = document.getElementById('leaderboard-list');
    
    if (!container) return;
    
    container.innerHTML = leaderboard.map((agent, index) => `
      <div class="leaderboard-item">
        <div class="leaderboard-rank rank-${index + 1}">${index + 1}</div>
        <div class="agent-avatar" style="width: 40px; height: 40px; font-size: 1.25rem; background: ${agent.color}; border: 2px solid ${agent.color};">${agent.emoji}</div>
        <div class="leaderboard-name">${agent.name}</div>
        <div class="leaderboard-level">Lvl ${agent.level}</div>
        <div class="leaderboard-xp">${agent.xp.toLocaleString()} XP</div>
      </div>
    `).join('');
  }

  // Rendu du feed d'activité temps réel
  renderActivityFeed() {
    const container = document.getElementById('activity-list');
    if (!container) return;
    
    const activities = this.api.activityLog;
    
    container.innerHTML = activities.map(activity => {
      const typeClass = activity.type || 'info';
      return `
        <div class="activity-item activity-${typeClass}">
          <span class="activity-icon">${activity.icon}</span>
          <span class="activity-text">${activity.text}</span>
          <span class="activity-time">${activity.time}</span>
        </div>
      `;
    }).join('');
    
    // Auto-scroll vers le haut (les plus récents)
    container.scrollTop = 0;
  }

  // Mises à jour temps réel (polling 500ms)
  startRealtimeUpdates() {
    // Souscrire aux mises à jour de l'API
    this.api.subscribe((data) => {
      this.updateDashboard(data);
    });
    
    // Démarrer la simulation
    this.api.startSimulation(500);
  }

  // Mettre à jour le dashboard
  updateDashboard(data) {
    // Mettre à jour les stats globales
    this.updateGlobalStats(data.globalStats);
    
    // Mettre à jour les cartes agents
    this.updateAgentCards(data.agents);
    
    // Mettre à jour le feed d'activité
    this.updateActivityFeed(data.activityLog);
  }

  // Mettre à jour les stats globales
  updateGlobalStats(stats) {
    const devisEl = document.getElementById('stat-devis');
    const scoreEl = document.getElementById('stat-score');
    const agentsEl = document.getElementById('stat-agents');
    const uptimeEl = document.getElementById('stat-uptime');
    const xpEl = document.getElementById('stat-xp');
    
    if (devisEl) devisEl.textContent = stats.totalDevis.toLocaleString();
    if (scoreEl) scoreEl.textContent = stats.avgScore + '%';
    if (agentsEl) agentsEl.textContent = stats.activeAgents + '/' + stats.totalAgents;
    if (uptimeEl) uptimeEl.textContent = stats.uptime;
    if (xpEl) xpEl.textContent = (stats.totalXP / 1000).toFixed(1) + 'k';
  }

  // Mettre à jour les cartes agents (mise à jour sélective)
  updateAgentCards(agents) {
    agents.forEach(agent => {
      const card = document.querySelector(`[data-agent-id="${agent.id}"]`);
      if (!card) return;
      
      const isBusy = agent.status === 'busy';
      const wasBusy = card.classList.contains('pulse-busy');
      
      // Mettre à jour le statut visuel
      if (isBusy !== wasBusy) {
        if (isBusy) {
          card.classList.add('pulse-busy');
        } else {
          card.classList.remove('pulse-busy');
        }
        // Re-render complet si changement de statut
        const container = document.getElementById('agents-grid');
        const index = agents.findIndex(a => a.id === agent.id);
        const newCard = this.createAgentCard(agent);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newCard;
        const newCardEl = tempDiv.firstElementChild;
        
        // Copier les event listeners
        newCardEl.addEventListener('click', () => openAgentModal(agent.id));
        
        card.replaceWith(newCardEl);
        return;
      }
      
      // Mettre à jour la barre d'XP
      const xpPercent = (agent.xp / agent.xpToNextLevel) * 100;
      const xpBar = card.querySelector('.xp-bar');
      const xpText = card.querySelector('.xp-text');
      if (xpBar) xpBar.style.width = xpPercent + '%';
      if (xpText) xpText.textContent = `${agent.xp.toLocaleString()} / ${agent.xpToNextLevel.toLocaleString()} XP`;
      
      // Mettre à jour le niveau
      const levelBadge = card.querySelector('.level-badge');
      if (levelBadge) levelBadge.textContent = `LVL ${agent.level}`;
      
      // Mettre à jour la barre de progression de tâche
      const taskProgressContainer = card.querySelector('.task-progress-container');
      if (isBusy && agent.currentTask) {
        if (taskProgressContainer) {
          const progressBar = taskProgressContainer.querySelector('.task-progress-bar');
          const progressText = taskProgressContainer.querySelector('.task-progress-text');
          if (progressBar) progressBar.style.width = `${agent.taskProgress}%`;
          if (progressText) progressText.textContent = `${agent.currentTask.name} - ${Math.round(agent.taskProgress)}%`;
        }
      }
      
      // Mettre à jour les stats
      const statValues = card.querySelectorAll('.agent-stat-value');
      if (statValues[0]) statValues[0].textContent = agent.stats.devisAnalyzed;
      if (statValues[1]) statValues[1].textContent = agent.stats.avgScore + '%';
      if (statValues[2]) statValues[2].textContent = agent.tasksCompletedToday;
    });
  }

  // Mettre à jour le feed d'activité
  updateActivityFeed(activities) {
    const container = document.getElementById('activity-list');
    if (!container) return;
    
    // Vérifier si de nouvelles activités
    const currentCount = container.children.length;
    if (activities.length !== currentCount || 
        (activities.length > 0 && container.children[0] && 
         !container.children[0].innerHTML.includes(activities[0].text))) {
      this.renderActivityFeed();
    }
  }
}

// Fonctions globales pour le modal
function openAgentModal(agentId) {
  currentAgentId = agentId;
  const agent = mockAPI.getAgent(agentId);
  
  if (!agent) return;
  
  const modal = document.getElementById('agent-modal');
  const nameEl = document.getElementById('modal-agent-name');
  const toggle = document.getElementById('agent-toggle');
  const slider = document.getElementById('workload-slider');
  const workloadValue = document.getElementById('workload-percent');
  
  if (nameEl) nameEl.textContent = `🎛️ Contrôle: ${agent.name}`;
  if (toggle) toggle.checked = agent.status !== 'offline';
  if (slider) {
    slider.value = agent.status === 'offline' ? 0 : (agent.status === 'busy' ? 85 : 65);
    workloadValue.textContent = slider.value + '%';
  }
  
  if (modal) modal.classList.add('active');
}

function closeAgentModal() {
  const modal = document.getElementById('agent-modal');
  if (modal) modal.classList.remove('active');
  currentAgentId = null;
}

function controlAgent(action) {
  if (!currentAgentId) return;
  
  const agent = mockAPI.getAgent(currentAgentId);
  if (!agent) return;
  
  const responseEl = document.getElementById('instruction-response');
  
  switch(action) {
    case 'start':
      agent.status = 'online';
      if (responseEl) {
        responseEl.textContent = `✅ ${agent.name} démarré avec succès`;
        responseEl.classList.add('show');
      }
      break;
    case 'stop':
      agent.status = 'offline';
      agent.isProcessing = false;
      agent.currentTask = null;
      if (responseEl) {
        responseEl.textContent = `⏹️ ${agent.name} arrêté`;
        responseEl.classList.add('show');
      }
      break;
    case 'restart':
      agent.status = 'busy';
      setTimeout(() => {
        agent.status = 'online';
      }, 2000);
      if (responseEl) {
        responseEl.textContent = `🔄 ${agent.name} redémarrage en cours...`;
        responseEl.classList.add('show');
      }
      break;
    case 'logs':
      if (responseEl) {
        responseEl.innerHTML = `<strong>📋 Logs ${agent.name}:</strong><br>[${new Date().toLocaleTimeString()}] Agent actif<br>[${new Date().toLocaleTimeString()}] Traitement de données...<br>[${new Date().toLocaleTimeString()}] Opération normale`;
        responseEl.classList.add('show');
      }
      break;
  }
  
  // Mettre à jour l'affichage
  if (window.dashboard) {
    window.dashboard.renderAgents();
  }
}

function sendInstruction() {
  if (!currentAgentId) return;
  
  const input = document.getElementById('agent-instruction');
  const responseEl = document.getElementById('instruction-response');
  const agent = mockAPI.getAgent(currentAgentId);
  
  if (!input || !agent) return;
  
  const instruction = input.value.trim();
  if (!instruction) return;
  
  // Simuler une réponse
  const responses = [
    `Instruction "${instruction}" reçue et en cours de traitement`,
    `Agent ${agent.name} a exécuté: ${instruction}`,
    `Commande validée - ${instruction}`,
    `Traitement de l'instruction en arrière-plan...`
  ];
  
  const randomResponse = responses[Math.floor(Math.random() * responses.length)];
  
  if (responseEl) {
    responseEl.textContent = `✅ ${randomResponse}`;
    responseEl.classList.add('show');
  }
  
  input.value = '';
}

// Fermer le modal en cliquant à l'extérieur
document.addEventListener('click', (e) => {
  const modal = document.getElementById('agent-modal');
  if (e.target === modal) {
    closeAgentModal();
  }
});

// Initialiser le dashboard au chargement
document.addEventListener('DOMContentLoaded', () => {
  // Initialiser le dashboard
  window.dashboard = new TrustDevisDashboard();
  
  console.log('🎮 TrustDevis Command Center v3.0 initialisé!');
  console.log('📊 Dashboard temps réel actif - Polling 500ms');
  console.log('🎛️ Panneau de contrôle des agents disponible');
  console.log('⚡ Système de tâches temps réel en marche');
});
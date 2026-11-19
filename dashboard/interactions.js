// interactions.js - TrustDevis Command Center - Flux d'interactions entre agents

class InteractionsManager {
  constructor() {
    this.flowNodes = [
      { id: 'ocr', name: 'OCR', icon: '📄', status: 'online', latency: 12, requests: 1247 },
      { id: 'normalizer', name: 'Normalizer', icon: '🔄', status: 'online', latency: 15, requests: 1234 },
      { id: 'pricing', name: 'Pricing', icon: '💰', status: 'busy', latency: 45, requests: 1189 },
      { id: 'market', name: 'MarketScore', icon: '📊', status: 'online', latency: 22, requests: 1185 }
    ];
    
    this.connections = [
      { from: 'ocr', to: 'normalizer', latency: 8, errors: 0 },
      { from: 'normalizer', to: 'pricing', latency: 12, errors: 2 },
      { from: 'pricing', to: 'market', latency: 18, errors: 0 }
    ];
    
    this.interactionLogs = [];
    this.maxLogs = 20;
    
    this.init();
  }

  init() {
    this.startRealtimeSimulation();
    this.startLogGeneration();
  }

  // Démarrer la simulation temps réel
  startRealtimeSimulation() {
    // Mettre à jour les stats des nœuds
    setInterval(() => {
      this.flowNodes.forEach(node => {
        // Variation aléatoire de la latence
        const variation = Math.floor(Math.random() * 10) - 5;
        node.latency = Math.max(5, node.latency + variation);
        
        // Incrémenter les requêtes
        node.requests += Math.floor(Math.random() * 5);
        
        // Mettre à jour le statut aléatoirement
        if (Math.random() < 0.05) {
          const statuses = ['online', 'busy', 'online'];
          node.status = statuses[Math.floor(Math.random() * statuses.length)];
        }
        
        this.updateNodeDisplay(node);
      });
      
      // Mettre à jour les connexions
      this.connections.forEach(conn => {
        conn.latency = Math.max(2, conn.latency + Math.floor(Math.random() * 6) - 3);
        if (Math.random() < 0.02) {
          conn.errors += Math.floor(Math.random() * 2);
        }
        this.updateConnectionDisplay(conn);
      });
      
      // Mettre à jour les stats globales
      this.updateGlobalStats();
      
    }, 2000);
  }

  // Mettre à jour l'affichage d'un nœud
  updateNodeDisplay(node) {
    const nodeEl = document.getElementById(`node-${node.id}`);
    if (!nodeEl) return;
    
    // Mettre à jour le statut visuel
    nodeEl.className = `flow-node ${node.status}`;
    
    // Mettre à jour les stats
    const latencyEl = nodeEl.querySelector('.flow-stat.latency');
    const requestsEl = nodeEl.querySelector('.flow-stat.requests');
    const statusEl = nodeEl.querySelector('.flow-node-status');
    
    if (latencyEl) latencyEl.textContent = `${node.latency}ms`;
    if (requestsEl) requestsEl.textContent = `${(node.requests / 1000).toFixed(1)}k req`;
    if (statusEl) statusEl.className = `flow-node-status ${node.status}`;
  }

  // Mettre à jour l'affichage d'une connexion
  updateConnectionDisplay(conn) {
    const arrowId = `arrow-${conn.from}-${conn.to === 'market' ? 'pricing-market' : conn.from + '-' + conn.to}`;
    const arrowEl = document.getElementById(arrowId);
    if (!arrowEl) return;
    
    const latencyEl = arrowEl.querySelector('.flow-latency');
    const errorsEl = arrowEl.querySelector('.flow-errors');
    
    if (latencyEl) latencyEl.textContent = `${conn.latency}ms`;
    if (errorsEl) errorsEl.textContent = `${conn.errors} err`;
    
    // Changer la couleur si erreurs
    if (conn.errors > 0) {
      arrowEl.querySelector('.flow-line').style.background = `linear-gradient(90deg, var(--accent-yellow), var(--accent-red))`;
    } else {
      arrowEl.querySelector('.flow-line').style.background = `linear-gradient(90deg, var(--accent-cyan), var(--accent-violet))`;
    }
  }

  // Mettre à jour les stats globales
  updateGlobalStats() {
    const totalRequests = this.flowNodes.reduce((sum, node) => sum + node.requests, 0);
    const avgLatency = Math.round(this.flowNodes.reduce((sum, node) => sum + node.latency, 0) / this.flowNodes.length);
    const totalErrors = this.connections.reduce((sum, conn) => sum + conn.errors, 0);
    const successRate = ((totalRequests - totalErrors) / totalRequests * 100).toFixed(1);
    
    const throughputEl = document.getElementById('total-throughput');
    const latencyEl = document.getElementById('avg-latency');
    const successEl = document.getElementById('success-rate');
    const connectionsEl = document.getElementById('active-connections');
    
    if (throughputEl) throughputEl.textContent = Math.floor(totalRequests / 10).toLocaleString();
    if (latencyEl) latencyEl.textContent = `${avgLatency}ms`;
    if (successEl) successEl.textContent = `${successRate}%`;
    if (connectionsEl) connectionsEl.textContent = this.connections.length;
  }

  // Générer des logs
  startLogGeneration() {
    const logTypes = [
      { source: 'OCR', dest: 'Normalizer', message: 'Envoi données extraites' },
      { source: 'Normalizer', dest: 'Pricing', message: 'Données normalisées' },
      { source: 'Pricing', dest: 'MarketScore', message: 'Prix calculés' },
      { source: 'MarketScore', dest: 'API', message: 'Score généré' },
      { source: 'OCR', dest: 'Cache', message: 'Mise en cache image' },
      { source: 'Pricing', dest: 'DB', message: 'Sauvegarde tarifs' },
      { source: 'Normalizer', dest: 'Validator', message: 'Validation schema' },
      { source: 'MarketScore', dest: 'Report', message: 'Génération rapport' }
    ];
    
    setInterval(() => {
      const logType = logTypes[Math.floor(Math.random() * logTypes.length)];
      this.addLog(logType.source, logType.dest, logType.message);
    }, 1500);
  }

  // Ajouter un log
  addLog(source, dest, message) {
    const time = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    this.interactionLogs.unshift({ time, source, dest, message });
    
    if (this.interactionLogs.length > this.maxLogs) {
      this.interactionLogs.pop();
    }
    
    this.renderLogs();
  }

  // Rendre les logs
  renderLogs() {
    const container = document.getElementById('interaction-logs-list');
    if (!container) return;
    
    container.innerHTML = this.interactionLogs.map(log => `
      <div class="log-item">
        <span class="log-time">[${log.time}]</span>
        <span class="log-source">${log.source}</span>
        <span class="log-arrow">→</span>
        <span class="log-dest">${log.dest}</span>
        <span class="log-message">${log.message}</span>
      </div>
    `).join('');
    
    // Scroll vers le bas
    container.scrollTop = 0;
  }
}

// Initialiser le gestionnaire d'interactions
document.addEventListener('DOMContentLoaded', () => {
  window.interactionsManager = new InteractionsManager();
  console.log('🔄 Gestionnaire de flux d\'interactions initialisé');
});

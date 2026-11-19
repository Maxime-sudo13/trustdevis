/**
 * TrustDevis - Simulation Heatmap
 * 
 * Génère des heatmaps de clics et de scroll pour visualiser
 * l'engagement utilisateur sur la landing page.
 */

class TrustDevisHeatmap {
  constructor(options = {}) {
    this.options = {
      container: document.body,
      gridSize: 20, // Taille de la grille en pixels
      maxOpacity: 0.6,
      colors: ['#00ff00', '#ffff00', '#ff0000'], // Vert → Jaune → Rouge
      ...options
    };
    
    this.clicks = [];
    this.scrolls = [];
    this.canvas = null;
    this.ctx = null;
    this.isRecording = false;
  }

  /**
   * Démarre l'enregistrement des interactions
   */
  start() {
    if (this.isRecording) return;
    this.isRecording = true;
    
    this.setupCanvas();
    this.attachListeners();
    console.log('[Heatmap] Recording started');
  }

  /**
   * Arrête l'enregistrement
   */
  stop() {
    this.isRecording = false;
    this.detachListeners();
    console.log('[Heatmap] Recording stopped');
  }

  /**
   * Configure le canvas de heatmap
   */
  setupCanvas() {
    this.canvas = document.createElement('canvas');
    this.canvas.id = 'td-heatmap';
    this.canvas.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 9999;
      opacity: 0;
      transition: opacity 0.3s;
    `;
    
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    
    this.ctx = this.canvas.getContext('2d');
    document.body.appendChild(this.canvas);
  }

  /**
   * Attache les écouteurs d'événements
   */
  attachListeners() {
    this.clickHandler = (e) => {
      this.clicks.push({
        x: e.clientX,
        y: e.clientY + window.scrollY,
        timestamp: Date.now(),
        element: e.target.tagName,
        id: e.target.id,
        class: e.target.className
      });
    };

    this.scrollHandler = throttle(() => {
      this.scrolls.push({
        y: window.scrollY,
        timestamp: Date.now(),
        pageHeight: document.body.scrollHeight
      });
    }, 500);

    document.addEventListener('click', this.clickHandler, true);
    window.addEventListener('scroll', this.scrollHandler);
  }

  /**
   * Détache les écouteurs
   */
  detachListeners() {
    document.removeEventListener('click', this.clickHandler, true);
    window.removeEventListener('scroll', this.scrollHandler);
  }

  /**
   * Génère et affiche la heatmap
   */
  render() {
    if (!this.canvas) return;
    
    this.canvas.style.opacity = '1';
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Dessiner les zones de chaleur
    this.clicks.forEach(click => {
      this.drawHeatPoint(click.x, click.y - window.scrollY);
    });
    
    console.log('[Heatmap] Rendered with', this.clicks.length, 'clicks');
  }

  /**
   * Dessine un point de chaleur
   */
  drawHeatPoint(x, y) {
    const radius = 30;
    const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, radius);
    
    gradient.addColorStop(0, 'rgba(255, 0, 0, 0.4)');
    gradient.addColorStop(0.5, 'rgba(255, 255, 0, 0.2)');
    gradient.addColorStop(1, 'rgba(255, 255, 0, 0)');
    
    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, Math.PI * 2);
    this.ctx.fill();
  }

  /**
   * Masque la heatmap
   */
  hide() {
    if (this.canvas) {
      this.canvas.style.opacity = '0';
    }
  }

  /**
   * Exporte les données de heatmap
   */
  export() {
    return {
      clicks: this.clicks,
      scrolls: this.scrolls,
      summary: this.generateSummary()
    };
  }

  /**
   * Génère un résumé des données
   */
  generateSummary() {
    const totalClicks = this.clicks.length;
    const uniqueElements = [...new Set(this.clicks.map(c => c.element))];
    
    // Zones les plus cliquées
    const zoneClicks = {};
    this.clicks.forEach(click => {
      const zone = this.getZone(click.y);
      zoneClicks[zone] = (zoneClicks[zone] || 0) + 1;
    });
    
    return {
      totalClicks,
      uniqueElements: uniqueElements.length,
      topZones: Object.entries(zoneClicks)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5),
      avgScrollDepth: this.scrolls.length > 0 
        ? this.scrolls.reduce((a, s) => a + s.y, 0) / this.scrolls.length 
        : 0
    };
  }

  /**
   * Détermine la zone d'un clic
   */
  getZone(y) {
    const zones = [
      { name: 'Hero', min: 0, max: 600 },
      { name: 'Upload', min: 600, max: 1200 },
      { name: 'Comment ça marche', min: 1200, max: 1800 },
      { name: 'Témoignages', min: 1800, max: 2400 },
      { name: 'Tarifs', min: 2400, max: 3000 },
      { name: 'Footer', min: 3000, max: Infinity }
    ];
    
    const zone = zones.find(z => y >= z.min && y < z.max);
    return zone ? zone.name : 'Autre';
  }

  /**
   * Génère un rapport visuel
   */
  generateReport() {
    const summary = this.generateSummary();
    
    return `
╔══════════════════════════════════════════════════════════════╗
║           TRUSTDEVIS - RAPPORT HEATMAP                       ║
╠══════════════════════════════════════════════════════════════╣
║  Total clics: ${summary.totalClicks.toString().padEnd(45)}║
║  Éléments uniques: ${summary.uniqueElements.toString().padEnd(40)}║
║  Profondeur scroll moyenne: ${Math.round(summary.avgScrollDepth).toString().padEnd(29)}px ║
╠══════════════════════════════════════════════════════════════╣
║  ZONES LES PLUS CLIQUÉES:                                    ║
${summary.topZones.map(([zone, count]) => 
  `║    • ${zone.padEnd(15)}: ${count.toString().padEnd(35)}║`
).join('\n')}
╚══════════════════════════════════════════════════════════════╝
    `;
  }
}

// Utilitaire throttle
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Exposer globalement
window.TrustDevisHeatmap = TrustDevisHeatmap;

// Usage:
// const heatmap = new TrustDevisHeatmap();
// heatmap.start(); // Commencer l'enregistrement
// heatmap.render(); // Afficher la heatmap
// heatmap.export(); // Exporter les données
// console.log(heatmap.generateReport()); // Voir le rapport

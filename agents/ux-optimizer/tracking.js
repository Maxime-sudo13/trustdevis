/**
 * TrustDevis - Système de Tracking UX
 * 
 * Tracking des événements utilisateurs pour analyse du funnel
 * et optimisation des conversions.
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    endpoint: '/api/analytics/events', // Endpoint pour envoyer les événements
    debug: false, // Mettre à true pour voir les logs en console
    sampleRate: 1.0, // 1.0 = 100% des événements
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
  };

  // État de la session
  const state = {
    sessionId: null,
    userId: null,
    startTime: Date.now(),
    events: [],
    funnel: {
      landingViewed: false,
      uploadSectionViewed: false,
      fileSelected: false,
      consentGiven: false,
      analysisStarted: false,
      analysisCompleted: false,
      resultViewed: false,
      ctaClicked: false,
    }
  };

  /**
   * Initialise le tracking
   */
  function init() {
    // Générer session ID
    state.sessionId = generateId();
    state.userId = getOrCreateUserId();
    
    // Tracker les événements de page
    trackPageView();
    
    // Configurer les observers
    setupIntersectionObserver();
    setupEventListeners();
    
    // Envoyer les événements périodiquement
    setInterval(flushEvents, 5000);
    
    // Envoyer avant fermeture
    window.addEventListener('beforeunload', flushEvents);
    
    log('TrustDevis Tracking initialized', { sessionId: state.sessionId });
  }

  /**
   * Génère un ID unique
   */
  function generateId() {
    return 'td_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }

  /**
   * Récupère ou crée l'ID utilisateur persistant
   */
  function getOrCreateUserId() {
    let userId = localStorage.getItem('td_user_id');
    if (!userId) {
      userId = generateId();
      localStorage.setItem('td_user_id', userId);
    }
    return userId;
  }

  /**
   * Track une vue de page
   */
  function trackPageView() {
    const event = {
      type: 'pageview',
      timestamp: Date.now(),
      data: {
        url: window.location.href,
        referrer: document.referrer,
        screenSize: `${window.innerWidth}x${window.innerHeight}`,
        device: getDeviceType(),
      }
    };
    
    queueEvent(event);
    state.funnel.landingViewed = true;
  }

  /**
   * Track un événement personnalisé
   */
  function track(eventName, data = {}) {
    const event = {
      type: 'event',
      name: eventName,
      timestamp: Date.now(),
      data: {
        ...data,
        timeOnPage: Date.now() - state.startTime,
      }
    };
    
    queueEvent(event);
    updateFunnel(eventName, data);
    log('Event tracked:', eventName, data);
  }

  /**
   * Ajoute un événement à la file d'attente
   */
  function queueEvent(event) {
    event.sessionId = state.sessionId;
    event.userId = state.userId;
    state.events.push(event);
  }

  /**
   * Met à jour le funnel de conversion
   */
  function updateFunnel(eventName, data) {
    switch(eventName) {
      case 'upload_section_visible':
        state.funnel.uploadSectionViewed = true;
        break;
      case 'file_selected':
        state.funnel.fileSelected = true;
        break;
      case 'consent_given':
        state.funnel.consentGiven = true;
        break;
      case 'analysis_started':
        state.funnel.analysisStarted = true;
        break;
      case 'analysis_completed':
        state.funnel.analysisCompleted = true;
        break;
      case 'result_viewed':
        state.funnel.resultViewed = true;
        break;
      case 'cta_premium_clicked':
      case 'cta_download_clicked':
        state.funnel.ctaClicked = true;
        break;
    }
  }

  /**
   * Envoie les événements au serveur
   */
  function flushEvents() {
    if (state.events.length === 0) return;
    
    const eventsToSend = [...state.events];
    state.events = [];
    
    // Envoyer via Beacon API si disponible (plus fiable sur beforeunload)
    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(eventsToSend)], { type: 'application/json' });
      navigator.sendBeacon(CONFIG.endpoint, blob);
    } else {
      // Fallback fetch
      fetch(CONFIG.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventsToSend),
        keepalive: true
      }).catch(err => log('Failed to send events:', err));
    }
    
    log('Flushed', eventsToSend.length, 'events');
  }

  /**
   * Configure l'IntersectionObserver pour tracker les vues de sections
   */
  function setupIntersectionObserver() {
    if (!('IntersectionObserver' in window)) return;
    
    const sections = [
      { selector: '#upload-section', event: 'upload_section_visible' },
      { selector: '#result-section', event: 'result_section_visible' },
      { selector: '#comment-ca-marche', event: 'how_it_works_visible' },
      { selector: '#tarifs', event: 'pricing_visible' },
    ];
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const section = sections.find(s => entry.target.matches(s.selector));
          if (section) {
            track(section.event, {
              timeToView: Date.now() - state.startTime
            });
          }
        }
      });
    }, { threshold: 0.5 });
    
    sections.forEach(section => {
      const el = document.querySelector(section.selector);
      if (el) observer.observe(el);
    });
  }

  /**
   * Configure les écouteurs d'événements
   */
  function setupEventListeners() {
    // Track scroll depth
    let maxScroll = 0;
    let scrollTracked = false;
    
    window.addEventListener('scroll', throttle(() => {
      const scrollPercent = Math.round(
        (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
      );
      maxScroll = Math.max(maxScroll, scrollPercent);
      
      // Track à 25%, 50%, 75%, 100%
      [25, 50, 75, 100].forEach(threshold => {
        if (maxScroll >= threshold && !scrollTracked) {
          track('scroll_depth', { depth: threshold });
          if (threshold === 100) scrollTracked = true;
        }
      });
    }, 500));

    // Track clicks sur les CTAs principaux
    document.addEventListener('click', (e) => {
      const target = e.target.closest('[data-track]');
      if (target) {
        const eventName = target.dataset.track;
        track(eventName, {
          element: target.tagName,
          text: target.textContent?.trim(),
          location: window.location.pathname
        });
      }
    });
  }

  /**
   * Détecte le type d'appareil
   */
  function getDeviceType() {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }

  /**
   * Throttle function
   */
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

  /**
   * Log debug
   */
  function log(...args) {
    if (CONFIG.debug) {
      console.log('[TrustDevis Tracking]', ...args);
    }
  }

  // Exposer l'API publique
  window.TrustDevisTracking = {
    track,
    getFunnel: () => state.funnel,
    getSessionId: () => state.sessionId,
    flush: flushEvents
  };

  // Initialiser au chargement
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

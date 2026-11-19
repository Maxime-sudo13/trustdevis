// agents_data.js - Données des 14 agents TrustDevis avec stats et gamification

const AGENTS_DATA = {
  agents: [
    // AGENTS CORE (8)
    {
      id: "agent-ocr",
      name: "OCR & Parser",
      emoji: "🔍",
      role: "Extraction texte devis",
      status: "online",
      level: 7,
      xp: 8750,
      xpToNextLevel: 10000,
      stats: {
        devisAnalyzed: 1247,
        avgScore: 78.5,
        accuracy: 94.2,
        responseTime: 1.2,
        streak: 15
      },
      badges: ["first_blood", "century", "speed_demon", "perfect_week"],
      color: "#06b6d4"
    },
    {
      id: "agent-normalizer",
      name: "Normalizer",
      emoji: "📄",
      role: "Classification catégories",
      status: "online",
      level: 6,
      xp: 6200,
      xpToNextLevel: 8000,
      stats: {
        devisAnalyzed: 892,
        avgScore: 82.1,
        accuracy: 96.8,
        responseTime: 0.8,
        streak: 8
      },
      badges: ["first_blood", "century", "precision_master"],
      color: "#8b5cf6"
    },
    {
      id: "agent-pricing",
      name: "Pricing Engine",
      emoji: "💰",
      role: "Prix médian marché",
      status: "busy",
      level: 5,
      xp: 4800,
      xpToNextLevel: 6000,
      stats: {
        devisAnalyzed: 654,
        avgScore: 75.3,
        accuracy: 91.5,
        responseTime: 2.1,
        streak: 3
      },
      badges: ["first_blood", "fifty_deals"],
      color: "#f59e0b"
    },
    {
      id: "agent-marketscore",
      name: "MarketScore",
      emoji: "🎯",
      role: "Score confiance 0-100",
      status: "online",
      level: 8,
      xp: 9200,
      xpToNextLevel: 12000,
      stats: {
        devisAnalyzed: 1567,
        avgScore: 85.4,
        accuracy: 97.1,
        responseTime: 1.8,
        streak: 22
      },
      badges: ["first_blood", "century", "speed_demon", "perfect_month", "core_product"],
      color: "#ec4899"
    },
    {
      id: "agent-leadfinder",
      name: "LeadFinder",
      emoji: "👁️",
      role: "Détection opportunités",
      status: "online",
      level: 4,
      xp: 3200,
      xpToNextLevel: 5000,
      stats: {
        devisAnalyzed: 423,
        avgScore: 71.8,
        accuracy: 89.2,
        responseTime: 1.5,
        streak: 0
      },
      badges: ["first_blood", "data_miner"],
      color: "#10b981"
    },
    {
      id: "agent-crm",
      name: "CRM & Relances",
      emoji: "📊",
      role: "Gestion clients",
      status: "online",
      level: 6,
      xp: 6800,
      xpToNextLevel: 8000,
      stats: {
        devisAnalyzed: 756,
        avgScore: 88.2,
        accuracy: 95.5,
        responseTime: 1.3,
        streak: 12
      },
      badges: ["first_blood", "customer_lover", "retention_master"],
      color: "#6366f1"
    },
    {
      id: "agent-compliance",
      name: "Compliance RGPD",
      emoji: "🛡️",
      role: "Conformité données",
      status: "online",
      level: 5,
      xp: 5100,
      xpToNextLevel: 6000,
      stats: {
        devisAnalyzed: 0,
        avgScore: 100,
        accuracy: 100,
        responseTime: 0.5,
        streak: 45
      },
      badges: ["first_blood", "security_guru", "gdpr_master"],
      color: "#14b8a6"
    },
    {
      id: "agent-billing",
      name: "Billing",
      emoji: "💳",
      role: "Paiements Stripe",
      status: "online",
      level: 4,
      xp: 3800,
      xpToNextLevel: 5000,
      stats: {
        devisAnalyzed: 0,
        avgScore: 99.9,
        accuracy: 99.9,
        responseTime: 0.3,
        streak: 30
      },
      badges: ["first_blood", "money_maker"],
      color: "#f97316"
    },
    // AGENTS STRATÉGIQUES (6) - NOUVEAUX
    {
      id: "agent-ux",
      name: "UX Optimizer",
      emoji: "✨",
      role: "Conversion & Analytics",
      status: "online",
      level: 3,
      xp: 2500,
      xpToNextLevel: 4000,
      stats: {
        devisAnalyzed: 150,
        avgScore: 85,
        accuracy: 92,
        responseTime: 0.8,
        streak: 5
      },
      badges: ["optimizer", "conversion_pro"],
      color: "#a855f7",
      isNew: true
    },
    {
      id: "agent-bizdev",
      name: "BizDev",
      emoji: "🤝",
      role: "Partenariats",
      status: "online",
      level: 2,
      xp: 1800,
      xpToNextLevel: 3000,
      stats: {
        devisAnalyzed: 0,
        avgScore: 95,
        accuracy: 98,
        responseTime: 1.2,
        streak: 3
      },
      badges: ["deal_maker"],
      color: "#22c55e",
      isNew: true
    },
    {
      id: "agent-mobile",
      name: "Mobile",
      emoji: "📱",
      role: "Apps iOS/Android",
      status: "online",
      level: 4,
      xp: 3200,
      xpToNextLevel: 5000,
      stats: {
        devisAnalyzed: 89,
        avgScore: 88,
        accuracy: 94,
        responseTime: 1.5,
        streak: 7
      },
      badges: ["mobile_master", "app_builder"],
      color: "#3b82f6",
      isNew: true
    },
    {
      id: "agent-ml",
      name: "ML Engine",
      emoji: "🧠",
      role: "IA Avancée",
      status: "online",
      level: 5,
      xp: 4800,
      xpToNextLevel: 6000,
      stats: {
        devisAnalyzed: 2100,
        avgScore: 99.4,
        accuracy: 99.4,
        responseTime: 2.1,
        streak: 15
      },
      badges: ["ml_master", "fraud_detector", "price_predictor"],
      color: "#ef4444",
      isNew: true
    },
    {
      id: "agent-artisans",
      name: "Artisans Compare",
      emoji: "🔨",
      role: "Comparaison artisans",
      status: "online",
      level: 3,
      xp: 2900,
      xpToNextLevel: 4000,
      stats: {
        devisAnalyzed: 45,
        avgScore: 87,
        accuracy: 91,
        responseTime: 1.1,
        streak: 4
      },
      badges: ["artisan_matcher"],
      color: "#f59e0b",
      isNew: true
    },
    {
      id: "agent-project",
      name: "Project Manager",
      emoji: "🏗️",
      role: "Gestion projet travaux",
      status: "online",
      level: 2,
      xp: 1500,
      xpToNextLevel: 3000,
      stats: {
        devisAnalyzed: 12,
        avgScore: 92,
        accuracy: 95,
        responseTime: 0.9,
        streak: 2
      },
      badges: ["project_master"],
      color: "#8b5cf6",
      isNew: true
    }
  ],

  badges: {
    first_blood: { name: "First Blood", icon: "🩸", desc: "Premier devis analysé", rarity: "common" },
    fifty_deals: { name: "50 Devis", icon: "📋", desc: "50 devis traités", rarity: "common" },
    century: { name: "100 Devis", icon: "💯", desc: "100 devis analysés", rarity: "rare" },
    speed_demon: { name: "Speed Demon", icon: "⚡", desc: "Temps de réponse < 1s", rarity: "rare" },
    precision_master: { name: "Précision", icon: "🎯", desc: "95%+ de précision", rarity: "rare" },
    data_miner: { name: "Data Miner", icon: "⛏️", desc: "500+ données extraites", rarity: "rare" },
    perfect_week: { name: "Perfect Week", icon: "🔥", desc: "7 jours de suite actif", rarity: "epic" },
    perfect_month: { name: "Perfect Month", icon: "📅", desc: "30 jours de suite actif", rarity: "epic" },
    core_product: { name: "Core", icon: "🎯", desc: "Cœur du produit", rarity: "epic" },
    customer_lover: { name: "Customer Love", icon: "❤️", desc: "100 clients satisfaits", rarity: "epic" },
    retention_master: { name: "Retention", icon: "🔄", desc: "90% rétention", rarity: "epic" },
    security_guru: { name: "Security", icon: "🔒", desc: "Zero faille", rarity: "epic" },
    gdpr_master: { name: "GDPR", icon: "📜", desc: "Conformité 100%", rarity: "epic" },
    money_maker: { name: "Money", icon: "💰", desc: "10k€ générés", rarity: "epic" },
    optimizer: { name: "Optimizer", icon: "📈", desc: "+25% conversion", rarity: "rare" },
    conversion_pro: { name: "Conversion", icon: "🎯", desc: "Expert CRO", rarity: "rare" },
    deal_maker: { name: "Deal Maker", icon: "🤝", desc: "3 partenariats", rarity: "rare" },
    mobile_master: { name: "Mobile", icon: "📱", desc: "App publiée", rarity: "epic" },
    app_builder: { name: "Builder", icon: "🏗️", desc: "Feature mobile", rarity: "rare" },
    ml_master: { name: "ML Master", icon: "🧠", desc: "Modèle déployé", rarity: "epic" },
    fraud_detector: { name: "Fraud", icon: "🕵️", desc: "Fraude détectée", rarity: "epic" },
    price_predictor: { name: "Predictor", icon: "🔮", desc: "Prédiction 95%+", rarity: "epic" },
    artisan_matcher: { name: "Matcher", icon: "🔨", desc: "Artisan trouvé", rarity: "rare" },
    project_master: { name: "Project", icon: "📊", desc: "Projet livré", rarity: "rare" }
  },

  globalStats: {
    totalDevis: 8940,
    avgScore: 87.3,
    activeAgents: 15,
    totalAgents: 15,
    totalXP: 68550,
    uptime: "99.97%",
    lastUpdate: new Date().toISOString()
  }
};

// Export pour utilisation dans les modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AGENTS_DATA;
}

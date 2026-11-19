-- Schéma de base de données pour les données tarifaires TrustDevis
-- Stockage des mentions de prix collectées depuis le web

-- Table principale des données tarifaires
CREATE TABLE IF NOT EXISTS pricing_data (
    id VARCHAR(32) PRIMARY KEY,
    type_travaux VARCHAR(50) NOT NULL,
    sous_categorie VARCHAR(100),
    prix DECIMAL(12, 2),
    prix_unitaire DECIMAL(10, 2),
    unite VARCHAR(20), -- m², heure, forfait, etc.
    region VARCHAR(100),
    departement VARCHAR(10),
    date_mention TIMESTAMP,
    source VARCHAR(50) NOT NULL,
    url_source TEXT,
    contexte TEXT, -- Description anonymisée
    confiance INTEGER CHECK (confiance >= 0 AND confiance <= 100),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index pour les recherches fréquentes
    INDEX idx_type_travaux (type_travaux),
    INDEX idx_region (region),
    INDEX idx_source (source),
    INDEX idx_confiance (confiance),
    INDEX idx_date_mention (date_mention),
    INDEX idx_scraped_at (scraped_at)
);

-- Table des statistiques agrégées par type et région
CREATE TABLE IF NOT EXISTS pricing_stats (
    id SERIAL PRIMARY KEY,
    type_travaux VARCHAR(50) NOT NULL,
    sous_categorie VARCHAR(100),
    region VARCHAR(100),
    count_total INTEGER DEFAULT 0,
    prix_moyen DECIMAL(12, 2),
    prix_median DECIMAL(12, 2),
    prix_min DECIMAL(12, 2),
    prix_max DECIMAL(12, 2),
    std_deviation DECIMAL(12, 2),
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_stats (type_travaux, sous_categorie, region)
);

-- Table des sources scrapées
CREATE TABLE IF NOT EXISTS pricing_sources (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL,
    url_base VARCHAR(255),
    statut VARCHAR(20) DEFAULT 'active', -- active, inactive, error
    dernier_scrap TIMESTAMP,
    items_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de log des exécutions de scraping
CREATE TABLE IF NOT EXISTS pricing_scrap_log (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    items_found INTEGER DEFAULT 0,
    items_new INTEGER DEFAULT 0,
    status VARCHAR(20), -- success, partial, error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vue pour les données de haute confiance uniquement
CREATE OR REPLACE VIEW pricing_data_high_confidence AS
SELECT * FROM pricing_data
WHERE confiance >= 70
ORDER BY scraped_at DESC;

-- Vue pour les statistiques par type de travaux
CREATE OR REPLACE VIEW pricing_summary_by_type AS
SELECT 
    type_travaux,
    sous_categorie,
    COUNT(*) as count,
    AVG(prix) as prix_moyen,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY prix) as prix_median,
    MIN(prix) as prix_min,
    MAX(prix) as prix_max,
    STDDEV(prix) as ecart_type
FROM pricing_data
WHERE prix IS NOT NULL AND prix > 0
GROUP BY type_travaux, sous_categorie
ORDER BY count DESC;

-- Vue pour les statistiques par région
CREATE OR REPLACE VIEW pricing_summary_by_region AS
SELECT 
    region,
    type_travaux,
    COUNT(*) as count,
    AVG(prix) as prix_moyen,
    MIN(prix) as prix_min,
    MAX(prix) as prix_max
FROM pricing_data
WHERE region IS NOT NULL AND prix IS NOT NULL
GROUP BY region, type_travaux
ORDER BY region, count DESC;

-- Insertion des sources par défaut
INSERT INTO pricing_sources (nom, url_base, statut) VALUES
('reddit', 'https://reddit.com', 'active'),
('bricoleurdudimanche', 'https://bricoleurdudimanche.com', 'active'),
('leboncoin', 'https://leboncoin.fr', 'inactive'),
('seloger', 'https://seloger.com', 'inactive'),
('datagouv_permis', 'https://data.gouv.fr', 'inactive')
ON CONFLICT (nom) DO NOTHING;

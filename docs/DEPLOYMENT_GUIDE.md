# TrustDevis - Guide de Déploiement

> Version 1.0 | 9 Mars 2026 | Agent Architecte

---

## Vue d'Ensemble

Ce guide décrit le déploiement complet de TrustDevis sur un VPS Hostinger (ou tout serveur Ubuntu 22.04/24.04).

**Temps estimé:** 45-60 minutes  
**Niveau:** Intermédiaire  
**Prérequis:** Accès root au VPS, nom de domaine configuré

---

## Prérequis

### Matériel Recommandé (VPS)

| Plan | CPU | RAM | Stockage | Prix/mois | Usage |
|------|-----|-----|----------|-----------|-------|
| KVM 1 | 1 cœur | 4 GB | 50 GB NVMe | ~€6 | Développement |
| **KVM 2** | **2 cœurs** | **8 GB** | **100 GB NVMe** | **~€10** | **Production MVP** |
| KVM 4 | 4 cœurs | 16 GB | 200 GB NVMe | ~€20 | Production scale |

**Recommandé pour MVP:** KVM 2 (2 cœurs, 8GB RAM)

### Logiciels Requis

- Ubuntu 22.04 LTS ou 24.04 LTS
- Docker 24.0+
- Docker Compose 2.20+
- Nginx
- Certbot (Let's Encrypt)

### Domaine

- Nom de domaine acheté et configuré
- DNS pointant vers le VPS:
  - `A` record: `api.trustdevis.com` → IP_VPS
  - `A` record: `admin.trustdevis.com` → IP_VPS
  - `A` record: `trustdevis.com` → IP_VPS

---

## Déploiement Automatisé (Recommandé)

### 1. Script d'Installation

Créer et exécuter le script d'installation:

```bash
# Sur votre machine locale, créer le script
cat > install-trustdevis.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 TrustDevis - Script d'installation"
echo "======================================"

# Configuration
DOMAIN="${DOMAIN:-trustdevis.com}"
API_DOMAIN="api.${DOMAIN}"
ADMIN_DOMAIN="admin.${DOMAIN}"
EMAIL="${EMAIL:-admin@${DOMAIN}}"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier root
if [ "$EUID" -ne 0 ]; then
    error "Veuillez exécuter en root: sudo ./install-trustdevis.sh"
    exit 1
fi

# Mise à jour système
log "Mise à jour du système..."
apt-get update && apt-get upgrade -y

# Installation des dépendances
log "Installation des dépendances..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    ufw \
    fail2ban \
    htop

# Installation Docker
log "Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    usermod -aG docker $SUDO_USER || true
    log "Docker installé avec succès"
else
    log "Docker déjà installé"
fi

# Création des répertoires
log "Création de la structure..."
mkdir -p /opt/trustdevis/{agents,database,nginx,scripts,backups}
mkdir -p /opt/trustdevis/agents/{directeur,ocr,normalizer,pricing,marketscore}
mkdir -p /var/log/trustdevis

# Configuration firewall
log "Configuration du firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Configuration fail2ban
log "Configuration fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOFBAN'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOFBAN

systemctl restart fail2ban

log "Installation de base terminée!"
log "Prochaine étape: Configurer les variables d'environnement"
EOF

chmod +x install-trustdevis.sh
```

### 2. Exécution sur le VPS

```bash
# Copier le script sur le VPS
scp install-trustdevis.sh root@IP_VPS:/root/

# Se connecter au VPS
ssh root@IP_VPS

# Exécuter
./install-trustdevis.sh
```

---

## Déploiement Manuel (Alternative)

### Étape 1: Préparation du Serveur

```bash
# Connexion SSH
ssh root@IP_VPS

# Mise à jour
apt update && apt upgrade -y

# Installation des outils de base
apt install -y curl wget git nginx certbot python3-certbot-nginx ufw fail2ban
```

### Étape 2: Installation Docker

```bash
# Supprimer anciennes versions
apt remove docker docker-engine docker.io containerd runc

# Ajouter le repo Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Vérification
docker --version
docker compose version
```

### Étape 3: Structure des Répertoires

```bash
mkdir -p /opt/trustdevis/{agents,database,nginx,scripts,backups}
mkdir -p /opt/trustdevis/agents/{directeur,ocr,normalizer,pricing,marketscore}
mkdir -p /var/log/trustdevis
```

### Étape 4: Configuration Environnement

Créer le fichier `.env`:

```bash
cat > /opt/trustdevis/.env << 'EOF'
# ============================================
# TrustDevis - Configuration Production
# ============================================

# Environnement
NODE_ENV=production
TZ=Europe/Paris

# Domaines
DOMAIN=trustdevis.com
API_DOMAIN=api.trustdevis.com
ADMIN_DOMAIN=admin.trustdevis.com

# Base de données PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=trustdevis
POSTGRES_USER=trustdevis_user
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_FORT_ICI

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=VOTRE_REDIS_PASSWORD_ICI

# JWT
JWT_SECRET=VOTRE_JWT_SECRET_TRES_LONG_ET_ALEATOIRE
JWT_EXPIRES_IN=3600
JWT_REFRESH_EXPIRES_IN=604800

# API Keys
KIMI_API_KEY=sk-votre_cle_api_kimi_ici
KIMI_API_URL=https://api.moonshot.cn/v1

# Internal API Keys (communication inter-services)
INTERNAL_API_KEY=votre_cle_interne_securisee

# Ports (internes Docker)
PORT_DIRECTEUR=3001
PORT_OCR=3002
PORT_NORMALIZER=3003
PORT_PRICING=3004
PORT_MARKETSCORE=3005
PORT_DASHBOARD=3000

# Uploads
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/app/uploads

# Logging
LOG_LEVEL=info
LOG_DIR=/var/log/trustdevis

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@trustdevis.com
SMTP_PASS=votre_mot_de_passe_app

# Rate Limiting
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX=100
EOF

chmod 600 /opt/trustdevis/.env
```

**⚠️ Important:** Remplacer tous les mots de passe et clés par des valeurs sécurisées!

### Étape 5: Docker Compose

Créer `/opt/trustdevis/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # ============================================
  # Base de données
  # ============================================
  postgres:
    image: postgres:16-alpine
    container_name: trustdevis-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "127.0.0.1:5432:5432"
    networks:
      - trustdevis-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: trustdevis-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    networks:
      - trustdevis-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ============================================
  # Agents TrustDevis
  # ============================================
  agent-directeur:
    build:
      context: ./agents/directeur
      dockerfile: Dockerfile
    container_name: trustdevis-directeur
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${PORT_DIRECTEUR}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRES_IN=${JWT_EXPIRES_IN}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
      - AGENT_OCR_URL=http://agent-ocr:${PORT_OCR}
      - AGENT_NORMALIZER_URL=http://agent-normalizer:${PORT_NORMALIZER}
      - AGENT_PRICING_URL=http://agent-pricing:${PORT_PRICING}
      - AGENT_MARKETSCORE_URL=http://agent-marketscore:${PORT_MARKETSCORE}
    ports:
      - "127.0.0.1:${PORT_DIRECTEUR}:${PORT_DIRECTEUR}"
    volumes:
      - ${LOG_DIR}:/app/logs
      - uploads_data:/app/uploads
    networks:
      - trustdevis-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT_DIRECTEUR}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  agent-ocr:
    build:
      context: ./agents/ocr
      dockerfile: Dockerfile
    container_name: trustdevis-ocr
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${PORT_OCR}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
      - KIMI_API_KEY=${KIMI_API_KEY}
      - KIMI_API_URL=${KIMI_API_URL}
      - MAX_FILE_SIZE=${MAX_FILE_SIZE}
    ports:
      - "127.0.0.1:${PORT_OCR}:${PORT_OCR}"
    volumes:
      - ${LOG_DIR}:/app/logs
      - uploads_data:/app/uploads
    networks:
      - trustdevis-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT_OCR}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  agent-normalizer:
    build:
      context: ./agents/normalizer
      dockerfile: Dockerfile
    container_name: trustdevis-normalizer
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${PORT_NORMALIZER}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
      - KIMI_API_KEY=${KIMI_API_KEY}
      - KIMI_API_URL=${KIMI_API_URL}
    ports:
      - "127.0.0.1:${PORT_NORMALIZER}:${PORT_NORMALIZER}"
    volumes:
      - ${LOG_DIR}:/app/logs
    networks:
      - trustdevis-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT_NORMALIZER}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  agent-pricing:
    build:
      context: ./agents/pricing
      dockerfile: Dockerfile
    container_name: trustdevis-pricing
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${PORT_PRICING}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
    ports:
      - "127.0.0.1:${PORT_PRICING}:${PORT_PRICING}"
    volumes:
      - ${LOG_DIR}:/app/logs
    networks:
      - trustdevis-network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT_PRICING}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  agent-marketscore:
    build:
      context: ./agents/marketscore
      dockerfile: Dockerfile
    container_name: trustdevis-marketscore
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${PORT_MARKETSCORE}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
      - KIMI_API_KEY=${KIMI_API_KEY}
      - KIMI_API_URL=${KIMI_API_URL}
    ports:
      - "127.0.0.1:${PORT_MARKETSCORE}:${PORT_MARKETSCORE}"
    volumes:
      - ${LOG_DIR}:/app/logs
    networks:
      - trustdevis-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT_MARKETSCORE}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # Dashboard
  # ============================================
  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    container_name: trustdevis-dashboard
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${PORT_DASHBOARD}
      - API_URL=http://agent-directeur:${PORT_DIRECTEUR}
    ports:
      - "127.0.0.1:${PORT_DASHBOARD}:${PORT_DASHBOARD}"
    networks:
      - trustdevis-network
    depends_on:
      - agent-directeur
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT_DASHBOARD}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  uploads_data:

networks:
  trustdevis-network:
    driver: bridge
```

### Étape 6: Configuration Nginx

Créer `/opt/trustdevis/nginx/nginx.conf`:

```nginx
# TrustDevis - Configuration Nginx

upstream agent_directeur {
    server 127.0.0.1:3001;
}

upstream dashboard {
    server 127.0.0.1:3000;
}

# ============================================
# API - api.trustdevis.com
# ============================================
server {
    listen 80;
    server_name api.trustdevis.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.trustdevis.com;

    # SSL (sera configuré par Certbot)
    ssl_certificate /etc/letsencrypt/live/trustdevis.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trustdevis.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Logs
    access_log /var/log/nginx/trustdevis-api-access.log;
    error_log /var/log/nginx/trustdevis-api-error.log;

    # Body size for uploads
    client_max_body_size 10M;

    location / {
        proxy_pass http://agent_directeur;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }

    # Health check endpoint (no rate limit)
    location /health {
        proxy_pass http://agent_directeur/health;
        limit_req off;
    }
}

# ============================================
# Dashboard - admin.trustdevis.com
# ============================================
server {
    listen 80;
    server_name admin.trustdevis.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name admin.trustdevis.com;

    ssl_certificate /etc/letsencrypt/live/trustdevis.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trustdevis.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    access_log /var/log/nginx/trustdevis-admin-access.log;
    error_log /var/log/nginx/trustdevis-admin-error.log;

    location / {
        proxy_pass http://dashboard;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# ============================================
# Site principal - trustdevis.com
# ============================================
server {
    listen 80;
    server_name trustdevis.com www.trustdevis.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name trustdevis.com www.trustdevis.com;

    ssl_certificate /etc/letsencrypt/live/trustdevis.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trustdevis.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        # Redirection vers le dashboard ou landing page
        proxy_pass http://dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Étape 7: SSL avec Let's Encrypt

```bash
# Créer le répertoire pour certbot
mkdir -p /var/www/certbot

# Obtenir les certificats (remplacer par votre email et domaine)
certbot certonly --webroot \
    -w /var/www/certbot \
    -d trustdevis.com \
    -d www.trustdevis.com \
    -d api.trustdevis.com \
    -d admin.trustdevis.com \
    --email admin@trustdevis.com \
    --agree-tos \
    --non-interactive

# Vérifier le renouvellement automatique
systemctl status certbot.timer

# Test renouvellement
 certbot renew --dry-run
```

### Étape 8: Démarrage des Services

```bash
cd /opt/trustdevis

# Pull des images et build
docker compose pull
docker compose build

# Démarrage
docker compose up -d

# Vérification des logs
docker compose logs -f

# Vérification santé
docker compose ps
```

---

## Commandes Utiles

### Gestion des Services

```bash
# Démarrer
docker compose up -d

# Arrêter
docker compose down

# Redémarrer un service
docker compose restart agent-ocr

# Voir les logs
docker compose logs -f agent-directeur

# Logs de tous les services
docker compose logs -f --tail 100

# Shell dans un container
docker compose exec agent-directeur sh

# Base de données
docker compose exec postgres psql -U trustdevis_user -d trustdevis
```

### Backup et Restore

```bash
# Backup base de données
docker compose exec postgres pg_dump -U trustdevis_user trustdevis > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U trustdevis_user trustdevis < backup_20260309.sql

# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /opt/trustdevis/uploads
```

### Mises à Jour

```bash
cd /opt/trustdevis

# Pull des dernières versions
git pull origin main

# Rebuild et redémarrage
docker compose down
docker compose build --no-cache
docker compose up -d

# Nettoyage
docker system prune -f
```

---

## Monitoring

### Health Checks

```bash
# API
curl https://api.trustdevis.com/health

# Agents individuels (depuis le serveur)
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
curl http://localhost:3004/health
curl http://localhost:3005/health
```

### Métriques Système

```bash
# CPU/Memory
docker stats

# Espace disque
df -h

# Processus
htop
```

---

## Dépannage

### Problèmes Courants

#### Les containers ne démarrent pas

```bash
# Vérifier les logs
docker compose logs agent-directeur

# Vérifier les variables d'environnement
docker compose config

# Rebuild complet
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### Erreur 502 Bad Gateway

```bash
# Vérifier que les services écoutent
netstat -tlnp | grep 300

# Vérifier Nginx
nginx -t
systemctl restart nginx

# Vérifier les logs Nginx
tail -f /var/log/nginx/trustdevis-api-error.log
```

#### Certificat SSL expiré

```bash
# Renouvellement manuel
certbot renew

# Redémarrer Nginx
systemctl restart nginx
```

#### Base de données inaccessible

```bash
# Vérifier PostgreSQL
docker compose ps postgres
docker compose logs postgres

# Reset (ATTENTION: perte de données!)
docker compose down -v
docker compose up -d postgres
```

---

## Sécurité Post-Déploiement

### Checklist

- [ ] Changer tous les mots de passe par défaut
- [ ] Configurer les backups automatiques
- [ ] Activer le monitoring (alertes email/Slack)
- [ ] Configurer log centralization
- [ ] Tester le plan de disaster recovery
- [ ] Documenter les procédures d'urgence

### Backups Automatiques

Ajouter au crontab:

```bash
# Backup quotidien à 2h du matin
0 2 * * * /opt/trustdevis/scripts/backup.sh >> /var/log/trustdevis/backup.log 2>&1

# Script backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/trustdevis/backups"

# Backup DB
docker compose exec -T postgres pg_dump -U trustdevis_user trustdevis > "$BACKUP_DIR/db_$DATE.sql"

# Backup uploads
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /opt/trustdevis/uploads

# Garder seulement 7 jours
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

---

## Support

En cas de problème:

1. Consulter les logs: `docker compose logs -f`
2. Vérifier la santé: `curl https://api.trustdevis.com/health`
3. Redémarrer les services: `docker compose restart`
4. Contacter l'équipe technique

---

*Guide de déploiement TrustDevis - Version 1.0*

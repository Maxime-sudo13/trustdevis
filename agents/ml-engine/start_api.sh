#!/bin/bash
# Démarrage de l'API ML TrustDevis

cd /root/.openclaw/workspace/trustdevis/agents/ml-engine

echo "🚀 Démarrage API ML TrustDevis..."
echo ""

# Vérifier si les modèles existent
if [ ! -f "models/saved/fraud_model.pkl" ]; then
    echo "⚠️  Modèles non trouvés. Entraînement en cours..."
    python3 training/train_all.py
fi

# Démarrer l'API
echo "🌐 Démarrage API sur http://localhost:8000"
echo ""
echo "Endpoints disponibles:"
echo "  - POST /predict/fraud       : Détection fraude"
echo "  - POST /predict/price       : Prédiction prix"
echo "  - POST /recommend/artisans  : Recommandation artisans"
echo "  - GET  /analytics/trends    : Tendances marché"
echo "  - GET  /analytics/alerts    : Alertes anomalies"
echo "  - GET  /health              : Health check"
echo ""

python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000

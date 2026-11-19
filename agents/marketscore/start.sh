#!/bin/bash
# MarketScore Agent Launcher

cd /root/.openclaw/workspace/trustdevis/agents/marketscore

echo "🚀 Démarrage de l'Agent MarketScore..."
echo "📊 Surveillance de la base de données toutes les 5 minutes"
echo "📈 Rapport horaire automatique"
echo ""
echo "Logs: tail -f /root/.openclaw/workspace/trustdevis/agents/marketscore/marketscore.log"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé"
    exit 1
fi

# Lancer l'agent
exec python3 agent.py

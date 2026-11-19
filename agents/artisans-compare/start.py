"""
Script de démarrage rapide pour le service Artisans Compare
"""

import uvicorn
from database import init_db

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données...")
    init_db()
    print("✅ Base de données prête")
    print("🌐 Démarrage du serveur sur http://0.0.0.0:8010")
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)

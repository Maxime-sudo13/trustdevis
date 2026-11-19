# API OLLAMA POUR AGENTS TRUSTDEVIS

## Endpoint

```python
import requests
import json

OLLAMA_URL = "http://localhost:11434"

def ask_ollama(prompt, model="llama3.2", system=None):
    """
    Envoie une requête à Ollama et retourne la réponse.
    
    Args:
        prompt: Le texte à envoyer au modèle
        model: Le modèle à utiliser (défaut: llama3.2)
        system: Instructions système optionnelles
    
    Returns:
        La réponse texte du modèle
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if system:
        payload["system"] = system
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Erreur Ollama: {str(e)}"


def analyze_devis(devis_text, secteur="Bâtiment"):
    """
    Analyse un devis avec le contexte TrustDevis.
    """
    system_prompt = f"""Tu es un expert en analyse de devis pour le secteur {secteur}.
    Tu dois évaluer la cohérence des prix, la qualité du descriptif, et identifier les anomalies.
    Utilise un langage professionnel et factuel."""
    
    prompt = f"""Analyse ce devis et donne-moi:
    1. Un score sur 100
    2. Les points forts
    3. Les points d'attention
    4. Une recommandation
    
    Devis:
    {devis_text}
    """
    
    return ask_ollama(prompt, system=system_prompt)


def compare_prix(prestation, prix_propose, secteur="Bâtiment"):
    """
    Compare un prix avec les normes du marché.
    """
    prompt = f"""Dans le secteur {secteur}, est-ce que {prix_propose}€ pour "{prestation}" est:
    - Dans la norme
    - Cher
    - Très cher
    - Bon marché (suspicieux)
    
    Donne une fourchette de prix normale et une recommandation."""
    
    return ask_ollama(prompt)


# Exemple d'utilisation
if __name__ == "__main__":
    # Test simple
    print("Test Ollama:")
    print(ask_ollama("Quelle est la capitale de la France?"))
    
    # Test analyse devis
    print("\nTest analyse:")
    devis = "Rénovation salle de bain: 12 000€ TTC. Carrelage 45m² à 80€/m², main d'œuvre 4000€"
    print(analyze_devis(devis))

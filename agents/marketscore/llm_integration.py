"""
TrustDevis MarketScore - Intégration LLM (Kimi K2)
"""
import os
import json
from typing import List, Dict, Any, Optional
import httpx
from dataclasses import asdict


KIMI_API_URL = "https://api.moonshot.cn/v1/chat/completions"
KIMI_MODEL = "kimi-k2.5"


class LLMIntegration:
    """Intégration avec l'API Kimi K2 pour génération de justifications."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("KIMI_API_KEY requis")
    
    async def generate_justification(
        self,
        lignes_detail: List[Any],
        score: int,
        delta_pct: float,
        risk_level: str,
        secteur: str
    ) -> List[str]:
        """
        Génère les justifications textuelles pour chaque ligne.
        
        RÈGLE ABSOLUE : Langage probabiliste uniquement
        JAMAIS : "arnaque", "fraude", "escroquerie"
        TOUJOURS : "probabilité de sur-tarification", "écart significatif"
        """
        prompt = self._build_justification_prompt(
            lignes_detail, score, delta_pct, risk_level, secteur
        )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    KIMI_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": KIMI_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": self._get_system_prompt_justification()
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parser la réponse JSON
                return self._parse_justifications(content)
                
        except Exception as e:
            # Fallback : génération locale
            return self._generate_fallback_justifications(lignes_detail)
    
    async def generate_actions(
        self,
        lignes_detail: List[Any],
        score: int,
        risk_level: str,
        secteur: str
    ) -> List[str]:
        """
        Génère les actions recommandées pour le client.
        """
        prompt = self._build_actions_prompt(lignes_detail, score, risk_level, secteur)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    KIMI_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": KIMI_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": self._get_system_prompt_actions()
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.4,
                        "max_tokens": 800
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                return self._parse_actions(content)
                
        except Exception as e:
            return self._generate_fallback_actions(risk_level, score)
    
    def _get_system_prompt_justification(self) -> str:
        """Prompt système pour la génération de justifications."""
        return """Tu es un analyste de devis pour TrustDevis, une plateforme de vérification de devis.

RÈGLES ABSOLUES :
1. Utilise UNIQUEMENT un langage probabiliste
2. JAMAIS les mots : "arnaque", "fraude", "escroquerie", "tromperie", "vol"
3. Utilise : "probabilité de sur-tarification", "écart significatif", "tarif supérieur à la médiane"
4. Sois factuel, neutre et professionnel
5. Chaque justification doit être concise (1 phrase)
6. Format : "categorie: explication"

Exemples corrects :
- "main_oeuvre: Probabilité de sur-tarification de 25% par rapport à la médiane régionale"
- "materiaux: Écart de 15% avec les prix du marché, justifiable si matériaux premium"
- "pieces: Tarif dans la fourchette haute du marché local"

Exemples INTERDITS :
- "Cette ligne semble être une arnaque"
- "Fraude détectée sur les matériaux"
- "Le professionnel essaie de vous tromper"
"""
    
    def _get_system_prompt_actions(self) -> str:
        """Prompt système pour la génération d'actions."""
        return """Tu es un conseiller client pour TrustDevis.

MISSION : Proposer des actions concrètes au client pour vérifier son devis.

RÈGLES :
1. Numérote les actions (1., 2., 3.)
2. Maximum 5 actions
3. Sois pratique et actionable
4. Pas de jugement moral
5. Langage professionnel et rassurant

Exemples :
- "1. Demander un détail des heures de main d'œuvre prévues"
- "2. Vérifier la référence exacte des matériaux proposés"
- "3. Comparer avec un second devis d'un autre professionnel"
"""
    
    def _build_justification_prompt(
        self,
        lignes_detail: List[Any],
        score: int,
        delta_pct: float,
        risk_level: str,
        secteur: str
    ) -> str:
        """Construit le prompt pour les justifications."""
        lignes_str = []
        for ligne in lignes_detail:
            if hasattr(ligne, 'categorie'):
                lignes_str.append(
                    f"- {ligne.categorie}: {ligne.description} | "
                    f"Devis: {ligne.montant_devis}€ | "
                    f"Marché: {ligne.mediane_marche}€ | "
                    f"Delta: {ligne.delta_pct:.1%}"
                )
            else:
                lignes_str.append(str(ligne))
        
        return f"""Analyse ce devis et génère une justification par ligne :

SECTEUR: {secteur}
SCORE GLOBAL: {score}/100
DELTA GLOBAL: {delta_pct}%
NIVEAU DE RISQUE: {risk_level}

LIGNES DU DEVIS:
{chr(10).join(lignes_str)}

Réponds UNIQUEMENT en JSON avec ce format:
{{"justifications": ["categorie: explication", ...]}}
"""
    
    def _build_actions_prompt(
        self,
        lignes_detail: List[Any],
        score: int,
        risk_level: str,
        secteur: str
    ) -> str:
        """Construit le prompt pour les actions."""
        return f"""Propose des actions pour ce devis :

SECTEUR: {secteur}
SCORE: {score}/100
RISQUE: {risk_level}

Réponds UNIQUEMENT en JSON:
{{"actions": ["1. Action...", "2. Action..."]}}
"""
    
    def _parse_justifications(self, content: str) -> List[str]:
        """Parse la réponse JSON du LLM."""
        try:
            # Nettoyer le contenu
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            if "justifications" in data:
                return data["justifications"]
            return [content]
        except:
            # Fallback : parser ligne par ligne
            lines = [l.strip() for l in content.split("\n") if l.strip() and ":" in l]
            return lines[:10]  # Max 10 justifications
    
    def _parse_actions(self, content: str) -> List[str]:
        """Parse la réponse JSON pour les actions."""
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            if "actions" in data:
                return data["actions"]
            return [content]
        except:
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            return lines[:5]
    
    def _generate_fallback_justifications(self, lignes_detail: List[Any]) -> List[str]:
        """Génère des justifications locales si le LLM échoue."""
        justifications = []
        for ligne in lignes_detail:
            if hasattr(ligne, 'categorie'):
                cat = ligne.categorie
                delta = ligne.delta_pct
                
                if delta > 0.30:
                    justifications.append(
                        f"{cat}: Probabilité de sur-tarification de {delta:.0%} "
                        f"par rapport à la médiane régionale"
                    )
                elif delta > 0.15:
                    justifications.append(
                        f"{cat}: Écart de {delta:.0%} avec les prix du marché"
                    )
                elif delta > 0:
                    justifications.append(
                        f"{cat}: Tarif légèrement supérieur à la médiane ({delta:.0%})"
                    )
                else:
                    justifications.append(
                        f"{cat}: Tarif conforme ou inférieur à la médiane du marché"
                    )
        return justifications
    
    def _generate_fallback_actions(self, risk_level: str, score: int) -> List[str]:
        """Génère des actions par défaut."""
        actions = []
        
        if risk_level == "high":
            actions = [
                "1. Demander un détail complet de chaque poste de dépense",
                "2. Comparer avec au moins 2 autres devis du même secteur",
                "3. Vérifier les références exactes des matériaux/pièces",
                "4. Questionner le professionnel sur les écarts de prix importants"
            ]
        elif risk_level == "moderate":
            actions = [
                "1. Demander la répartition détaillée des heures de main d'œuvre",
                "2. Vérifier la qualité des matériaux/pièces proposés",
                "3. Comparer avec un second avis si possible"
            ]
        else:
            actions = [
                "1. Vérifier que toutes les prestations demandées sont bien listées",
                "2. Conserver ce devis comme référence pour comparaison"
            ]
        
        if score < 60:
            actions.insert(0, "1. Faire appel à un expert pour une revue approfondie")
        
        return actions[:5]

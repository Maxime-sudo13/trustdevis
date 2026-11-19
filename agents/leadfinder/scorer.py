"""
Scorer de pertinence pour les leads TrustDevis.
Calcule un score 0-100 basé sur multiple critères.
"""

from typing import Optional
from datetime import datetime, timedelta
from models import Lead, LeadQuality, LeadType, LeadScoreFactors


class LeadScorer:
    """Moteur de scoring des leads"""
    
    # Poids des différents critères (doivent sommer à 100)
    WEIGHTS = {
        'type_travaux': 25,
        'budget': 25,
        'urgence': 20,
        'localisation': 15,
        'contact': 15
    }
    
    # Types de travaux prioritaires (haute valeur)
    HIGH_VALUE_TYPES = [
        LeadType.CONSTRUCTION,
        LeadType.RENOVATION
    ]
    
    # Sous-types à forte valeur ajoutée
    HIGH_VALUE_SUBTYPES = [
        'toiture', 'charpente', 'extension', 'surelevation',
        'renovation_complete', 'construction_neuve', 'piscine',
        'chauffage', 'climatisation', 'isolation'
    ]
    
    def __init__(self):
        self.weights = self.WEIGHTS
    
    def score_lead(self, lead: Lead) -> tuple[int, LeadQuality, LeadScoreFactors]:
        """
        Calcule le score complet d'un lead.
        
        Returns:
            tuple: (score_total, qualité, facteurs_détaillés)
        """
        # Calcul des sous-scores
        type_score = self._score_type_travaux(lead)
        budget_score = self._score_budget(lead)
        urgence_score = self._score_urgence(lead)
        loc_score = self._score_localisation(lead)
        contact_score = self._score_contact(lead)
        
        # Score pondéré final
        total_score = int(
            type_score * self.weights['type_travaux'] / 100 +
            budget_score * self.weights['budget'] / 100 +
            urgence_score * self.weights['urgence'] / 100 +
            loc_score * self.weights['localisation'] / 100 +
            contact_score * self.weights['contact'] / 100
        )
        
        # Classification qualité
        qualite = self._classify_quality(total_score)
        
        factors = LeadScoreFactors(
            type_travaux_score=type_score,
            budget_score=budget_score,
            urgence_score=urgence_score,
            localisation_score=loc_score,
            contact_score=contact_score,
            total_score=total_score
        )
        
        return total_score, qualite, factors
    
    def _score_type_travaux(self, lead: Lead) -> int:
        """Score basé sur le type de travaux (0-100)"""
        score = 50  # Score de base
        
        # Type principal
        if lead.type_travaux in self.HIGH_VALUE_TYPES:
            score += 30
        elif lead.type_travaux == LeadType.INSTALLATION:
            score += 15
        elif lead.type_travaux == LeadType.REPARATION:
            score += 10
        
        # Sous-type
        if lead.sous_type:
            sous_type_lower = lead.sous_type.lower()
            if any(hv in sous_type_lower for hv in self.HIGH_VALUE_SUBTYPES):
                score += 20
        
        return min(100, score)
    
    def _score_budget(self, lead: Lead) -> int:
        """Score basé sur le budget (0-100)"""
        if lead.budget_estime is None:
            return 30  # Budget inconnu = score moyen-faible
        
        budget = lead.budget_estime
        
        if budget >= 100000:
            return 100
        elif budget >= 50000:
            return 90
        elif budget >= 30000:
            return 80
        elif budget >= 15000:
            return 70
        elif budget >= 8000:
            return 60
        elif budget >= 3000:
            return 50
        elif budget >= 1000:
            return 40
        else:
            return 30
    
    def _score_urgence(self, lead: Lead) -> int:
        """Score basé sur l'urgence (0-100)"""
        score = 50
        
        # Analyse texte d'urgence
        if lead.urgence:
            urgence_lower = lead.urgence.lower()
            urgent_keywords = ['urgent', 'immédiat', 'rapidement', 'au plus vite', 
                             'cette semaine', 'ce mois', 'asap', 'pressing']
            if any(kw in urgence_lower for kw in urgent_keywords):
                score += 40
            elif 'mois' in urgence_lower:
                score += 20
        
        # Date souhaitée
        if lead.date_souhaitee:
            days_until = (lead.date_souhaitee - datetime.utcnow()).days
            if days_until <= 7:
                score += 30
            elif days_until <= 30:
                score += 15
            elif days_until <= 90:
                score += 5
        
        return min(100, score)
    
    def _score_localisation(self, lead: Lead) -> int:
        """Score basé sur la qualité de la localisation (0-100)"""
        score = 50
        loc = lead.localisation
        
        # Présence des champs
        if loc.code_postal:
            score += 15
        if loc.ville:
            score += 15
        if loc.departement:
            score += 10
        if loc.region:
            score += 5
        if loc.latitude and loc.longitude:
            score += 5  # Géocodé précisément
        
        return min(100, score)
    
    def _score_contact(self, lead: Lead) -> int:
        """Score basé sur la qualité des infos de contact (0-100)"""
        if not lead.contact:
            return 20
        
        score = 30
        contact = lead.contact
        
        if contact.telephone:
            score += 25
        if contact.email:
            score += 20
        if contact.nom:
            score += 15
        if contact.societe:
            score += 10
        
        return min(100, score)
    
    def _classify_quality(self, score: int) -> LeadQuality:
        """Classifie la qualité selon le score"""
        if score >= 70:
            return LeadQuality.HOT
        elif score >= 40:
            return LeadQuality.WARM
        else:
            return LeadQuality.COLD
    
    def update_lead_score(self, lead: Lead) -> Lead:
        """Met à jour le score et la qualité d'un lead"""
        score, qualite, _ = self.score_lead(lead)
        lead.score = score
        lead.qualite = qualite
        lead.updated_at = datetime.utcnow()
        return lead

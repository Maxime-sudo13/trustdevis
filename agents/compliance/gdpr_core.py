"""
GDPR Core Module - TrustDevis Compliance Agent
Fonctions de gestion RGPD : consentement, export, suppression, traçabilité
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from models import (
    Consent, ConsentType, Treatment, DataAccessLog,
    GDPRExportResponse, GDPRDeleteResponse
)

# Stockage en mémoire (à remplacer par une base de données en production)
_consents_db: Dict[str, List[Consent]] = {}
_treatments_db: Dict[str, Treatment] = {}
_access_logs_db: List[DataAccessLog] = []
_user_data_db: Dict[str, Dict[str, Any]] = {}  # Simulation données utilisateur
_anonymized_users: set = set()

class GDPRCore:
    """Classe principale pour la gestion RGPD"""
    
    def __init__(self):
        self._init_default_treatments()
    
    def _init_default_treatments(self):
        """Initialise les traitements par défaut de TrustDevis"""
        default_treatments = [
            Treatment(
                id="USER_REGISTRATION",
                purpose="Création et gestion du compte utilisateur",
                legal_basis="contract",
                retention="3y_after_deletion",
                recipients=["TrustDevis"],
                description="Stockage des informations de profil et authentification"
            ),
            Treatment(
                id="QUOTE_ANALYSIS",
                purpose="Analyse et vérification de devis",
                legal_basis="contract",
                retention="5y",
                recipients=["TrustDevis", "Prestataires de vérification"],
                description="Traitement des documents de devis pour détection d'anomalies"
            ),
            Treatment(
                id="COMMUNICATION",
                purpose="Communication avec l'utilisateur",
                legal_basis="contract",
                retention="3y",
                recipients=["TrustDevis", "SendGrid (email)"],
                description="Envoi de notifications et mises à jour"
            ),
            Treatment(
                id="MARKETING",
                purpose="Marketing et communications commerciales",
                legal_basis="consent",
                retention="3y_or_until_revocation",
                recipients=["TrustDevis"],
                description="Newsletters, offres promotionnelles (avec consentement)"
            ),
            Treatment(
                id="ANALYTICS",
                purpose="Analyse d'utilisation et amélioration du service",
                legal_basis="consent",
                retention="2y",
                recipients=["TrustDevis", "Google Analytics"],
                description="Statistiques d'utilisation anonymisées"
            ),
            Treatment(
                id="FRAUD_PREVENTION",
                purpose="Prévention de la fraude et sécurité",
                legal_basis="legitimate_interests",
                retention="5y",
                recipients=["TrustDevis"],
                description="Détection d'activités suspectes et sécurisation"
            ),
            Treatment(
                id="LEGAL_COMPLIANCE",
                purpose="Obligations légales et réglementaires",
                legal_basis="legal_obligation",
                retention="10y",
                recipients=["TrustDevis", "Autorités compétentes"],
                description="Conservation pour obligations fiscales et légales"
            )
        ]
        
        for treatment in default_treatments:
            _treatments_db[treatment.id] = treatment
    
    # ==================== CONSENTEMENT ====================
    
    def log_consent(self, user_id: str, consent_type: ConsentType, 
                    ip: str, version: str) -> Consent:
        """Enregistre un nouveau consentement"""
        consent = Consent(
            user_id=user_id,
            type=consent_type,
            date=datetime.utcnow(),
            ip=ip,
            version=version,
            active=True
        )
        
        if user_id not in _consents_db:
            _consents_db[user_id] = []
        
        # Désactiver les anciens consentements du même type
        for c in _consents_db[user_id]:
            if c.type == consent_type:
                c.active = False
        
        _consents_db[user_id].append(consent)
        
        # Logger l'accès
        self.log_data_access(user_id, "consent_given", ip, 
                           f"Type: {consent_type.value}, Version: {version}")
        
        return consent
    
    def revoke_consent(self, user_id: str, consent_type: ConsentType, 
                       ip: str) -> bool:
        """Révoque un consentement"""
        if user_id not in _consents_db:
            return False
        
        revoked = False
        for consent in _consents_db[user_id]:
            if consent.type == consent_type and consent.active:
                consent.active = False
                revoked = True
        
        if revoked:
            self.log_data_access(user_id, "consent_revoked", ip,
                               f"Type: {consent_type.value}")
        
        return revoked
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Vérifie si un utilisateur a donné son consentement"""
        if user_id in _anonymized_users:
            return False
        
        if user_id not in _consents_db:
            return False
        
        for consent in _consents_db[user_id]:
            if consent.type == consent_type and consent.active:
                return True
        
        return False
    
    def get_user_consents(self, user_id: str) -> List[Consent]:
        """Récupère tous les consentements d'un utilisateur"""
        return _consents_db.get(user_id, [])
    
    def verify_consent_before_processing(self, user_id: str, 
                                         consent_type: ConsentType,
                                         raise_exception: bool = True) -> bool:
        """
        Vérifie le consentement avant un traitement.
        Si raise_exception=True, lève une exception si pas de consentement.
        """
        has_consent = self.check_consent(user_id, consent_type)
        
        if not has_consent and raise_exception:
            raise PermissionError(
                f"Consentement requis pour le traitement '{consent_type.value}'. "
                f"Utilisateur: {user_id}"
            )
        
        return has_consent
    
    # ==================== EXPORT RGPD ====================
    
    def export_user_data(self, user_id: str, ip: str) -> GDPRExportResponse:
        """
        Exporte toutes les données personnelles d'un utilisateur (droit à la portabilité)
        """
        if user_id in _anonymized_users:
            raise ValueError(f"Utilisateur {user_id} a été anonymisé")
        
        export_data = {
            "export_metadata": {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "format_version": "1.0",
                "generated_by": "TrustDevis GDPR Export System"
            },
            "consents": [],
            "treatments": [],
            "access_logs": [],
            "user_profile": {},
            "quotes": [],
            "communications": []
        }
        
        # Consentements
        if user_id in _consents_db:
            export_data["consents"] = [
                {
                    "type": c.type.value,
                    "date": c.date.isoformat(),
                    "ip": c.ip,
                    "version": c.version,
                    "active": c.active
                }
                for c in _consents_db[user_id]
            ]
        
        # Traitements applicables
        export_data["treatments"] = [
            {
                "id": t.id,
                "purpose": t.purpose,
                "legal_basis": t.legal_basis.value,
                "retention": t.retention,
                "recipients": t.recipients
            }
            for t in _treatments_db.values()
        ]
        
        # Logs d'accès
        export_data["access_logs"] = [
            {
                "action": log.action,
                "date": log.date.isoformat(),
                "ip": log.ip,
                "details": log.details
            }
            for log in _access_logs_db
            if log.user_id == user_id
        ]
        
        # Données utilisateur (simulation)
        if user_id in _user_data_db:
            export_data["user_profile"] = _user_data_db[user_id]
        
        # Logger l'export
        self.log_data_access(user_id, "data_export", ip, 
                           "Export complet des données personnelles")
        
        return GDPRExportResponse(
            user_id=user_id,
            export_date=datetime.utcnow(),
            data=export_data
        )
    
    # ==================== SUPPRESSION / ANONYMISATION ====================
    
    def delete_user_data(self, user_id: str, ip: str, 
                         reason: Optional[str] = None) -> GDPRDeleteResponse:
        """
        Suppression complète ou anonymisation des données (droit à l'oubli)
        """
        if user_id in _anonymized_users:
            return GDPRDeleteResponse(
                user_id=user_id,
                deleted_at=datetime.utcnow(),
                status="already_anonymized",
                anonymized=True
            )
        
        # Déterminer si on peut supprimer ou doit anonymiser
        # Certains traitements légaux obligatoires nécessitent conservation
        must_anonymize = self._has_legal_retention_obligation(user_id)
        
        if must_anonymize:
            self._anonymize_user_data(user_id)
            status = "anonymized"
        else:
            self._purge_user_data(user_id)
            status = "deleted"
        
        # Logger la suppression
        self.log_data_access(
            user_id, 
            "data_deletion" if status == "deleted" else "data_anonymization",
            ip,
            f"Raison: {reason or 'Demande utilisateur'}"
        )
        
        _anonymized_users.add(user_id)
        
        return GDPRDeleteResponse(
            user_id=user_id,
            deleted_at=datetime.utcnow(),
            status=status,
            anonymized=must_anonymize
        )
    
    def _has_legal_retention_obligation(self, user_id: str) -> bool:
        """Vérifie s'il existe des obligations de conservation légale"""
        # Vérifier si l'utilisateur a des transactions/factures
        user_data = _user_data_db.get(user_id, {})
        has_transactions = user_data.get("has_transactions", False)
        has_legal_proceedings = user_data.get("has_legal_proceedings", False)
        
        return has_transactions or has_legal_proceedings
    
    def _anonymize_user_data(self, user_id: str):
        """Anonymise les données en conservant les traces nécessaires"""
        # Générer un hash unique pour l'anonymisation
        anonymization_id = hashlib.sha256(
            f"{user_id}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Anonymiser le profil
        if user_id in _user_data_db:
            _user_data_db[user_id] = {
                "anonymized": True,
                "anonymization_id": anonymization_id,
                "anonymized_at": datetime.utcnow().isoformat(),
                "retention_reason": "legal_obligation",
                # Conserver uniquement les données nécessaires (montants, dates)
                "transactions_summary": _user_data_db[user_id].get("transactions_summary", {})
            }
        
        # Anonymiser les consentements (garder l'historique sans identifiant)
        if user_id in _consents_db:
            for consent in _consents_db[user_id]:
                consent.user_id = f"ANON_{anonymization_id}"
        
        # Supprimer les logs d'accès personnels
        global _access_logs_db
        _access_logs_db = [
            log for log in _access_logs_db 
            if log.user_id != user_id
        ]
    
    def _purge_user_data(self, user_id: str):
        """Supprime complètement toutes les données"""
        # Supprimer les consentements
        if user_id in _consents_db:
            del _consents_db[user_id]
        
        # Supprimer les données utilisateur
        if user_id in _user_data_db:
            del _user_data_db[user_id]
        
        # Supprimer les logs d'accès
        global _access_logs_db
        _access_logs_db = [
            log for log in _access_logs_db 
            if log.user_id != user_id
        ]
    
    # ==================== LOGS TRAÇABILITÉ ====================
    
    def log_data_access(self, user_id: str, action: str, ip: str,
                        details: Optional[str] = None) -> DataAccessLog:
        """Enregistre un log d'accès aux données"""
        log = DataAccessLog(
            user_id=user_id,
            action=action,
            date=datetime.utcnow(),
            ip=ip,
            details=details
        )
        _access_logs_db.append(log)
        return log
    
    def get_access_logs(self, user_id: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[DataAccessLog]:
        """Récupère les logs d'accès avec filtres optionnels"""
        logs = _access_logs_db
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if start_date:
            logs = [log for log in logs if log.date >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.date <= end_date]
        
        return logs
    
    # ==================== REGISTRE DES TRAITEMENTS ====================
    
    def get_treatments_register(self) -> List[Treatment]:
        """Récupère le registre des traitements"""
        return list(_treatments_db.values())
    
    def add_treatment(self, treatment: Treatment) -> Treatment:
        """Ajoute un nouveau traitement au registre"""
        treatment.created_at = datetime.utcnow()
        treatment.updated_at = datetime.utcnow()
        _treatments_db[treatment.id] = treatment
        return treatment
    
    def update_treatment(self, treatment_id: str, 
                         updates: Dict[str, Any]) -> Optional[Treatment]:
        """Met à jour un traitement existant"""
        if treatment_id not in _treatments_db:
            return None
        
        treatment = _treatments_db[treatment_id]
        for key, value in updates.items():
            if hasattr(treatment, key):
                setattr(treatment, key, value)
        
        treatment.updated_at = datetime.utcnow()
        return treatment
    
    # ==================== UTILITAIRES ====================
    
    def is_user_anonymized(self, user_id: str) -> bool:
        """Vérifie si un utilisateur a été anonymisé"""
        return user_id in _anonymized_users
    
    def get_data_retention_info(self, user_id: str) -> Dict[str, Any]:
        """Retourne les informations de conservation des données"""
        consents = self.get_user_consents(user_id)
        
        return {
            "user_id": user_id,
            "anonymized": user_id in _anonymized_users,
            "total_consents": len(consents),
            "active_consents": len([c for c in consents if c.active]),
            "last_consent_date": max(
                (c.date for c in consents), default=None
            ).isoformat() if consents else None,
            "applicable_treatments": [
                {
                    "id": t.id,
                    "retention": t.retention,
                    "legal_basis": t.legal_basis.value
                }
                for t in _treatments_db.values()
            ]
        }


# Instance singleton
gdpr_core = GDPRCore()

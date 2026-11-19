"""
TrustDevis Compliance Agent - Service FastAPI RGPD
Gestion des consentements, exports et suppressions de données
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional

from models import (
    ConsentCreate, ConsentRevoke, Consent, ConsentType,
    Treatment, TreatmentCreate,
    DataAccessLog, DataAccessLogCreate,
    GDPRExportRequest, GDPRDeleteRequest,
    GDPRExportResponse, GDPRDeleteResponse
)
from gdpr_core import gdpr_core, GDPRCore
from middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    GDPRAuditMiddleware,
    RequestValidationMiddleware,
    CORSConfig,
    APITokenAuth
)

# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print("🚀 TrustDevis Compliance Agent - Démarrage...")
    print(f"📋 Registre des traitements: {len(gdpr_core.get_treatments_register())} traitements")
    yield
    # Shutdown
    print("🛑 Arrêt du service Compliance...")

# ==================== APP INIT ====================

app = FastAPI(
    title="TrustDevis Compliance API",
    description="Service de gestion RGPD et conformité des données personnelles",
    version="1.0.0",
    lifespan=lifespan
)

# Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.add_middleware(GDPRAuditMiddleware, gdpr_core=gdpr_core)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORSConfig.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=CORSConfig.ALLOWED_METHODS,
    allow_headers=CORSConfig.ALLOWED_HEADERS,
    expose_headers=CORSConfig.EXPOSED_HEADERS
)

# Auth
auth = APITokenAuth()

# ==================== HELPERS ====================

def get_client_ip(request: Request) -> str:
    """Récupère l'IP client réelle"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

# ==================== ENDPOINTS SANTÉ ====================

@app.get("/health")
async def health_check():
    """Vérification de santé du service"""
    return {
        "status": "healthy",
        "service": "compliance",
        "version": "1.0.0",
        "gdpr_ready": True
    }

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "service": "TrustDevis Compliance API",
        "version": "1.0.0",
        "endpoints": {
            "consent": "/consent",
            "gdpr": "/gdpr",
            "health": "/health"
        }
    }

# ==================== ENDPOINTS CONSENTEMENTS ====================

@app.post("/consent/log", response_model=dict)
async def log_consent(consent: ConsentCreate, request: Request):
    """
    Enregistre un consentement utilisateur
    
    - **user_id**: Identifiant unique de l'utilisateur
    - **type**: Type de consentement (terms_of_service, marketing, analytics, etc.)
    - **version**: Version des CGU/politique acceptée
    """
    try:
        ip = consent.ip or get_client_ip(request)
        result = gdpr_core.log_consent(
            user_id=consent.user_id,
            consent_type=consent.type,
            ip=ip,
            version=consent.version
        )
        return {
            "success": True,
            "consent": {
                "user_id": result.user_id,
                "type": result.type.value,
                "date": result.date.isoformat(),
                "version": result.version,
                "active": result.active
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consent/revoke")
async def revoke_consent(revoke: ConsentRevoke, request: Request):
    """
    Révoque un consentement utilisateur
    """
    try:
        ip = get_client_ip(request)
        success = gdpr_core.revoke_consent(
            user_id=revoke.user_id,
            consent_type=revoke.type,
            ip=ip
        )
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun consentement actif trouvé pour {revoke.type.value}"
            )
        return {
            "success": True,
            "message": f"Consentement {revoke.type.value} révoqué avec succès"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consent/{user_id}")
async def get_user_consents(user_id: str, request: Request):
    """
    Récupère tous les consentements d'un utilisateur
    """
    try:
        consents = gdpr_core.get_user_consents(user_id)
        
        # Logger l'accès
        ip = get_client_ip(request)
        gdpr_core.log_data_access(user_id, "consent_view", ip)
        
        return {
            "user_id": user_id,
            "consents": [
                {
                    "type": c.type.value,
                    "date": c.date.isoformat(),
                    "ip": c.ip,
                    "version": c.version,
                    "active": c.active
                }
                for c in consents
            ],
            "active_consents": [c.type.value for c in consents if c.active]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consent/{user_id}/check/{consent_type}")
async def check_consent(user_id: str, consent_type: ConsentType, request: Request):
    """
    Vérifie si un utilisateur a donné un consentement spécifique
    """
    try:
        has_consent = gdpr_core.check_consent(user_id, consent_type)
        return {
            "user_id": user_id,
            "consent_type": consent_type.value,
            "has_consent": has_consent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS RGPD ====================

@app.post("/gdpr/export", response_model=dict)
async def export_user_data(export_req: GDPRExportRequest, request: Request):
    """
    Exporte toutes les données personnelles d'un utilisateur (droit à la portabilité)
    
    Retourne un fichier JSON contenant:
    - Les consentements
    - Les logs d'accès
    - Les données de profil
    - Les traitements applicables
    """
    try:
        ip = export_req.ip or get_client_ip(request)
        
        # Vérifier que l'utilisateur existe
        if gdpr_core.is_user_anonymized(export_req.user_id):
            raise HTTPException(
                status_code=404,
                detail="Utilisateur non trouvé ou données anonymisées"
            )
        
        result = gdpr_core.export_user_data(export_req.user_id, ip)
        
        return {
            "success": True,
            "export": {
                "user_id": result.user_id,
                "export_date": result.export_date.isoformat(),
                "data": result.data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gdpr/delete", response_model=dict)
async def delete_user_data(delete_req: GDPRDeleteRequest, request: Request):
    """
    Supprime ou anonymise les données d'un utilisateur (droit à l'oubli)
    
    Si des obligations légales de conservation existent, les données seront
    anonymisées plutôt que supprimées.
    """
    try:
        ip = delete_req.ip or get_client_ip(request)
        
        result = gdpr_core.delete_user_data(
            user_id=delete_req.user_id,
            ip=ip,
            reason=delete_req.reason
        )
        
        return {
            "success": True,
            "deletion": {
                "user_id": result.user_id,
                "deleted_at": result.deleted_at.isoformat(),
                "status": result.status,
                "anonymized": result.anonymized,
                "message": (
                    "Données anonymisées (conservation légale requise)" 
                    if result.anonymized 
                    else "Données supprimées définitivement"
                )
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gdpr/register")
async def get_treatments_register():
    """
    Récupère le registre des traitements (conformité CNIL)
    
    Liste tous les traitements de données personnelles effectués par TrustDevis,
    avec leur base légale, durée de conservation et destinataires.
    """
    try:
        treatments = gdpr_core.get_treatments_register()
        last_updated = max(
            (t.updated_at or t.created_at for t in treatments if t.updated_at or t.created_at),
            default=None
        )
        return {
            "register_version": "1.0",
            "last_updated": last_updated.isoformat() if last_updated else None,
            "organization": "TrustDevis",
            "dpo_contact": "dpo@trustdevis.fr",
            "treatments": [
                {
                    "id": t.id,
                    "purpose": t.purpose,
                    "description": t.description,
                    "legal_basis": t.legal_basis.value,
                    "retention": t.retention,
                    "recipients": t.recipients,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None
                }
                for t in treatments
            ],
            "total_treatments": len(treatments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gdpr/register/{treatment_id}")
async def get_treatment_details(treatment_id: str):
    """
    Récupère les détails d'un traitement spécifique
    """
    try:
        treatments = gdpr_core.get_treatments_register()
        treatment = next((t for t in treatments if t.id == treatment_id), None)
        
        if not treatment:
            raise HTTPException(
                status_code=404,
                detail=f"Traitement {treatment_id} non trouvé"
            )
        
        return {
            "id": treatment.id,
            "purpose": treatment.purpose,
            "description": treatment.description,
            "legal_basis": treatment.legal_basis.value,
            "retention": treatment.retention,
            "recipients": treatment.recipients,
            "created_at": treatment.created_at.isoformat() if treatment.created_at else None,
            "updated_at": treatment.updated_at.isoformat() if treatment.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gdpr/retention/{user_id}")
async def get_data_retention_info(user_id: str, request: Request):
    """
    Récupère les informations de conservation des données d'un utilisateur
    """
    try:
        info = gdpr_core.get_data_retention_info(user_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS ADMIN ====================

@app.get("/admin/logs")
async def get_access_logs(
    user_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Récupère les logs d'accès (admin uniquement)
    """
    try:
        logs = gdpr_core.get_access_logs(user_id=user_id)
        total = len(logs)
        
        # Pagination
        paginated_logs = logs[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "user_id": log.user_id,
                    "action": log.action,
                    "date": log.date.isoformat(),
                    "ip": log.ip,
                    "details": log.details
                }
                for log in paginated_logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/treatments")
async def add_treatment(treatment: TreatmentCreate):
    """
    Ajoute un nouveau traitement au registre (admin uniquement)
    """
    try:
        from models import Treatment
        new_treatment = Treatment(**treatment.dict())
        result = gdpr_core.add_treatment(new_treatment)
        return {
            "success": True,
            "treatment": {
                "id": result.id,
                "purpose": result.purpose,
                "legal_basis": result.legal_basis.value,
                "retention": result.retention
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== POINT D'ENTRÉE ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )

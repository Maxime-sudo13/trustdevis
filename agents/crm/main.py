from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import logging

from models import (
    Client, Devis, Relance, NPS, 
    PlanType, SecteurType, DevisStatus, 
    RelanceType, RelanceStatus,
    get_engine, init_db, get_session
)
from scheduler import create_scheduler

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'app FastAPI
app = FastAPI(
    title="TrustDevis CRM API",
    description="API de gestion clients, relances et feedback",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./crm.db"
engine = get_engine(DATABASE_URL)
init_db(engine)
SessionLocal = get_session(engine)

# Scheduler (démarré au lancement)
scheduler = None

# ==================== PYDANTIC MODELS ====================

class ClientCreate(BaseModel):
    nom: str
    email: EmailStr
    tel: Optional[str] = None
    entreprise: Optional[str] = None
    secteur: SecteurType = SecteurType.AUTRE
    plan: PlanType = PlanType.ESSAI

class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    tel: Optional[str] = None
    entreprise: Optional[str] = None
    secteur: Optional[SecteurType] = None
    plan: Optional[PlanType] = None
    actif: Optional[int] = None

class ClientResponse(BaseModel):
    id: int
    nom: str
    email: str
    tel: Optional[str]
    entreprise: Optional[str]
    secteur: str
    plan: str
    date_inscription: datetime
    date_fin_essai: Optional[datetime]
    date_fin_abonnement: Optional[datetime]
    actif: int
    nb_devis: int = 0
    
    class Config:
        from_attributes = True

class DevisCreate(BaseModel):
    client_id: int
    fichier: str
    fichier_origine: Optional[str] = None

class DevisUpdate(BaseModel):
    score: Optional[float] = None
    status: Optional[DevisStatus] = None
    resultat_analyse: Optional[str] = None
    nb_lignes: Optional[int] = None
    montant_total: Optional[float] = None

class DevisResponse(BaseModel):
    id: int
    client_id: int
    fichier: str
    fichier_origine: Optional[str]
    score: Optional[float]
    date_upload: datetime
    status: str
    nb_lignes: Optional[int]
    montant_total: Optional[float]
    
    class Config:
        from_attributes = True

class RelanceResponse(BaseModel):
    id: int
    client_id: int
    type: str
    sujet: Optional[str]
    date_planification: datetime
    date_envoi: Optional[datetime]
    status: str
    ouvert: int
    clique: int
    
    class Config:
        from_attributes = True

class NPSCreate(BaseModel):
    client_id: int
    score: int
    commentaire: Optional[str] = None

class NPSResponse(BaseModel):
    id: int
    client_id: int
    score: int
    commentaire: Optional[str]
    date: datetime
    
    class Config:
        from_attributes = True

class CampagneCreate(BaseModel):
    nom: str
    type: RelanceType
    date_envoi: datetime
    criteres: Optional[dict] = None

class StatsResponse(BaseModel):
    total_clients: int
    clients_actifs: int
    nouveaux_clients_30j: int
    total_devis: int
    devis_ce_mois: int
    moyenne_score: Optional[float]
    taux_conversion: float
    nps_moyen: Optional[float]

# ==================== DEPENDENCIES ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== CLIENT ENDPOINTS ====================

@app.post("/clients", response_model=ClientResponse, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Crée un nouveau client."""
    # Vérifier email unique
    existing = db.query(Client).filter(Client.email == client.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    db_client = Client(**client.dict())
    
    # Calculer date fin essai (14 jours)
    if db_client.plan == PlanType.ESSAI:
        db_client.date_fin_essai = datetime.utcnow() + timedelta(days=14)
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Ajouter le nombre de devis
    db_client.nb_devis = 0
    
    logger.info(f"✅ Client créé: {db_client.email}")
    return db_client

@app.get("/clients", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    plan: Optional[PlanType] = None,
    secteur: Optional[SecteurType] = None,
    actif: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Liste tous les clients avec filtres optionnels."""
    query = db.query(Client)
    
    if plan:
        query = query.filter(Client.plan == plan)
    if secteur:
        query = query.filter(Client.secteur == secteur)
    if actif is not None:
        query = query.filter(Client.actif == actif)
    if search:
        query = query.filter(
            (Client.nom.ilike(f"%{search}%")) |
            (Client.email.ilike(f"%{search}%")) |
            (Client.entreprise.ilike(f"%{search}%"))
        )
    
    clients = query.offset(skip).limit(limit).all()
    
    # Ajouter le nombre de devis pour chaque client
    for client in clients:
        client.nb_devis = db.query(Devis).filter(Devis.client_id == client.id).count()
    
    return clients

@app.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Récupère un client par son ID."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    client.nb_devis = db.query(Devis).filter(Devis.client_id == client.id).count()
    return client

@app.put("/clients/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    """Met à jour un client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    client.nb_devis = db.query(Devis).filter(Devis.client_id == client.id).count()
    logger.info(f"✅ Client mis à jour: {client.email}")
    return client

@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Supprime un client (soft delete - désactivation)."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    client.actif = 0
    db.commit()
    
    logger.info(f"🗑️ Client désactivé: {client.email}")
    return {"message": "Client désactivé"}

# ==================== DEVIS ENDPOINTS ====================

@app.post("/devis", response_model=DevisResponse, status_code=201)
def create_devis(devis: DevisCreate, db: Session = Depends(get_db)):
    """Crée un nouveau devis pour un client."""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == devis.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    db_devis = Devis(**devis.dict())
    db.add(db_devis)
    db.commit()
    db.refresh(db_devis)
    
    logger.info(f"✅ Devis créé pour client {devis.client_id}")
    return db_devis

@app.get("/devis", response_model=List[DevisResponse])
def list_devis(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    status: Optional[DevisStatus] = None,
    db: Session = Depends(get_db)
):
    """Liste tous les devis avec filtres optionnels."""
    query = db.query(Devis)
    
    if client_id:
        query = query.filter(Devis.client_id == client_id)
    if status:
        query = query.filter(Devis.status == status)
    
    return query.order_by(Devis.date_upload.desc()).offset(skip).limit(limit).all()

@app.get("/clients/{client_id}/devis", response_model=List[DevisResponse])
def get_client_devis(client_id: int, db: Session = Depends(get_db)):
    """Récupère l'historique des devis d'un client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    return db.query(Devis).filter(Devis.client_id == client_id).order_by(Devis.date_upload.desc()).all()

@app.get("/devis/{devis_id}", response_model=DevisResponse)
def get_devis(devis_id: int, db: Session = Depends(get_db)):
    """Récupère un devis par son ID."""
    devis = db.query(Devis).filter(Devis.id == devis_id).first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    return devis

@app.put("/devis/{devis_id}", response_model=DevisResponse)
def update_devis(devis_id: int, devis_update: DevisUpdate, db: Session = Depends(get_db)):
    """Met à jour un devis (résultat d'analyse)."""
    devis = db.query(Devis).filter(Devis.id == devis_id).first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    update_data = devis_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(devis, field, value)
    
    db.commit()
    db.refresh(devis)
    
    logger.info(f"✅ Devis {devis_id} mis à jour - Score: {devis.score}")
    return devis

@app.delete("/devis/{devis_id}", status_code=204)
def delete_devis(devis_id: int, db: Session = Depends(get_db)):
    """Supprime un devis."""
    devis = db.query(Devis).filter(Devis.id == devis_id).first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    db.delete(devis)
    db.commit()
    
    logger.info(f"🗑️ Devis {devis_id} supprimé")
    return {"message": "Devis supprimé"}

# ==================== RELANCES / CAMPAGNES ====================

@app.get("/relances", response_model=List[RelanceResponse])
def list_relances(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    type: Optional[RelanceType] = None,
    status: Optional[RelanceStatus] = None,
    db: Session = Depends(get_db)
):
    """Liste toutes les relances avec filtres."""
    query = db.query(Relance)
    
    if client_id:
        query = query.filter(Relance.client_id == client_id)
    if type:
        query = query.filter(Relance.type == type)
    if status:
        query = query.filter(Relance.status == status)
    
    return query.order_by(Relance.date_planification.desc()).offset(skip).limit(limit).all()

@app.get("/clients/{client_id}/relances", response_model=List[RelanceResponse])
def get_client_relances(client_id: int, db: Session = Depends(get_db)):
    """Récupère l'historique des relances d'un client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    return db.query(Relance).filter(Relance.client_id == client_id).order_by(Relance.date_planification.desc()).all()

@app.post("/campagnes", status_code=201)
def create_campagne(campagne: CampagneCreate, db: Session = Depends(get_db)):
    """Crée une campagne de relance."""
    # Construire la requête selon les critères
    query = db.query(Client).filter(Client.actif == 1)
    
    if campagne.criteres:
        if "plan" in campagne.criteres:
            query = query.filter(Client.plan == campagne.criteres["plan"])
        if "secteur" in campagne.criteres:
            query = query.filter(Client.secteur == campagne.criteres["secteur"])
        if "min_jours_inscription" in campagne.criteres:
            min_date = datetime.utcnow() - timedelta(days=campagne.criteres["min_jours_inscription"])
            query = query.filter(Client.date_inscription <= min_date)
    
    clients = query.all()
    
    # Créer les relances
    relances_creees = 0
    for client in clients:
        relance = Relance(
            client_id=client.id,
            type=campagne.type,
            sujet=campagne.nom,
            date_planification=campagne.date_envoi,
            status=RelanceStatus.PLANIFIE
        )
        db.add(relance)
        relances_creees += 1
    
    db.commit()
    
    logger.info(f"✅ Campagne créée: {campagne.nom} - {relances_creees} relances")
    return {
        "message": "Campagne créée",
        "nom": campagne.nom,
        "relances_creees": relances_creees,
        "date_envoi": campagne.date_envoi
    }

# ==================== NPS / FEEDBACK ====================

@app.post("/nps", response_model=NPSResponse, status_code=201)
def create_nps(nps: NPSCreate, db: Session = Depends(get_db)):
    """Enregistre une réponse NPS."""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == nps.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier que le score est entre 0 et 10
    if nps.score < 0 or nps.score > 10:
        raise HTTPException(status_code=400, detail="Le score doit être entre 0 et 10")
    
    db_nps = NPS(**nps.dict())
    db.add(db_nps)
    db.commit()
    db.refresh(db_nps)
    
    logger.info(f"✅ NPS reçu: client {nps.client_id} - Score {nps.score}")
    return db_nps

@app.get("/nps", response_model=List[NPSResponse])
def list_nps(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Liste toutes les réponses NPS."""
    query = db.query(NPS)
    
    if client_id:
        query = query.filter(NPS.client_id == client_id)
    
    return query.order_by(NPS.date.desc()).offset(skip).limit(limit).all()

@app.get("/nps/stats")
def get_nps_stats(db: Session = Depends(get_db)):
    """Récupère les statistiques NPS."""
    total = db.query(NPS).count()
    
    if total == 0:
        return {
            "total_reponses": 0,
            "nps_score": None,
            "promoteurs": 0,
            "passifs": 0,
            "detracteurs": 0
        }
    
    promoteurs = db.query(NPS).filter(NPS.score >= 9).count()
    passifs = db.query(NPS).filter(NPS.score >= 7, NPS.score <= 8).count()
    detracteurs = db.query(NPS).filter(NPS.score <= 6).count()
    
    nps_score = ((promoteurs - detracteurs) / total) * 100
    
    return {
        "total_reponses": total,
        "nps_score": round(nps_score, 1),
        "promoteurs": promoteurs,
        "passifs": passifs,
        "detracteurs": detracteurs
    }

# ==================== STATS GLOBALES ====================

@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Récupère les statistiques globales du CRM."""
    now = datetime.utcnow()
    
    # Clients
    total_clients = db.query(Client).count()
    clients_actifs = db.query(Client).filter(Client.actif == 1).count()
    
    # Nouveaux clients sur 30 jours
    date_30j = now - timedelta(days=30)
    nouveaux_clients_30j = db.query(Client).filter(Client.date_inscription >= date_30j).count()
    
    # Devis
    total_devis = db.query(Devis).count()
    debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    devis_ce_mois = db.query(Devis).filter(Devis.date_upload >= debut_mois).count()
    
    # Score moyen
    moyenne_score = db.query(func.avg(Devis.score)).filter(Devis.score != None).scalar()
    
    # Taux de conversion (clients avec au moins 1 devis / total clients)
    clients_avec_devis = db.query(Devis.client_id).distinct().count()
    taux_conversion = (clients_avec_devis / total_clients * 100) if total_clients > 0 else 0
    
    # NPS moyen
    nps_moyen = db.query(func.avg(NPS.score)).scalar()
    
    return StatsResponse(
        total_clients=total_clients,
        clients_actifs=clients_actifs,
        nouveaux_clients_30j=nouveaux_clients_30j,
        total_devis=total_devis,
        devis_ce_mois=devis_ce_mois,
        moyenne_score=round(moyenne_score, 1) if moyenne_score else None,
        taux_conversion=round(taux_conversion, 1),
        nps_moyen=round(nps_moyen, 1) if nps_moyen else None
    )

# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    """Vérifie l'état du service."""
    return {
        "status": "ok",
        "service": "crm",
        "timestamp": datetime.utcnow().isoformat()
    }

# ==================== LIFECYCLE EVENTS ====================

@app.on_event("startup")
def startup_event():
    """Démarrage du service."""
    global scheduler
    scheduler = create_scheduler(SessionLocal)
    scheduler.start()
    logger.info("🚀 CRM Service démarré")

@app.on_event("shutdown")
def shutdown_event():
    """Arrêt du service."""
    global scheduler
    if scheduler:
        scheduler.stop()
    logger.info("🛑 CRM Service arrêté")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

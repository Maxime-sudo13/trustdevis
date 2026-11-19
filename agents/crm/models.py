from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class PlanType(str, enum.Enum):
    ESSAI = "essai"
    BASIQUE = "basique"
    PRO = "pro"
    ENTREPRISE = "entreprise"

class SecteurType(str, enum.Enum):
    BATIMENT = "batiment"
    MECANIQUE = "mecanique"
    AUTRE = "autre"

class DevisStatus(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    ANALYSE = "analyse"
    TERMINE = "termine"
    ERREUR = "erreur"

class RelanceType(str, enum.Enum):
    ONBOARDING_J1 = "onboarding_j1"
    ONBOARDING_J3 = "onboarding_j3"
    ONBOARDING_J7 = "onboarding_j7"
    CONVERSION = "conversion"
    NPS = "nps"
    RENOUVELLEMENT = "renouvellement"

class RelanceStatus(str, enum.Enum):
    PLANIFIE = "planifie"
    ENVOYE = "envoye"
    OUVERT = "ouvert"
    CLIQUE = "clique"
    ERREUR = "erreur"

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    tel = Column(String(20), nullable=True)
    entreprise = Column(String(100), nullable=True)
    secteur = Column(Enum(SecteurType), default=SecteurType.AUTRE)
    plan = Column(Enum(PlanType), default=PlanType.ESSAI)
    date_inscription = Column(DateTime, default=datetime.utcnow)
    date_fin_essai = Column(DateTime, nullable=True)
    date_fin_abonnement = Column(DateTime, nullable=True)
    actif = Column(Integer, default=1)
    
    devis = relationship("Devis", back_populates="client", cascade="all, delete-orphan")
    relances = relationship("Relance", back_populates="client", cascade="all, delete-orphan")
    nps = relationship("NPS", back_populates="client", cascade="all, delete-orphan")

class Devis(Base):
    __tablename__ = "devis"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    fichier = Column(String(255), nullable=False)
    fichier_origine = Column(String(255), nullable=True)
    score = Column(Float, nullable=True)
    date_upload = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(DevisStatus), default=DevisStatus.EN_ATTENTE)
    resultat_analyse = Column(Text, nullable=True)
    nb_lignes = Column(Integer, nullable=True)
    montant_total = Column(Float, nullable=True)
    
    client = relationship("Client", back_populates="devis")

class Relance(Base):
    __tablename__ = "relances"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    type = Column(Enum(RelanceType), nullable=False)
    date_envoi = Column(DateTime, nullable=True)
    date_planification = Column(DateTime, nullable=False)
    status = Column(Enum(RelanceStatus), default=RelanceStatus.PLANIFIE)
    contenu = Column(Text, nullable=True)
    sujet = Column(String(200), nullable=True)
    ouvert = Column(Integer, default=0)
    clique = Column(Integer, default=0)
    
    client = relationship("Client", back_populates="relances")

class NPS(Base):
    __tablename__ = "nps"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    score = Column(Integer, nullable=False)
    commentaire = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("Client", back_populates="nps")

# Database setup
def get_engine(database_url="sqlite:///./crm.db"):
    return create_engine(database_url)

def init_db(engine):
    Base.metadata.create_all(bind=engine)

def get_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

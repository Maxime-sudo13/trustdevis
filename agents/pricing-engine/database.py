from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import numpy as np
from typing import List, Optional, Dict, Any

Base = declarative_base()

# Database configuration - SQLite pour dev, PostgreSQL pour prod
DATABASE_URL = "sqlite:///./pricing.db"
# Pour PostgreSQL en production:
# DATABASE_URL = "postgresql://user:password@localhost/trustdevis_pricing"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Region(Base):
    """Table des régions avec coefficient main d'œuvre"""
    __tablename__ = "regions"
    
    code = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    labor_coefficient = Column(Float, default=1.0)  # Coefficient main d'œuvre régional


class Price(Base):
    """Table des prix par catégorie et région"""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    region_code = Column(String(10), ForeignKey("regions.code"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # m², heure, forfait, etc.
    source = Column(String(100), nullable=True)  # Origine du prix (artisan_X, dataset_Y)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency pour obtenir une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialise la base de données"""
    Base.metadata.create_all(bind=engine)


def get_region(db: Session, region_code: str) -> Optional[Region]:
    """Récupère une région par son code"""
    return db.query(Region).filter(Region.code == region_code.upper()).first()


def get_prices_by_category_region(db: Session, category: str, region_code: str) -> List[Price]:
    """Récupère tous les prix pour une catégorie et région"""
    return db.query(Price).filter(
        Price.category == category.lower(),
        Price.region_code == region_code.upper()
    ).all()


def add_price(db: Session, category: str, region_code: str, price: float, unit: str, source: str = None) -> Price:
    """Ajoute un nouveau prix"""
    db_price = Price(
        category=category.lower(),
        region_code=region_code.upper(),
        price=price,
        unit=unit.lower(),
        source=source
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


def get_categories(db: Session) -> List[str]:
    """Récupère la liste des catégories uniques"""
    result = db.query(Price.category).distinct().all()
    return [r[0] for r in result]


def get_regions(db: Session) -> List[Region]:
    """Récupère toutes les régions"""
    return db.query(Region).all()


def get_price_stats(db: Session, category: str = None, region_code: str = None) -> Dict[str, Any]:
    """Récupère les statistiques de prix avec médiane et percentiles"""
    query = db.query(Price)
    
    if category:
        query = query.filter(Price.category == category.lower())
    if region_code:
        query = query.filter(Price.region_code == region_code.upper())
    
    prices = [p.price for p in query.all()]
    
    if not prices:
        return None
    
    prices_array = np.array(prices)
    
    return {
        "count": len(prices),
        "median": float(np.median(prices_array)),
        "percentile_25": float(np.percentile(prices_array, 25)),
        "percentile_75": float(np.percentile(prices_array, 75)),
        "percentile_90": float(np.percentile(prices_array, 90)),
        "min": float(np.min(prices_array)),
        "max": float(np.max(prices_array)),
        "mean": float(np.mean(prices_array)),
        "std": float(np.std(prices_array))
    }


def get_global_stats(db: Session) -> Dict[str, Any]:
    """Récupère les statistiques globales"""
    total_prices = db.query(Price).count()
    total_categories = db.query(Price.category).distinct().count()
    total_regions = db.query(Price.region_code).distinct().count()
    
    # Dernière mise à jour
    last_update = db.query(Price).order_by(desc(Price.created_at)).first()
    
    # Répartition par catégorie
    category_counts = db.query(
        Price.category, 
        func.count(Price.id).label('count')
    ).group_by(Price.category).all()
    
    # Répartition par région
    region_counts = db.query(
        Price.region_code, 
        func.count(Price.id).label('count')
    ).group_by(Price.region_code).all()
    
    return {
        "total_prices": total_prices,
        "total_categories": total_categories,
        "total_regions": total_regions,
        "last_update": last_update.created_at.isoformat() if last_update else None,
        "categories": {cat: count for cat, count in category_counts},
        "regions": {reg: count for reg, count in region_counts}
    }

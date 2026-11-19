"""
Base de données SQLite pour les artisans
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from models import Artisan, Review, Badge

DB_PATH = "artisans.db"


def init_db():
    """Initialiser la base de données avec données de démo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table artisans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artisans (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            company_name TEXT,
            specialty TEXT NOT NULL,
            sub_specialties TEXT,
            city TEXT NOT NULL,
            postal_code TEXT,
            region TEXT,
            service_radius_km INTEGER DEFAULT 30,
            phone TEXT,
            email TEXT,
            website TEXT,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            badges TEXT,
            transparency_score INTEGER DEFAULT 0,
            available INTEGER DEFAULT 1,
            next_available_date TEXT,
            average_daily_rate REAL,
            min_project_amount REAL,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Table reviews
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            artisan_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            rating REAL NOT NULL,
            title TEXT,
            comment TEXT NOT NULL,
            project_type TEXT,
            project_amount REAL,
            verified INTEGER DEFAULT 0,
            created_at TEXT,
            quality_rating REAL,
            punctuality_rating REAL,
            communication_rating REAL,
            value_rating REAL,
            FOREIGN KEY (artisan_id) REFERENCES artisans(id)
        )
    """)
    
    conn.commit()
    
    # Insérer données de démo si vide
    cursor.execute("SELECT COUNT(*) FROM artisans")
    if cursor.fetchone()[0] == 0:
        insert_demo_data(cursor)
        conn.commit()
    
    conn.close()


def insert_demo_data(cursor):
    """Insérer des artisans de démo"""
    
    artisans_data = [
        {
            "id": "art_001",
            "name": "Jean Dupont",
            "company_name": "Dupont Plomberie",
            "specialty": "plomberie",
            "sub_specialties": json.dumps(["chauffe-eau", "robinetterie", "fuite"]),
            "city": "Lyon",
            "postal_code": "69001",
            "region": "Auvergne-Rhône-Alpes",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.8,
            "review_count": 127,
            "badges": json.dumps(["trustdevis_verified", "transparency_excellent", "quality_gold", "insured"]),
            "transparency_score": 94,
            "available": 1,
            "next_available_date": "2026-03-12",
            "average_daily_rate": 450,
            "min_project_amount": 150,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_002",
            "name": "Marie Martin",
            "company_name": "Martin Électricité",
            "specialty": "electricite",
            "sub_specialties": json.dumps(["installation", "dépannage", "mise_aux_normes"]),
            "city": "Lyon",
            "postal_code": "69002",
            "region": "Auvergne-Rhône-Alpes",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.6,
            "review_count": 89,
            "badges": json.dumps(["trustdevis_verified", "certified", "insured"]),
            "transparency_score": 87,
            "available": 1,
            "next_available_date": "2026-03-10",
            "average_daily_rate": 420,
            "min_project_amount": 120,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_003",
            "name": "Pierre Bernard",
            "company_name": "Bernard Maçonnerie",
            "specialty": "maconnerie",
            "sub_specialties": json.dumps(["mur", "parpaing", "enduit"]),
            "city": "Lyon",
            "postal_code": "69003",
            "region": "Auvergne-Rhône-Alpes",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.9,
            "review_count": 203,
            "badges": json.dumps(["trustdevis_verified", "transparency_excellent", "quality_gold", "punctuality", "insured", "certified"]),
            "transparency_score": 96,
            "available": 1,
            "next_available_date": "2026-03-15",
            "average_daily_rate": 380,
            "min_project_amount": 500,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_004",
            "name": "Sophie Petit",
            "company_name": "Petit Peinture",
            "specialty": "peinture",
            "sub_specialties": json.dumps(["intérieur", "extérieur", "papier_peint"]),
            "city": "Paris",
            "postal_code": "75011",
            "region": "Île-de-France",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.7,
            "review_count": 156,
            "badges": json.dumps(["trustdevis_verified", "quality_gold", "responsive"]),
            "transparency_score": 91,
            "available": 1,
            "next_available_date": "2026-03-11",
            "average_daily_rate": 350,
            "min_project_amount": 300,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_005",
            "name": "Lucas Moreau",
            "company_name": "Moreau Toiture",
            "specialty": "couverture",
            "sub_specialties": json.dumps(["tuile", "ardoise", "zinc", "gouttière"]),
            "city": "Paris",
            "postal_code": "75012",
            "region": "Île-de-France",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.5,
            "review_count": 78,
            "badges": json.dumps(["trustdevis_verified", "insured", "certified"]),
            "transparency_score": 82,
            "available": 0,
            "next_available_date": "2026-03-20",
            "average_daily_rate": 480,
            "min_project_amount": 800,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_006",
            "name": "Emma Richard",
            "company_name": "Richard Menuiserie",
            "specialty": "menuiserie",
            "sub_specialties": json.dumps(["porte", "fenêtre", "escalier", "meuble"]),
            "city": "Bordeaux",
            "postal_code": "33000",
            "region": "Nouvelle-Aquitaine",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.9,
            "review_count": 112,
            "badges": json.dumps(["trustdevis_verified", "transparency_excellent", "quality_gold", "punctuality", "responsive"]),
            "transparency_score": 95,
            "available": 1,
            "next_available_date": "2026-03-13",
            "average_daily_rate": 400,
            "min_project_amount": 400,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_007",
            "name": "Thomas Roux",
            "company_name": "Roux Chauffage",
            "specialty": "chauffage",
            "sub_specialties": json.dumps(["chaudière", "pompe_à_chaleur", "plancher_chauffant"]),
            "city": "Lyon",
            "postal_code": "69004",
            "region": "Auvergne-Rhône-Alpes",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.4,
            "review_count": 67,
            "badges": json.dumps(["trustdevis_verified", "certified", "insured"]),
            "transparency_score": 79,
            "available": 1,
            "next_available_date": "2026-03-10",
            "average_daily_rate": 500,
            "min_project_amount": 600,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "art_008",
            "name": "Camille Dubois",
            "company_name": "Dubois Carrelage",
            "specialty": "carrelage",
            "sub_specialties": json.dumps(["sol", "mur", "salle_de_bain", "terrasse"]),
            "city": "Marseille",
            "postal_code": "13001",
            "region": "Provence-Alpes-Côte d'Azur",
            "service_radius_km": 30,
            "phone": None,
            "email": None,
            "website": None,
            "rating": 4.7,
            "review_count": 94,
            "badges": json.dumps(["trustdevis_verified", "quality_gold", "insured"]),
            "transparency_score": 88,
            "available": 1,
            "next_available_date": "2026-03-14",
            "average_daily_rate": 360,
            "min_project_amount": 400,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
    ]
    
    for artisan in artisans_data:
        cursor.execute("""
            INSERT INTO artisans VALUES (
                :id, :name, :company_name, :specialty, :sub_specialties,
                :city, :postal_code, :region, :service_radius_km,
                :phone, :email, :website, :rating, :review_count,
                :badges, :transparency_score, :available, :next_available_date,
                :average_daily_rate, :min_project_amount, :created_at, :updated_at
            )
        """, artisan)
    
    # Insérer des avis de démo
    reviews_data = [
        {
            "id": "rev_001",
            "artisan_id": "art_001",
            "client_name": "Marie L.",
            "rating": 5.0,
            "title": "Excellent travail",
            "comment": "Jean a réparé une fuite en urgence. Très professionnel, prix correct. Je recommande !",
            "project_type": "plomberie",
            "project_amount": 180,
            "verified": 1,
            "created_at": "2026-02-15T10:30:00",
            "quality_rating": 5.0,
            "punctuality_rating": 5.0,
            "communication_rating": 5.0,
            "value_rating": 4.5
        },
        {
            "id": "rev_002",
            "artisan_id": "art_001",
            "client_name": "Pierre D.",
            "rating": 4.5,
            "title": "Bonne expérience",
            "comment": "Installation d'un nouveau chauffe-eau. Travail propre et rapide.",
            "project_type": "plomberie",
            "project_amount": 850,
            "verified": 1,
            "created_at": "2026-01-20T14:00:00",
            "quality_rating": 5.0,
            "punctuality_rating": 4.0,
            "communication_rating": 5.0,
            "value_rating": 4.0
        },
        {
            "id": "rev_003",
            "artisan_id": "art_002",
            "client_name": "Sophie M.",
            "rating": 5.0,
            "title": "Très satisfaite",
            "comment": "Mise aux normes complète de l'installation électrique. Marie a tout expliqué clairement.",
            "project_type": "electricite",
            "project_amount": 3200,
            "verified": 1,
            "created_at": "2026-02-10T09:15:00",
            "quality_rating": 5.0,
            "punctuality_rating": 5.0,
            "communication_rating": 5.0,
            "value_rating": 4.5
        },
        {
            "id": "rev_004",
            "artisan_id": "art_003",
            "client_name": "Lucas B.",
            "rating": 5.0,
            "title": "Artisan d'exception",
            "comment": "Construction d'un mur de clôture. Travail impeccable, respect des délais.",
            "project_type": "maconnerie",
            "project_amount": 4500,
            "verified": 1,
            "created_at": "2026-02-28T16:30:00",
            "quality_rating": 5.0,
            "punctuality_rating": 5.0,
            "communication_rating": 5.0,
            "value_rating": 5.0
        },
        {
            "id": "rev_005",
            "artisan_id": "art_004",
            "client_name": "Emma R.",
            "rating": 4.5,
            "title": "Peinture salon et chambres",
            "comment": "Bon rapport qualité-prix. Sophie est méticuleuse et soignée.",
            "project_type": "peinture",
            "project_amount": 1200,
            "verified": 1,
            "created_at": "2026-02-05T11:00:00",
            "quality_rating": 5.0,
            "punctuality_rating": 4.0,
            "communication_rating": 5.0,
            "value_rating": 4.5
        },
    ]
    
    for review in reviews_data:
        cursor.execute("""
            INSERT INTO reviews VALUES (
                :id, :artisan_id, :client_name, :rating, :title, :comment,
                :project_type, :project_amount, :verified, :created_at,
                :quality_rating, :punctuality_rating, :communication_rating, :value_rating
            )
        """, review)


def get_artisans(limit: int = 100, offset: int = 0) -> List[Artisan]:
    """Récupérer tous les artisans"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM artisans LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_artisan(row) for row in rows]


def get_artisan_by_id(artisan_id: str) -> Optional[Artisan]:
    """Récupérer un artisan par ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM artisans WHERE id = ?", (artisan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row_to_artisan(row)
    return None


def search_artisans(
    query: Optional[str] = None,
    specialty: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    available: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Artisan]:
    """Rechercher des artisans avec filtres"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM artisans WHERE 1=1"
    params = []
    
    if specialty:
        sql += " AND specialty = ?"
        params.append(specialty)
    
    if location:
        sql += " AND (city LIKE ? OR postal_code LIKE ? OR region LIKE ?)"
        params.extend([f"%{location}%", f"%{location}%", f"%{location}%"])
    
    if min_rating is not None:
        sql += " AND rating >= ?"
        params.append(min_rating)
    
    if available is not None:
        sql += " AND available = ?"
        params.append(1 if available else 0)
    
    if query:
        sql += " AND (name LIKE ? OR company_name LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    sql += " ORDER BY rating DESC, review_count DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_artisan(row) for row in rows]


def get_reviews(artisan_id: str, limit: int = 10, offset: int = 0) -> List[Review]:
    """Récupérer les avis d'un artisan"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM reviews WHERE artisan_id = ? 
           ORDER BY created_at DESC LIMIT ? OFFSET ?""",
        (artisan_id, limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_review(row) for row in rows]


def row_to_artisan(row: sqlite3.Row) -> Artisan:
    """Convertir une ligne SQL en objet Artisan"""
    badges = json.loads(row["badges"]) if row["badges"] else []
    sub_specialties = json.loads(row["sub_specialties"]) if row["sub_specialties"] else []
    
    return Artisan(
        id=row["id"],
        name=row["name"],
        company_name=row["company_name"],
        specialty=row["specialty"],
        sub_specialties=sub_specialties,
        city=row["city"],
        postal_code=row["postal_code"],
        region=row["region"],
        service_radius_km=row["service_radius_km"],
        phone=row["phone"],
        email=row["email"],
        website=row["website"],
        rating=row["rating"],
        review_count=row["review_count"],
        badges=[Badge(b) for b in badges],
        transparency_score=row["transparency_score"],
        available=bool(row["available"]),
        next_available_date=row["next_available_date"],
        average_daily_rate=row["average_daily_rate"],
        min_project_amount=row["min_project_amount"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


def row_to_review(row: sqlite3.Row) -> Review:
    """Convertir une ligne SQL en objet Review"""
    return Review(
        id=row["id"],
        artisan_id=row["artisan_id"],
        client_name=row["client_name"],
        rating=row["rating"],
        title=row["title"],
        comment=row["comment"],
        project_type=row["project_type"],
        project_amount=row["project_amount"],
        verified=bool(row["verified"]),
        created_at=row["created_at"],
        quality_rating=row["quality_rating"],
        punctuality_rating=row["punctuality_rating"],
        communication_rating=row["communication_rating"],
        value_rating=row["value_rating"]
    )

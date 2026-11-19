from database import SessionLocal, init_db, Region, Price


def seed_regions():
    """Initialise les régions avec leurs coefficients main d'œuvre"""
    regions = [
        # Région, Nom, Coefficient main d'œuvre (1.0 = moyenne nationale)
        ("IDF", "Île-de-France", 1.35),
        ("PACA", "Provence-Alpes-Côte d'Azur", 1.20),
        ("ARA", "Auvergne-Rhône-Alpes", 1.10),
        ("NAQ", "Nouvelle-Aquitaine", 1.00),
        ("OCC", "Occitanie", 0.95),
        ("HDF", "Hauts-de-France", 0.90),
        ("BRE", "Bretagne", 0.95),
        ("PDL", "Pays de la Loire", 0.95),
        ("NOR", "Normandie", 0.90),
        ("GES", "Grand Est", 0.90),
        ("CVL", "Centre-Val de Loire", 0.90),
        ("BFC", "Bourgogne-Franche-Comté", 0.85),
    ]
    
    db = SessionLocal()
    try:
        # Vérifie si les régions existent déjà
        existing = db.query(Region).count()
        if existing > 0:
            print(f"✓ {existing} régions déjà initialisées")
            return
        
        for code, name, coeff in regions:
            region = Region(code=code, name=name, labor_coefficient=coeff)
            db.add(region)
        
        db.commit()
        print(f"✓ {len(regions)} régions initialisées")
    finally:
        db.close()


def seed_building_prices():
    """Données de prix pour le bâtiment (tarifs moyens France 2024)"""
    
    # Prix de base (moyenne nationale), ajustés par région via coefficient
    building_data = [
        # PEINTURE - Prix au m²
        ("peinture", "IDF", 42.00, "m²", "dataset_batiment_2024"),
        ("peinture", "IDF", 38.50, "m²", "artisan_paris_001"),
        ("peinture", "IDF", 45.00, "m²", "artisan_paris_002"),
        ("peinture", "IDF", 40.00, "m²", "artisan_paris_003"),
        ("peinture", "IDF", 35.00, "m²", "dataset_batiment_2024"),
        ("peinture", "PACA", 38.00, "m²", "dataset_batiment_2024"),
        ("peinture", "PACA", 42.00, "m²", "artisan_marseille_001"),
        ("peinture", "PACA", 36.00, "m²", "artisan_nice_001"),
        ("peinture", "ARA", 32.00, "m²", "dataset_batiment_2024"),
        ("peinture", "ARA", 35.00, "m²", "artisan_lyon_001"),
        ("peinture", "ARA", 30.00, "m²", "artisan_lyon_002"),
        ("peinture", "NAQ", 28.00, "m²", "dataset_batiment_2024"),
        ("peinture", "NAQ", 32.00, "m²", "artisan_bordeaux_001"),
        ("peinture", "OCC", 27.00, "m²", "dataset_batiment_2024"),
        ("peinture", "HDF", 25.00, "m²", "dataset_batiment_2024"),
        ("peinture", "BRE", 26.00, "m²", "dataset_batiment_2024"),
        ("peinture", "PDL", 26.00, "m²", "dataset_batiment_2024"),
        ("peinture", "NOR", 24.00, "m²", "dataset_batiment_2024"),
        ("peinture", "GES", 24.00, "m²", "dataset_batiment_2024"),
        ("peinture", "CVL", 24.00, "m²", "dataset_batiment_2024"),
        ("peinture", "BFC", 22.00, "m²", "dataset_batiment_2024"),
        
        # PLOMBERIE - Prix horaire
        ("plomberie", "IDF", 65.00, "heure", "dataset_batiment_2024"),
        ("plomberie", "IDF", 70.00, "heure", "artisan_paris_001"),
        ("plomberie", "IDF", 60.00, "heure", "artisan_paris_002"),
        ("plomberie", "PACA", 58.00, "heure", "dataset_batiment_2024"),
        ("plomberie", "PACA", 62.00, "heure", "artisan_marseille_001"),
        ("plomberie", "ARA", 52.00, "heure", "dataset_batiment_2024"),
        ("plomberie", "ARA", 55.00, "heure", "artisan_lyon_001"),
        ("plomberie", "NAQ", 48.00, "heure", "dataset_batiment_2024"),
        ("plomberie", "OCC", 45.00, "heure", "dataset_batiment_2024"),
        ("plomberie", "HDF", 42.00, "heure", "dataset_batiment_2024"),
        ("plomberie", "BRE", 44.00, "heure", "dataset_batiment_2024"),
        
        # Remplacement WC complet - Prix forfaitaire
        ("remplacement_wc", "IDF", 450.00, "forfait", "dataset_batiment_2024"),
        ("remplacement_wc", "IDF", 500.00, "forfait", "artisan_paris_001"),
        ("remplacement_wc", "IDF", 400.00, "forfait", "artisan_paris_002"),
        ("remplacement_wc", "PACA", 400.00, "forfait", "dataset_batiment_2024"),
        ("remplacement_wc", "ARA", 350.00, "forfait", "dataset_batiment_2024"),
        ("remplacement_wc", "NAQ", 320.00, "forfait", "dataset_batiment_2024"),
        ("remplacement_wc", "OCC", 300.00, "forfait", "dataset_batiment_2024"),
        ("remplacement_wc", "HDF", 280.00, "forfait", "dataset_batiment_2024"),
        
        # TOITURE - Prix au m²
        ("toiture", "IDF", 85.00, "m²", "dataset_batiment_2024"),
        ("toiture", "IDF", 95.00, "m²", "artisan_paris_001"),
        ("toiture", "IDF", 80.00, "m²", "artisan_paris_002"),
        ("toiture", "PACA", 78.00, "m²", "dataset_batiment_2024"),
        ("toiture", "PACA", 85.00, "m²", "artisan_marseille_001"),
        ("toiture", "ARA", 70.00, "m²", "dataset_batiment_2024"),
        ("toiture", "NAQ", 65.00, "m²", "dataset_batiment_2024"),
        ("toiture", "OCC", 62.00, "m²", "dataset_batiment_2024"),
        ("toiture", "HDF", 58.00, "m²", "dataset_batiment_2024"),
        
        # ÉLECTRICITÉ - Prix horaire
        ("electricite", "IDF", 58.00, "heure", "dataset_batiment_2024"),
        ("electricite", "IDF", 65.00, "heure", "artisan_paris_001"),
        ("electricite", "IDF", 55.00, "heure", "artisan_paris_002"),
        ("electricite", "PACA", 52.00, "heure", "dataset_batiment_2024"),
        ("electricite", "ARA", 48.00, "heure", "dataset_batiment_2024"),
        ("electricite", "NAQ", 45.00, "heure", "dataset_batiment_2024"),
        ("electricite", "OCC", 42.00, "heure", "dataset_batiment_2024"),
        ("electricite", "HDF", 40.00, "heure", "dataset_batiment_2024"),
        
        # Installation prise électrique - Prix forfaitaire
        ("installation_prise", "IDF", 85.00, "forfait", "dataset_batiment_2024"),
        ("installation_prise", "IDF", 95.00, "forfait", "artisan_paris_001"),
        ("installation_prise", "IDF", 75.00, "forfait", "artisan_paris_002"),
        ("installation_prise", "PACA", 78.00, "forfait", "dataset_batiment_2024"),
        ("installation_prise", "ARA", 70.00, "forfait", "dataset_batiment_2024"),
        ("installation_prise", "NAQ", 65.00, "forfait", "dataset_batiment_2024"),
        ("installation_prise", "OCC", 62.00, "forfait", "dataset_batiment_2024"),
        ("installation_prise", "HDF", 58.00, "forfait", "dataset_batiment_2024"),
        
        # CHAUFFAGE - Installation chaudière gaz
        ("installation_chaudiere", "IDF", 3200.00, "forfait", "dataset_batiment_2024"),
        ("installation_chaudiere", "IDF", 3500.00, "forfait", "artisan_paris_001"),
        ("installation_chaudiere", "IDF", 2900.00, "forfait", "artisan_paris_002"),
        ("installation_chaudiere", "PACA", 3000.00, "forfait", "dataset_batiment_2024"),
        ("installation_chaudiere", "ARA", 2800.00, "forfait", "dataset_batiment_2024"),
        ("installation_chaudiere", "NAQ", 2600.00, "forfait", "dataset_batiment_2024"),
        ("installation_chaudiere", "OCC", 2500.00, "forfait", "dataset_batiment_2024"),
        
        # MENUISERIE - Pose fenêtre PVC
        ("pose_fenetre", "IDF", 650.00, "forfait", "dataset_batiment_2024"),
        ("pose_fenetre", "IDF", 720.00, "forfait", "artisan_paris_001"),
        ("pose_fenetre", "IDF", 600.00, "forfait", "artisan_paris_002"),
        ("pose_fenetre", "PACA", 600.00, "forfait", "dataset_batiment_2024"),
        ("pose_fenetre", "ARA", 550.00, "forfait", "dataset_batiment_2024"),
        ("pose_fenetre", "NAQ", 500.00, "forfait", "dataset_batiment_2024"),
        ("pose_fenetre", "OCC", 480.00, "forfait", "dataset_batiment_2024"),
    ]
    
    return building_data


def seed_mechanic_prices():
    """Données de prix pour la mécanique auto (tarifs moyens France 2024)"""
    
    mechanic_data = [
        # FREINS - Remplacement plaquettes avant
        ("freins_plaquettes_avant", "IDF", 185.00, "forfait", "dataset_mecanique_2024"),
        ("freins_plaquettes_avant", "IDF", 210.00, "forfait", "garage_paris_001"),
        ("freins_plaquettes_avant", "IDF", 165.00, "forfait", "garage_paris_002"),
        ("freins_plaquettes_avant", "PACA", 175.00, "forfait", "dataset_mecanique_2024"),
        ("freins_plaquettes_avant", "PACA", 190.00, "forfait", "garage_marseille_001"),
        ("freins_plaquettes_avant", "ARA", 160.00, "forfait", "dataset_mecanique_2024"),
        ("freins_plaquettes_avant", "ARA", 175.00, "forfait", "garage_lyon_001"),
        ("freins_plaquettes_avant", "NAQ", 150.00, "forfait", "dataset_mecanique_2024"),
        ("freins_plaquettes_avant", "OCC", 145.00, "forfait", "dataset_mecanique_2024"),
        ("freins_plaquettes_avant", "HDF", 140.00, "forfait", "dataset_mecanique_2024"),
        
        # FREINS - Remplacement disques + plaquettes avant
        ("freins_complet_avant", "IDF", 320.00, "forfait", "dataset_mecanique_2024"),
        ("freins_complet_avant", "IDF", 350.00, "forfait", "garage_paris_001"),
        ("freins_complet_avant", "IDF", 290.00, "forfait", "garage_paris_002"),
        ("freins_complet_avant", "PACA", 300.00, "forfait", "dataset_mecanique_2024"),
        ("freins_complet_avant", "ARA", 280.00, "forfait", "dataset_mecanique_2024"),
        ("freins_complet_avant", "NAQ", 260.00, "forfait", "dataset_mecanique_2024"),
        ("freins_complet_avant", "OCC", 250.00, "forfait", "dataset_mecanique_2024"),
        
        # VIDANGE - Standard
        ("vidange_standard", "IDF", 95.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_standard", "IDF", 110.00, "forfait", "garage_paris_001"),
        ("vidange_standard", "IDF", 85.00, "forfait", "garage_paris_002"),
        ("vidange_standard", "PACA", 90.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_standard", "PACA", 100.00, "forfait", "garage_marseille_001"),
        ("vidange_standard", "ARA", 85.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_standard", "ARA", 95.00, "forfait", "garage_lyon_001"),
        ("vidange_standard", "NAQ", 80.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_standard", "OCC", 78.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_standard", "HDF", 75.00, "forfait", "dataset_mecanique_2024"),
        
        # VIDANGE - Haute performance (huile synthétique)
        ("vidange_synthetique", "IDF", 145.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_synthetique", "IDF", 165.00, "forfait", "garage_paris_001"),
        ("vidange_synthetique", "PACA", 135.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_synthetique", "ARA", 125.00, "forfait", "dataset_mecanique_2024"),
        ("vidange_synthetique", "NAQ", 115.00, "forfait", "dataset_mecanique_2024"),
        
        # PNEUS - Montage équilibrage (par pneu)
        ("montage_pneu", "IDF", 25.00, "unite", "dataset_mecanique_2024"),
        ("montage_pneu", "IDF", 30.00, "unite", "garage_paris_001"),
        ("montage_pneu", "IDF", 22.00, "unite", "garage_paris_002"),
        ("montage_pneu", "PACA", 24.00, "unite", "dataset_mecanique_2024"),
        ("montage_pneu", "ARA", 22.00, "unite", "dataset_mecanique_2024"),
        ("montage_pneu", "NAQ", 20.00, "unite", "dataset_mecanique_2024"),
        ("montage_pneu", "OCC", 19.00, "unite", "dataset_mecanique_2024"),
        
        # PNEUS - Forfait 4 pneus montés équilibrés
        ("forfait_4_pneus", "IDF", 85.00, "forfait", "dataset_mecanique_2024"),
        ("forfait_4_pneus", "IDF", 100.00, "forfait", "garage_paris_001"),
        ("forfait_4_pneus", "PACA", 80.00, "forfait", "dataset_mecanique_2024"),
        ("forfait_4_pneus", "ARA", 75.00, "forfait", "dataset_mecanique_2024"),
        ("forfait_4_pneus", "NAQ", 70.00, "forfait", "dataset_mecanique_2024"),
        
        # MAIN D'OEUVRE - Taux horaire garage
        ("main_oeuvre_mecanique", "IDF", 75.00, "heure", "dataset_mecanique_2024"),
        ("main_oeuvre_mecanique", "IDF", 85.00, "heure", "garage_paris_001"),
        ("main_oeuvre_mecanique", "IDF", 70.00, "heure", "garage_paris_002"),
        ("main_oeuvre_mecanique", "PACA", 70.00, "heure", "dataset_mecanique_2024"),
        ("main_oeuvre_mecanique", "PACA", 78.00, "heure", "garage_marseille_001"),
        ("main_oeuvre_mecanique", "ARA", 65.00, "heure", "dataset_mecanique_2024"),
        ("main_oeuvre_mecanique", "ARA", 72.00, "heure", "garage_lyon_001"),
        ("main_oeuvre_mecanique", "NAQ", 60.00, "heure", "dataset_mecanique_2024"),
        ("main_oeuvre_mecanique", "OCC", 58.00, "heure", "dataset_mecanique_2024"),
        ("main_oeuvre_mecanique", "HDF", 55.00, "heure", "dataset_mecanique_2024"),
        
        # EMBRAYAGE - Remplacement
        ("embrayage_remplacement", "IDF", 650.00, "forfait", "dataset_mecanique_2024"),
        ("embrayage_remplacement", "IDF", 720.00, "forfait", "garage_paris_001"),
        ("embrayage_remplacement", "PACA", 620.00, "forfait", "dataset_mecanique_2024"),
        ("embrayage_remplacement", "ARA", 580.00, "forfait", "dataset_mecanique_2024"),
        ("embrayage_remplacement", "NAQ", 540.00, "forfait", "dataset_mecanique_2024"),
        
        # DISTRIBUTION - Courroie de distribution
        ("courroie_distribution", "IDF", 520.00, "forfait", "dataset_mecanique_2024"),
        ("courroie_distribution", "IDF", 580.00, "forfait", "garage_paris_001"),
        ("courroie_distribution", "PACA", 500.00, "forfait", "dataset_mecanique_2024"),
        ("courroie_distribution", "ARA", 470.00, "forfait", "dataset_mecanique_2024"),
        ("courroie_distribution", "NAQ", 440.00, "forfait", "dataset_mecanique_2024"),
        
        # BATTERIE - Remplacement
        ("batterie_remplacement", "IDF", 35.00, "forfait", "dataset_mecanique_2024"),
        ("batterie_remplacement", "IDF", 45.00, "forfait", "garage_paris_001"),
        ("batterie_remplacement", "PACA", 32.00, "forfait", "dataset_mecanique_2024"),
        ("batterie_remplacement", "ARA", 30.00, "forfait", "dataset_mecanique_2024"),
        ("batterie_remplacement", "NAQ", 28.00, "forfait", "dataset_mecanique_2024"),
        
        # DIAGNOSTIC - Lecture défauts
        ("diagnostic_electronique", "IDF", 55.00, "forfait", "dataset_mecanique_2024"),
        ("diagnostic_electronique", "IDF", 65.00, "forfait", "garage_paris_001"),
        ("diagnostic_electronique", "PACA", 50.00, "forfait", "dataset_mecanique_2024"),
        ("diagnostic_electronique", "ARA", 48.00, "forfait", "dataset_mecanique_2024"),
        ("diagnostic_electronique", "NAQ", 45.00, "forfait", "dataset_mecanique_2024"),
        
        # CLIMATISATION - Recharge
        ("climatisation_recharge", "IDF", 95.00, "forfait", "dataset_mecanique_2024"),
        ("climatisation_recharge", "IDF", 110.00, "forfait", "garage_paris_001"),
        ("climatisation_recharge", "PACA", 90.00, "forfait", "dataset_mecanique_2024"),
        ("climatisation_recharge", "ARA", 85.00, "forfait", "dataset_mecanique_2024"),
        ("climatisation_recharge", "NAQ", 80.00, "forfait", "dataset_mecanique_2024"),
    ]
    
    return mechanic_data


def seed_all_prices():
    """Insère toutes les données de prix"""
    db = SessionLocal()
    try:
        # Vérifie si des prix existent déjà
        existing = db.query(Price).count()
        if existing > 0:
            print(f"✓ {existing} prix déjà initialisés")
            return
        
        # Combine toutes les données
        all_data = seed_building_prices() + seed_mechanic_prices()
        
        for category, region_code, price, unit, source in all_data:
            price_entry = Price(
                category=category,
                region_code=region_code,
                price=price,
                unit=unit,
                source=source
            )
            db.add(price_entry)
        
        db.commit()
        print(f"✓ {len(all_data)} prix initialisés")
        
        # Affiche un résumé
        categories = db.query(Price.category).distinct().count()
        regions = db.query(Price.region_code).distinct().count()
        print(f"  → {categories} catégories, {regions} régions")
        
    finally:
        db.close()


def main():
    """Point d'entrée pour initialiser la base de données"""
    print("🌱 Initialisation de la base de données TrustDevis Pricing...")
    
    # Crée les tables
    init_db()
    print("✓ Tables créées")
    
    # Insère les données
    seed_regions()
    seed_all_prices()
    
    print("\n✅ Base de données initialisée avec succès!")
    print("\nCatégories disponibles:")
    print("  Bâtiment: peinture, plomberie, remplacement_wc, toiture, electricite,")
    print("            installation_prise, installation_chaudiere, pose_fenetre")
    print("  Mécanique: freins_plaquettes_avant, freins_complet_avant, vidange_standard,")
    print("             vidange_synthetique, montage_pneu, forfait_4_pneus,")
    print("             main_oeuvre_mecanique, embrayage_remplacement,")
    print("             courroie_distribution, batterie_remplacement,")
    print("             diagnostic_electronique, climatisation_recharge")


if __name__ == "__main__":
    main()

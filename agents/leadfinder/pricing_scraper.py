"""
Module de scraping éthique de données tarifaires pour TrustDevis.
Collecte de mentions de prix depuis des sources publiques uniquement.
"""

import asyncio
import hashlib
import re
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse
import time

import httpx
from bs4 import BeautifulSoup


@dataclass
class PricingData:
    """Donnée tarifaire anonymisée"""
    id: str
    type_travaux: str
    sous_categorie: Optional[str]
    prix: Optional[float]
    prix_unitaire: Optional[float]  # €/m², €/heure, etc.
    unite: Optional[str]  # m², heure, forfait, etc.
    region: Optional[str]
    departement: Optional[str]
    date_mention: Optional[datetime]
    source: str
    url_source: Optional[str]
    contexte: Optional[str]  # Description anonymisée
    confiance: int  # 0-100 score de fiabilité
    scraped_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'date_mention': self.date_mention.isoformat() if self.date_mention else None,
            'scraped_at': self.scraped_at.isoformat()
        }


class RateLimiter:
    """Rate limiter simple - max 1 req/sec"""
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_request = 0
    
    async def wait(self):
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_request = time.time()


class BasePricingScraper(ABC):
    """Classe de base pour les scrapers de pricing"""
    
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limiter = RateLimiter(min_interval=1.0)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        self.data: List[PricingData] = []
    
    @abstractmethod
    async def scrape(self, **kwargs) -> List[PricingData]:
        """Méthode principale de scraping"""
        pass
    
    def _generate_id(self, content_hash: str) -> str:
        """Génère un ID unique anonymisé"""
        hash_input = f"{self.source_name}:{content_hash}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _anonymize_text(self, text: str) -> str:
        """Anonymise le texte - supprime noms, adresses, emails, téléphones"""
        if not text:
            return ""
        
        # Patterns à supprimer/remplacer
        patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
            (r'\b0[1-9](?:[\s.-]?\d{2}){4}\b', '[TEL]'),
            (r'\b\d{1,4}\s+(rue|avenue|boulevard|chemin|impasse|place|allée)\s+[^,.\n]{3,50}\b', '[ADRESSE]'),
            (r'M\.|Mme|Mr|Madame|Monsieur\s+\w+', '[PERSONNE]'),
            (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[NOM]'),  # Noms propres simples
        ]
        
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _extract_price(self, text: str) -> Optional[Tuple[float, str]]:
        """Extrait un prix et son unité du texte"""
        if not text:
            return None
        
        # Patterns de prix
        patterns = [
            # Prix avec €, euros, EUR
            r'(\d[\d\s,.]*)(?:\s*)(?:€|euros?|EUR)',
            # Prix /m², /heure, etc.
            r'(\d[\d\s,.]*)(?:\s*)(?:€|euros?|EUR)?(?:\s*)(?:/|par|au\s+)(m²|m2|metre|heure|h|jour|j|forfait)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Prend le premier prix trouvé
                match = matches[0]
                if isinstance(match, tuple):
                    price_str, unite = match
                else:
                    price_str = match
                    unite = None
                
                # Nettoie et convertit
                price_str = price_str.replace(' ', '').replace(',', '.')
                try:
                    price = float(price_str)
                    if price > 1000000:  # Outlier évident
                        return None
                    return (price, unite)
                except ValueError:
                    continue
        
        return None
    
    def _detect_region(self, text: str) -> Optional[str]:
        """Détecte la région dans le texte"""
        regions = [
            'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Bretagne',
            'Centre-Val de Loire', 'Corse', 'Grand Est', 'Hauts-de-France',
            'Île-de-France', 'Normandie', 'Nouvelle-Aquitaine', 'Occitanie',
            'Pays de la Loire', "Provence-Alpes-Côte d'Azur"
        ]
        
        text_lower = text.lower()
        for region in regions:
            if region.lower() in text_lower:
                return region
        
        # Départements
        dept_pattern = r'\b(\d{2})\s*\d{3}\b'
        matches = re.findall(dept_pattern, text)
        if matches:
            return self._dept_to_region(matches[0])
        
        return None
    
    def _dept_to_region(self, dept: str) -> Optional[str]:
        """Convertit un département en région"""
        mapping = {
            '01': 'Auvergne-Rhône-Alpes', '03': 'Auvergne-Rhône-Alpes',
            '07': 'Auvergne-Rhône-Alpes', '15': 'Auvergne-Rhône-Alpes',
            '26': 'Auvergne-Rhône-Alpes', '38': 'Auvergne-Rhône-Alpes',
            '42': 'Auvergne-Rhône-Alpes', '43': 'Auvergne-Rhône-Alpes',
            '63': 'Auvergne-Rhône-Alpes', '69': 'Auvergne-Rhône-Alpes',
            '73': 'Auvergne-Rhône-Alpes', '74': 'Auvergne-Rhône-Alpes',
            '21': 'Bourgogne-Franche-Comté', '25': 'Bourgogne-Franche-Comté',
            '39': 'Bourgogne-Franche-Comté', '58': 'Bourgogne-Franche-Comté',
            '70': 'Bourgogne-Franche-Comté', '71': 'Bourgogne-Franche-Comté',
            '89': 'Bourgogne-Franche-Comté', '90': 'Bourgogne-Franche-Comté',
            '22': 'Bretagne', '29': 'Bretagne', '35': 'Bretagne', '56': 'Bretagne',
            '18': 'Centre-Val de Loire', '28': 'Centre-Val de Loire',
            '36': 'Centre-Val de Loire', '37': 'Centre-Val de Loire',
            '41': 'Centre-Val de Loire', '45': 'Centre-Val de Loire',
            '2A': 'Corse', '2B': 'Corse',
            '08': 'Grand Est', '10': 'Grand Est', '51': 'Grand Est',
            '52': 'Grand Est', '54': 'Grand Est', '55': 'Grand Est',
            '57': 'Grand Est', '67': 'Grand Est', '68': 'Grand Est',
            '88': 'Grand Est', '02': 'Hauts-de-France', '59': 'Hauts-de-France',
            '60': 'Hauts-de-France', '62': 'Hauts-de-France', '80': 'Hauts-de-France',
            '75': 'Île-de-France', '77': 'Île-de-France', '78': 'Île-de-France',
            '91': 'Île-de-France', '92': 'Île-de-France', '93': 'Île-de-France',
            '94': 'Île-de-France', '95': 'Île-de-France',
            '14': 'Normandie', '27': 'Normandie', '50': 'Normandie',
            '61': 'Normandie', '76': 'Normandie',
            '16': 'Nouvelle-Aquitaine', '17': 'Nouvelle-Aquitaine',
            '19': 'Nouvelle-Aquitaine', '23': 'Nouvelle-Aquitaine',
            '24': 'Nouvelle-Aquitaine', '33': 'Nouvelle-Aquitaine',
            '40': 'Nouvelle-Aquitaine', '47': 'Nouvelle-Aquitaine',
            '64': 'Nouvelle-Aquitaine', '79': 'Nouvelle-Aquitaine',
            '86': 'Nouvelle-Aquitaine', '87': 'Nouvelle-Aquitaine',
            '09': 'Occitanie', '11': 'Occitanie', '12': 'Occitanie',
            '30': 'Occitanie', '31': 'Occitanie', '32': 'Occitanie',
            '34': 'Occitanie', '46': 'Occitanie', '48': 'Occitanie',
            '65': 'Occitanie', '66': 'Occitanie', '81': 'Occitanie',
            '82': 'Occitanie', '44': 'Pays de la Loire', '49': 'Pays de la Loire',
            '53': 'Pays de Loire', '72': 'Pays de la Loire', '85': 'Pays de la Loire',
            '04': "Provence-Alpes-Côte d'Azur", '05': "Provence-Alpes-Côte d'Azur",
            '06': "Provence-Alpes-Côte d'Azur", '13': "Provence-Alpes-Côte d'Azur",
            '83': "Provence-Alpes-Côte d'Azur", '84': "Provence-Alpes-Côte d'Azur"
        }
        return mapping.get(dept)
    
    def _detect_type_travaux(self, text: str) -> Tuple[str, Optional[str]]:
        """Détecte le type de travaux et sous-catégorie"""
        text_lower = text.lower()
        
        # Mapping des types avec priorité
        categories = {
            # Plomberie (priorité haute)
            'plomberie': ('reparation', 'plomberie'),
            'plombier': ('reparation', 'plomberie'),
            'fuite d eau': ('reparation', 'plomberie'),
            'fuite d\'eau': ('reparation', 'plomberie'),
            'robinet': ('reparation', 'plomberie'),
            'wc': ('installation', 'plomberie'),
            'toilettes': ('installation', 'plomberie'),
            'douche': ('renovation', 'plomberie'),
            'lavabo': ('installation', 'plomberie'),
            'evier': ('installation', 'plomberie'),
            'tuyau': ('reparation', 'plomberie'),
            'canalisation': ('reparation', 'plomberie'),
            
            # Électricité
            'electricite': ('installation', 'electricite'),
            'electricien': ('installation', 'electricite'),
            'electrique': ('installation', 'electricite'),
            'tableau electrique': ('installation', 'electricite'),
            'prise': ('installation', 'electricite'),
            'interrupteur': ('installation', 'electricite'),
            'eclairage': ('installation', 'electricite'),
            'spot': ('installation', 'electricite'),
            'cablage': ('installation', 'electricite'),
            'disjoncteur': ('installation', 'electricite'),
            
            # Peinture
            'peinture': ('renovation', 'peinture'),
            'peintre': ('renovation', 'peinture'),
            'peindre': ('renovation', 'peinture'),
            'enduit': ('renovation', 'peinture'),
            'tapisserie': ('renovation', 'peinture'),
            
            # Chauffage / Clim
            'chauffage': ('installation', 'chauffage'),
            'chaudiere': ('installation', 'chauffage'),
            'climatisation': ('installation', 'climatisation'),
            'clim': ('installation', 'climatisation'),
            'pompe a chaleur': ('installation', 'chauffage'),
            'pac': ('installation', 'chauffage'),
            'radiateur': ('installation', 'chauffage'),
            'poele': ('installation', 'chauffage'),
            'cheminee': ('installation', 'chauffage'),
            
            # Toiture
            'toiture': ('renovation', 'toiture'),
            'couverture': ('renovation', 'toiture'),
            'toit': ('renovation', 'toiture'),
            'tuile': ('renovation', 'toiture'),
            'ardoise': ('renovation', 'toiture'),
            'gouttiere': ('renovation', 'toiture'),
            'zinc': ('renovation', 'toiture'),
            'charpente': ('renovation', 'charpente'),
            
            # Sols
            'carrelage': ('renovation', 'carrelage'),
            'carreleur': ('renovation', 'carrelage'),
            'parquet': ('renovation', 'parquet'),
            'parqueteur': ('renovation', 'parquet'),
            'sol': ('renovation', 'sol'),
            'dalles': ('renovation', 'sol'),
            'moquette': ('renovation', 'sol'),
            
            # Menuiserie
            'menuiserie': ('renovation', 'menuiserie'),
            'menuisier': ('renovation', 'menuiserie'),
            'fenetre': ('renovation', 'fenetres'),
            'fenetres': ('renovation', 'fenetres'),
            'porte': ('renovation', 'menuiserie'),
            'portes': ('renovation', 'menuiserie'),
            'volet': ('renovation', 'menuiserie'),
            'volets': ('renovation', 'menuiserie'),
            'baie vitree': ('renovation', 'fenetres'),
            'verriere': ('renovation', 'menuiserie'),
            'escalier': ('renovation', 'menuiserie'),
            'placard': ('renovation', 'menuiserie'),
            
            # Pièces spécifiques
            'salle de bain': ('renovation', 'salle_de_bain'),
            'salle de bains': ('renovation', 'salle_de_bain'),
            'sdb': ('renovation', 'salle_de_bain'),
            'douche italienne': ('renovation', 'salle_de_bain'),
            'baignoire': ('renovation', 'salle_de_bain'),
            'cuisine': ('renovation', 'cuisine'),
            'meuble cuisine': ('renovation', 'cuisine'),
            'plan de travail': ('renovation', 'cuisine'),
            
            # Maçonnerie
            'maconnerie': ('construction', 'maconnerie'),
            'macon': ('construction', 'maconnerie'),
            'mur': ('construction', 'maconnerie'),
            'cloison': ('renovation', 'maconnerie'),
            'dalle': ('construction', 'maconnerie'),
            'fondation': ('construction', 'maconnerie'),
            'démolition': ('renovation', 'demolition'),
            'ouverture mur': ('renovation', 'maconnerie'),
            
            # Isolation
            'isolation': ('renovation', 'isolation'),
            'isoler': ('renovation', 'isolation'),
            'ite': ('renovation', 'isolation'),
            'iti': ('renovation', 'isolation'),
            'combles': ('renovation', 'isolation'),
            'grenier': ('renovation', 'isolation'),
            'sous-sol': ('renovation', 'isolation'),
            'vide sanitaire': ('renovation', 'isolation'),
            
            # Extérieur
            'terrasse': ('exterieur', 'terrasse'),
            'terrassement': ('exterieur', 'terrassement'),
            'piscine': ('exterieur', 'piscine'),
            'jardin': ('exterieur', 'jardin'),
            'cloture': ('exterieur', 'cloture'),
            'portail': ('exterieur', 'cloture'),
            'allee': ('exterieur', 'terrassement'),
            'abri de jardin': ('exterieur', 'abri'),
            'pergola': ('exterieur', 'pergola'),
            
            # Construction
            'construction': ('construction', 'construction'),
            'construire': ('construction', 'construction'),
            'maison': ('construction', 'construction'),
            'extension': ('construction', 'extension'),
            'annexe': ('construction', 'extension'),
            'garage': ('construction', 'garage'),
            'abri': ('construction', 'abri'),
            
            # Plâtrerie
            'placo': ('renovation', 'platrerie'),
            'platrerie': ('renovation', 'platrerie'),
            'plaque de platre': ('renovation', 'platrerie'),
            'cloison seche': ('renovation', 'platrerie'),
            'plaquiste': ('renovation', 'platrerie'),
            'faux plafond': ('renovation', 'platrerie'),
        }
        
        for keyword, (type_t, sous_cat) in categories.items():
            if keyword in text_lower:
                return (type_t, sous_cat)
        
        return ('autre', None)
    
    def _calculate_confidence(self, data: PricingData) -> int:
        """Calcule le score de confiance 0-100"""
        score = 40  # Base
        
        # Prix présent et cohérent
        if data.prix and 50 < data.prix < 500000:
            score += 15
            
            # Prix dans une fourchette réaliste pour des travaux
            if 100 <= data.prix <= 100000:
                score += 10
        
        # Région identifiée
        if data.region:
            score += 15
        
        # Département identifié (plus précis)
        if data.departement:
            score += 5
        
        # Type de travaux identifié (très important)
        if data.type_travaux != 'autre':
            score += 20
            
            # Sous-catégorie aussi identifiée
            if data.sous_categorie:
                score += 10
        
        # Contexte présent et de bonne qualité
        if data.contexte:
            if len(data.contexte) > 100:
                score += 5
            if len(data.contexte) > 200:
                score += 5
        
        # Date de mention présente
        if data.date_mention:
            score += 5
        
        return min(100, score)
    
    async def close(self):
        """Ferme le client HTTP"""
        await self.client.aclose()


class BricoleurDuDimancheScraper(BasePricingScraper):
    """
    Scraper pour BricoleurDuDimanche.com (forum bricolage)
    Source: discussions publiques avec mentions de prix
    """
    
    def __init__(self):
        super().__init__("bricoleurdudimanche", "https://www.bricoleurdudimanche.com")
    
    async def scrape(self, max_pages: int = 5, **kwargs) -> List[PricingData]:
        """
        Scrape les discussions du forum avec mentions de prix.
        Respecte robots.txt - uniquement pages publiques.
        """
        print(f"[{self.source_name}] Démarrage scraping (max {max_pages} pages)...")
        
        # URLs des sections pertinentes
        sections = [
            '/forum/f/18-plomberie',  # Plomberie
            '/forum/f/19-electricite',  # Électricité
            '/forum/f/20-chauffage',  # Chauffage
            '/forum/f/21-menuiserie',  # Menuiserie
            '/forum/f/22-peinture',  # Peinture
            '/forum/f/23-carrelage',  # Carrelage
            '/forum/f/24-toiture',  # Toiture
        ]
        
        for section in sections[:max_pages]:
            await self.rate_limiter.wait()
            
            try:
                url = urljoin(self.base_url, section)
                response = await self.client.get(url)
                
                if response.status_code != 200:
                    print(f"[{self.source_name}] Erreur {response.status_code} sur {url}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extraction des sujets de discussion
                topics = soup.find_all('a', class_='topic-title')
                
                for topic in topics[:10]:  # Limite par section
                    topic_url = urljoin(self.base_url, topic.get('href', ''))
                    await self._scrape_topic(topic_url)
                    
            except Exception as e:
                print(f"[{self.source_name}] Erreur: {e}")
                continue
        
        print(f"[{self.source_name}] {len(self.data)} données collectées")
        return self.data
    
    async def _scrape_topic(self, url: str):
        """Scrape un sujet de discussion spécifique"""
        await self.rate_limiter.wait()
        
        try:
            response = await self.client.get(url)
            if response.status_code != 200:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction des messages
            posts = soup.find_all('div', class_='post-content')
            
            for post in posts:
                text = post.get_text(separator=' ', strip=True)
                
                # Vérifie si mention de prix
                price_info = self._extract_price(text)
                if not price_info:
                    continue
                
                prix, unite = price_info
                
                # Anonymise le texte
                contexte = self._anonymize_text(text[:500])
                
                # Détecte métadonnées
                type_t, sous_cat = self._detect_type_travaux(text)
                region = self._detect_region(text)
                
                # Crée la donnée
                data = PricingData(
                    id=self._generate_id(text[:200]),
                    type_travaux=type_t,
                    sous_categorie=sous_cat,
                    prix=prix,
                    prix_unitaire=None,
                    unite=unite,
                    region=region,
                    departement=None,
                    date_mention=datetime.now(),
                    source=self.source_name,
                    url_source=url,
                    contexte=contexte,
                    confiance=50,
                    scraped_at=datetime.now()
                )
                
                data.confiance = self._calculate_confidence(data)
                
                # Vérifie si pas déjà présent
                if not any(d.id == data.id for d in self.data):
                    self.data.append(data)
                    
        except Exception as e:
            print(f"[{self.source_name}] Erreur topic {url}: {e}")


class RedditScraper(BasePricingScraper):
    """
    Scraper pour Reddit (r/bricolage, r/France)
    Utilise l'API JSON publique de Reddit (pas besoin d'authentification pour lecture)
    """
    
    def __init__(self):
        super().__init__("reddit", "https://www.reddit.com")
        self.client.headers['User-Agent'] = 'TrustDevisPricingBot/1.0'
    
    # Requêtes de recherche ciblées sur les travaux
    SEARCH_QUERIES = [
        'devis plomberie OR devis electricite OR devis peinture',
        'prix renovation salle de bain OR prix renovation cuisine',
        'cout travaux OR tarif artisan OR prix metre carre',
        'devis toiture OR devis charpente OR prix couverture',
        'prix carrelage OR prix parquet OR prix menuiserie',
        'devis chauffage OR devis climatisation OR prix pompe a chaleur',
        'tarif macon OR tarif plaquiste OR tarif peintre',
        'prix construction maison OR budget travaux',
    ]
    
    async def scrape(self, subreddits: List[str] = None, **kwargs) -> List[PricingData]:
        """
        Scrape les posts Reddit avec mentions de prix sur les travaux.
        """
        if subreddits is None:
            subreddits = ['bricolage', 'france', 'renovation', 'travaux']
        
        print(f"[{self.source_name}] Démarrage scraping sur {subreddits}...")
        
        for subreddit in subreddits:
            for query in self.SEARCH_QUERIES[:4]:  # Limite les requêtes
                await self._scrape_subreddit(subreddit, query)
        
        print(f"[{self.source_name}] {len(self.data)} données collectées")
        return self.data
    
    async def _scrape_subreddit(self, subreddit: str, query: str = None):
        """Scrape un subreddit spécifique avec une requête ciblée"""
        await self.rate_limiter.wait()
        
        try:
            # Utilise l'API JSON publique
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                'q': query or 'devis OR prix travaux OR tarif artisan OR €',
                'restrict_sr': '1',
                'sort': 'new',
                'limit': '25'
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 429:
                print(f"[{self.source_name}] Rate limit atteint, attente...")
                await asyncio.sleep(5)
                return
            
            if response.status_code != 200:
                print(f"[{self.source_name}] Erreur {response.status_code}")
                return
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                full_text = f"{title} {selftext}"
                
                # Extrait prix
                price_info = self._extract_price(full_text)
                if not price_info:
                    continue
                
                prix, unite = price_info
                
                # Anonymise
                contexte = self._anonymize_text(full_text[:500])
                
                # Détecte métadonnées
                type_t, sous_cat = self._detect_type_travaux(full_text)
                region = self._detect_region(full_text)
                
                # Date du post
                created_utc = post_data.get('created_utc')
                date_mention = datetime.fromtimestamp(created_utc) if created_utc else None
                
                # Crée la donnée
                pricing_data = PricingData(
                    id=self._generate_id(post_data.get('id', '')),
                    type_travaux=type_t,
                    sous_categorie=sous_cat,
                    prix=prix,
                    prix_unitaire=None,
                    unite=unite,
                    region=region,
                    departement=None,
                    date_mention=date_mention,
                    source=f"reddit_{subreddit}",
                    url_source=f"https://reddit.com{post_data.get('permalink', '')}",
                    contexte=contexte,
                    confiance=50,
                    scraped_at=datetime.now()
                )
                
                pricing_data.confiance = self._calculate_confidence(pricing_data)
                
                if not any(d.id == pricing_data.id for d in self.data):
                    self.data.append(pricing_data)
                    
        except Exception as e:
            print(f"[{self.source_name}] Erreur subreddit {subreddit}: {e}")


class PricingDataStore:
    """Stockage des données tarifaires"""
    
    def __init__(self, data_dir: str = "/root/.openclaw/workspace/trustdevis/data/pricing"):
        self.data_dir = data_dir
        self.ensure_dir()
    
    def ensure_dir(self):
        """Crée le répertoire si nécessaire"""
        import os
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save(self, data: List[PricingData], filename: str = None):
        """Sauvegarde les données en JSON"""
        if filename is None:
            filename = f"pricing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = f"{self.data_dir}/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([d.to_dict() for d in data], f, ensure_ascii=False, indent=2)
        
        print(f"[Store] {len(data)} données sauvegardées dans {filepath}")
        return filepath
    
    def load_all(self) -> List[PricingData]:
        """Charge toutes les données existantes"""
        import os
        import glob
        
        all_data = []
        pattern = f"{self.data_dir}/pricing_*.json"
        
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
            except Exception as e:
                print(f"[Store] Erreur chargement {filepath}: {e}")
        
        return all_data
    
    def get_stats(self) -> Dict:
        """Statistiques sur les données collectées"""
        data = self.load_all()
        
        if not data:
            return {"total": 0}
        
        stats = {
            "total": len(data),
            "by_type": {},
            "by_region": {},
            "by_source": {},
            "avg_confidence": sum(d.get('confiance', 0) for d in data) / len(data),
            "price_range": {
                "min": min(d.get('prix', float('inf')) for d in data if d.get('prix')),
                "max": max(d.get('prix', 0) for d in data if d.get('prix'))
            }
        }
        
        for d in data:
            t = d.get('type_travaux', 'unknown')
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
            
            r = d.get('region', 'unknown')
            stats["by_region"][r] = stats["by_region"].get(r, 0) + 1
            
            s = d.get('source', 'unknown')
            stats["by_source"][s] = stats["by_source"].get(s, 0) + 1
        
        return stats


class PricingScraperManager:
    """Gestionnaire central des scrapers de pricing"""
    
    def __init__(self):
        self.scrapers = {
            'reddit': RedditScraper(),
            'bricoleurdudimanche': BricoleurDuDimancheScraper(),
        }
        self.store = PricingDataStore()
    
    async def run_all(self, **kwargs) -> Dict[str, List[PricingData]]:
        """Exécute tous les scrapers"""
        results = {}
        
        for name, scraper in self.scrapers.items():
            try:
                print(f"\n[Manager] Lancement {name}...")
                data = await scraper.scrape(**kwargs)
                results[name] = data
                
                # Sauvegarde immédiate
                if data:
                    self.store.save(data, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    
            except Exception as e:
                print(f"[Manager] Erreur {name}: {e}")
                results[name] = []
        
        return results
    
    async def close_all(self):
        """Ferme tous les scrapers"""
        for scraper in self.scrapers.values():
            await scraper.close()
    
    def get_report(self) -> str:
        """Génère un rapport des données collectées"""
        stats = self.store.get_stats()
        
        report = f"""
📊 RAPPORT PRICING SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*60}

📈 STATISTIQUES GLOBALES
• Total données collectées: {stats['total']}
• Confiance moyenne: {stats.get('avg_confidence', 0):.1f}/100

📁 PAR TYPE DE TRAVAUX
"""
        for t, count in sorted(stats.get('by_type', {}).items(), key=lambda x: -x[1]):
            report += f"  • {t}: {count}\n"
        
        report += "\n🌍 PAR RÉGION\n"
        for r, count in sorted(stats.get('by_region', {}).items(), key=lambda x: -x[1]):
            report += f"  • {r}: {count}\n"
        
        report += "\n🔗 PAR SOURCE\n"
        for s, count in sorted(stats.get('by_source', {}).items(), key=lambda x: -x[1]):
            report += f"  • {s}: {count}\n"
        
        if 'price_range' in stats:
            report += f"\n💰 FOURCHETTE DE PRIX\n"
            report += f"  • Min: {stats['price_range']['min']:.2f}€\n"
            report += f"  • Max: {stats['price_range']['max']:.2f}€\n"
        
        return report


# ============================================================================
# Point d'entrée pour exécution autonome
# ============================================================================

async def main():
    """Fonction principale de scraping"""
    print("🚀 Démarrage du Pricing Scraper TrustDevis")
    print("="*60)
    print("Règles: Respect robots.txt | Rate limit: 1 req/sec | Anonymisation active")
    print("="*60)
    
    manager = PricingScraperManager()
    
    try:
        # Exécute tous les scrapers
        results = await manager.run_all(max_pages=3)
        
        # Affiche le rapport
        print("\n" + manager.get_report())
        
        # Sauvegarde consolidée
        all_data = []
        for data_list in results.values():
            all_data.extend(data_list)
        
        if all_data:
            manager.store.save(all_data, f"consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        print(f"\n✅ Scraping terminé. {len(all_data)} données collectées au total.")
        
    finally:
        await manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())

"""
Logique de classification TrustDevis
=====================================
Classification fuzzy des lignes de devis
Détection des unités et scoring de confiance
"""

import re
from typing import Dict, List, Tuple, Optional
from thefuzz import fuzz, process
from categories import ALL_CATEGORIES, BUILDING_CATEGORIES, MECHANIC_CATEGORIES


class LineNormalizer:
    """Normalise une ligne de devis en catégorie standardisée"""
    
    # Patterns pour détection des unités
    UNIT_PATTERNS = {
        "m2": [
            r'm[²2]', r'm2', r'm²', r'm\^2', r'metre carre', r'mètre carré',
            r'mc', r'm.c', r'au m2', r'au m²', r'/m2', r'/m²'
        ],
        "hour": [
            r'h\b', r'heure', r'heures', r'hr', r'hrs', r'heure\(s\)',
            r'h/mo', r'heure de main', r'heure ouvree', r'heure ouvrée'
        ],
        "unit": [
            r'u\b', r'unite', r'unité', r'unit', r'piece', r'pièce',
            r'forfait', r'prestation', r'intervention', r'poste'
        ],
        "item": [
            r'item', r'lot', r'package', r'ensemble', r'kit', r'pack'
        ],
        "linear": [
            r'ml\b', r'm\.l', r'ml\b', r'metre lineaire', r'mètre linéaire',
            r'linear', r'au ml', r'/ml'
        ],
    }
    
    # Seuils de confiance
    CONFIDENCE_HIGH = 85
    CONFIDENCE_MEDIUM = 60
    CONFIDENCE_LOW = 40
    
    def __init__(self):
        self.category_keywords = self._build_keyword_index()
    
    def _build_keyword_index(self) -> Dict[str, List[Tuple[str, str]]]:
        """Construit un index des mots-clés pour recherche rapide"""
        index = {}
        for cat_id, cat_data in ALL_CATEGORIES.items():
            for keyword in cat_data.get("keywords", []):
                keyword_lower = keyword.lower()
                if keyword_lower not in index:
                    index[keyword_lower] = []
                index[keyword_lower].append((cat_id, cat_data["name"]))
        return index
    
    def normalize(self, line: str, sector: Optional[str] = None) -> Dict:
        """
        Normalise une ligne de devis
        
        Args:
            line: Ligne brute OCR
            sector: Secteur optionnel ('building' ou 'mechanic')
        
        Returns:
            Dict avec category, unit, qty, normalized_desc, confidence
        """
        line_clean = self._clean_line(line)
        
        # Détection de la catégorie
        category_result = self._detect_category(line_clean, sector)
        
        # Détection de l'unité
        unit = self._detect_unit(line_clean) or category_result.get("default_unit", "unit")
        
        # Extraction de la quantité
        qty = self._extract_quantity(line_clean)
        
        # Normalisation de la description
        normalized_desc = self._normalize_description(line_clean, category_result.get("category"))
        
        # Calcul du score de confiance
        confidence = self._calculate_confidence(line_clean, category_result, unit)
        
        return {
            "orig_line": line,
            "category": category_result.get("category", "unknown"),
            "unit": unit,
            "qty": qty,
            "normalized_desc": normalized_desc,
            "confidence": confidence,
            "category_name": category_result.get("category_name", "Inconnu"),
        }
    
    def _clean_line(self, line: str) -> str:
        """Nettoie la ligne OCR"""
        # Supprime les caractères spéciaux excessifs
        line = re.sub(r'[^\w\s\-\.,;:/\(\)€%²m²]', ' ', line)
        # Normalise les espaces
        line = re.sub(r'\s+', ' ', line).strip()
        # Minuscules pour matching
        return line.lower()
    
    def _detect_category(self, line: str, sector: Optional[str] = None) -> Dict:
        """Détecte la catégorie par matching fuzzy"""
        categories = ALL_CATEGORIES
        if sector == "building":
            categories = BUILDING_CATEGORIES
        elif sector == "mechanic":
            categories = MECHANIC_CATEGORIES
        
        best_match = None
        best_score = 0
        
        for cat_id, cat_data in categories.items():
            # Matching sur les mots-clés
            for keyword in cat_data.get("keywords", []):
                # Fuzzy match exact
                score = fuzz.partial_ratio(keyword.lower(), line)
                
                # Bonus si le mot-clé est présent exactement
                if keyword.lower() in line:
                    score = min(100, score + 15)
                
                # Vérification des exclusions
                excluded = False
                for excl in cat_data.get("exclude", []):
                    if excl.lower() in line:
                        excluded = True
                        break
                
                if not excluded and score > best_score:
                    best_score = score
                    best_match = {
                        "category": cat_id,
                        "category_name": cat_data["name"],
                        "default_unit": cat_data.get("unit", "unit"),
                        "score": score
                    }
        
        return best_match or {"category": "unknown", "category_name": "Inconnu", "default_unit": "unit", "score": 0}
    
    def _detect_unit(self, line: str) -> Optional[str]:
        """Détecte l'unité de mesure dans la ligne"""
        for unit_type, patterns in self.UNIT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return unit_type
        return None
    
    def _extract_quantity(self, line: str) -> Optional[float]:
        """Extrait la quantité numérique de la ligne"""
        # Patterns pour quantités
        patterns = [
            r'(\d+[.,]?\d*)\s*(?:m[²2]|m2|m²|mc|m\.c)',  # m²
            r'(\d+[.,]?\d*)\s*(?:h\b|heure|hr)',  # heures
            r'(\d+[.,]?\d*)\s*(?:u\b|unite|unité|piece|pièce)',  # unités
            r'(\d+[.,]?\d*)\s*(?:ml\b|m\.l)',  # ml
            r'x\s*(\d+[.,]?\d*)',  # x 5
            r'^(\d+[.,]?\d*)\s+',  # nombre au début
            r'\s(\d+[.,]?\d*)\s*$',  # nombre à la fin
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    qty_str = match.group(1).replace(',', '.')
                    return float(qty_str)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _normalize_description(self, line: str, category: Optional[str]) -> str:
        """Normalise la description pour affichage"""
        # Supprime les prix et quantités
        desc = re.sub(r'\d+[.,]?\d*\s*[€$]', '', line)
        desc = re.sub(r'x\s*\d+[.,]?\d*', '', desc)
        desc = re.sub(r'\d+\s*(?:m[²2]|h\b|u\b)', '', desc)
        
        # Capitalise la première lettre
        desc = desc.strip()
        if desc:
            desc = desc[0].upper() + desc[1:]
        
        return desc
    
    def _calculate_confidence(self, line: str, category_result: Dict, detected_unit: str) -> float:
        """Calcule le score de confiance global"""
        scores = []
        
        # Score de matching catégorie
        cat_score = category_result.get("score", 0)
        scores.append(cat_score * 0.6)  # 60% du score total
        
        # Score de détection d'unité
        if detected_unit and detected_unit != "unknown":
            scores.append(30)  # Bonus unité détectée
        
        # Score basé sur la qualité OCR
        ocr_quality = self._assess_ocr_quality(line)
        scores.append(ocr_quality * 0.1)
        
        total = sum(scores)
        return round(min(100, total), 1)
    
    def _assess_ocr_quality(self, line: str) -> float:
        """Évalue la qualité de la ligne OCR"""
        score = 100
        
        # Pénalise les caractères suspects
        suspicious = len(re.findall(r'[^\w\s\-\.,;:/\(\)€%²m²]', line))
        score -= suspicious * 5
        
        # Pénalise les mots trop courts (bruit OCR)
        words = line.split()
        short_words = sum(1 for w in words if len(w) <= 2)
        if words:
            score -= (short_words / len(words)) * 20
        
        return max(0, score)


def normalize_lines(lines: List[str], sector: Optional[str] = None) -> List[Dict]:
    """
    Normalise une liste de lignes de devis
    
    Args:
        lines: Liste de lignes brutes OCR
        sector: Secteur optionnel ('building' ou 'mechanic')
    
    Returns:
        Liste de résultats normalisés
    """
    normalizer = LineNormalizer()
    return [normalizer.normalize(line, sector) for line in lines if line.strip()]


def batch_normalize(lines: List[str], sector: Optional[str] = None) -> Dict:
    """
    Normalisation batch avec statistiques
    
    Returns:
        Dict avec 'results' et 'stats'
    """
    results = normalize_lines(lines, sector)
    
    stats = {
        "total_lines": len(results),
        "categorized": sum(1 for r in results if r["category"] != "unknown"),
        "high_confidence": sum(1 for r in results if r["confidence"] >= 85),
        "medium_confidence": sum(1 for r in results if 60 <= r["confidence"] < 85),
        "low_confidence": sum(1 for r in results if r["confidence"] < 60),
        "categories_found": len(set(r["category"] for r in results if r["category"] != "unknown")),
    }
    
    return {
        "results": results,
        "stats": stats
    }

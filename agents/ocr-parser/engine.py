"""
Moteur OCR pour TrustDevis
Extraction de texte et structuration des données de devis
"""

import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import tempfile
import os


@dataclass
class LineItem:
    """Représente une ligne de devis structurée"""
    description: str
    quantity: Optional[float]
    unit_price: Optional[float]
    total: Optional[float]
    confidence: float
    raw_text: str


@dataclass
class ExtractionResult:
    """Résultat complet de l'extraction"""
    filename: str
    raw_text: str
    lines: List[Dict[str, Any]]


class OCREngine:
    """Moteur OCR avec Tesseract pour extraction de devis"""
    
    def __init__(self, lang: str = "fra+eng", dpi: int = 300):
        self.lang = lang
        self.dpi = dpi
        
        # Patterns pour détection des lignes de devis
        self.patterns = {
            # Pattern générique: description + quantité + prix unitaire + total
            'line_with_qty_price': re.compile(
                r'(?P<desc>.+?)\s+(?P<qty>\d+[.,]?\d*)\s*(?P<unit>m[²2]?|ml|u|h|forfait)?\s+(?P<unit_price>\d+[.,]?\d*)\s*[€$]?\s+(?P<total>\d+[.,]?\d*)\s*[€$]?',
                re.IGNORECASE
            ),
            # Pattern avec prix total seulement
            'line_with_total': re.compile(
                r'(?P<desc>.+?)\s+(?P<total>\d+[.,]?\d*)\s*[€$]',
                re.IGNORECASE
            ),
            # Pattern mécanique: pièce + main d'œuvre
            'mechanic_line': re.compile(
                r'(?P<desc>.+?)\s+(?P<ref>[A-Z0-9-]+)?\s+(?P<qty>\d+)\s+x?\s*(?P<unit_price>\d+[.,]?\d*)',
                re.IGNORECASE
            ),
        }
        
        # Mots-clés à ignorer (en-têtes, pieds de page)
        self.skip_keywords = [
            'total', 'sous-total', 'tva', 'ht', 'ttc', 'taux', 'montant',
            'devis', 'facture', 'date', 'client', 'adresse', 'téléphone',
            'email', 'siret', 'rcs', 'rib', 'iban', 'tva intracommunautaire'
        ]
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extrait le texte d'un PDF en convertissant en images"""
        images = convert_from_path(pdf_path, dpi=self.dpi)
        all_text = []
        
        for img in images:
            # Convertir PIL Image en format compatible
            text = self._extract_from_pil_image(img)
            all_text.append(text)
        
        return "\n".join(all_text)
    
    def extract_from_image(self, image_path: str) -> str:
        """Extrait le texte d'une image"""
        img = Image.open(image_path)
        return self._extract_from_pil_image(img)
    
    def _extract_from_pil_image(self, img: Image.Image) -> str:
        """Extrait le texte d'une image PIL avec prétraitement"""
        # Convertir en numpy array pour OpenCV
        img_array = np.array(img)
        
        # Prétraitement pour améliorer l'OCR
        processed = self._preprocess_image(img_array)
        
        # OCR avec données détaillées
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed, lang=self.lang, config=custom_config)
        
        return text
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Prétraite l'image pour améliorer la qualité OCR"""
        # Convertir en niveaux de gris si nécessaire
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        # Redimensionner si l'image est trop petite
        height, width = gray.shape
        if height < 1000:
            scale = 1000 / height
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Débruitage
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def parse_lines(self, text: str) -> List[LineItem]:
        """Parse le texte brut pour extraire les lignes structurées"""
        lines = []
        raw_lines = text.split('\n')
        
        for raw_line in raw_lines:
            raw_line = raw_line.strip()
            if not raw_line or len(raw_line) < 10:
                continue
            
            # Vérifier si c'est une ligne à ignorer
            if self._should_skip_line(raw_line):
                continue
            
            # Essayer d'extraire les données
            line_item = self._extract_line_data(raw_line)
            if line_item:
                lines.append(line_item)
        
        return lines
    
    def _should_skip_line(self, line: str) -> bool:
        """Détermine si une ligne doit être ignorée"""
        line_lower = line.lower()
        
        # Vérifier les mots-clés d'exclusion
        for keyword in self.skip_keywords:
            if keyword in line_lower:
                # Mais garder si ça ressemble à une ligne avec des chiffres
                if not re.search(r'\d+[.,]?\d*\s*[€$]?', line):
                    return True
        
        # Ignorer les lignes trop courtes
        if len(line) < 15:
            return True
        
        return False
    
    def _extract_line_data(self, line: str) -> Optional[LineItem]:
        """Extrait les données d'une ligne de devis"""
        
        # Essayer le pattern complet (description + qty + prix unitaire + total)
        match = self.patterns['line_with_qty_price'].search(line)
        if match:
            return self._create_line_item_from_match(match, line, 'full')
        
        # Essayer le pattern mécanique
        match = self.patterns['mechanic_line'].search(line)
        if match:
            return self._create_line_item_from_mechanic_match(match, line)
        
        # Essayer le pattern avec total seulement
        match = self.patterns['line_with_total'].search(line)
        if match:
            return self._create_line_item_from_total_match(match, line)
        
        # Ligne avec description mais pas de données numériques claires
        if self._looks_like_description(line):
            return LineItem(
                description=self._clean_description(line),
                quantity=None,
                unit_price=None,
                total=None,
                confidence=0.3,
                raw_text=line
            )
        
        return None
    
    def _create_line_item_from_match(self, match: re.Match, raw_line: str, pattern_type: str) -> LineItem:
        """Crée un LineItem depuis un match regex complet"""
        desc = self._clean_description(match.group('desc'))
        
        try:
            qty = self._parse_number(match.group('qty')) if 'qty' in match.groupdict() else None
        except:
            qty = None
        
        try:
            unit_price = self._parse_number(match.group('unit_price')) if 'unit_price' in match.groupdict() else None
        except:
            unit_price = None
        
        try:
            total = self._parse_number(match.group('total')) if 'total' in match.groupdict() else None
        except:
            total = None
        
        # Calculer la confiance
        confidence = self._calculate_confidence(desc, qty, unit_price, total, pattern_type)
        
        return LineItem(
            description=desc,
            quantity=qty,
            unit_price=unit_price,
            total=total,
            confidence=confidence,
            raw_text=raw_line
        )
    
    def _create_line_item_from_mechanic_match(self, match: re.Match, raw_line: str) -> LineItem:
        """Crée un LineItem depuis un match de pattern mécanique"""
        desc = self._clean_description(match.group('desc'))
        
        try:
            qty = self._parse_number(match.group('qty'))
        except:
            qty = None
        
        try:
            unit_price = self._parse_number(match.group('unit_price'))
            total = qty * unit_price if qty and unit_price else None
        except:
            unit_price = None
            total = None
        
        confidence = self._calculate_confidence(desc, qty, unit_price, total, 'mechanic')
        
        return LineItem(
            description=desc,
            quantity=qty,
            unit_price=unit_price,
            total=total,
            confidence=confidence,
            raw_text=raw_line
        )
    
    def _create_line_item_from_total_match(self, match: re.Match, raw_line: str) -> LineItem:
        """Crée un LineItem depuis un match avec total seulement"""
        desc = self._clean_description(match.group('desc'))
        
        try:
            total = self._parse_number(match.group('total'))
        except:
            total = None
        
        confidence = self._calculate_confidence(desc, None, None, total, 'total_only')
        
        return LineItem(
            description=desc,
            quantity=None,
            unit_price=None,
            total=total,
            confidence=confidence,
            raw_text=raw_line
        )
    
    def _clean_description(self, desc: str) -> str:
        """Nettoie la description"""
        # Supprimer les caractères spéciaux en début/fin
        desc = desc.strip(' .,-:;|')
        # Normaliser les espaces
        desc = ' '.join(desc.split())
        return desc
    
    def _parse_number(self, value: str) -> Optional[float]:
        """Parse un nombre avec gestion des formats français"""
        if not value:
            return None
        
        # Nettoyer la valeur
        value = value.strip().replace(' ', '')
        
        # Détecter le format (français: 1.234,56 ou 1234,56 / anglais: 1,234.56)
        if ',' in value and '.' in value:
            # Format avec séparateurs des milliers et décimales
            if value.rfind(',') > value.rfind('.'):
                # Format français: 1.234,56
                value = value.replace('.', '').replace(',', '.')
            else:
                # Format anglais: 1,234.56
                value = value.replace(',', '')
        elif ',' in value:
            # Peut être 1234,56 (français) ou 1,234 (anglais milliers)
            parts = value.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Probablement décimal français
                value = value.replace(',', '.')
            else:
                # Probablement séparateur de milliers anglais
                value = value.replace(',', '')
        
        try:
            return float(value)
        except ValueError:
            return None
    
    def _looks_like_description(self, line: str) -> bool:
        """Vérifie si une ligne ressemble à une description de poste"""
        # Doit contenir des lettres
        if not re.search(r'[a-zA-Z]{3,}', line):
            return False
        
        # Ne doit pas être juste des chiffres
        if re.match(r'^\d+$', line.strip()):
            return False
        
        return True
    
    def _calculate_confidence(self, desc: str, qty: Optional[float], 
                              unit_price: Optional[float], total: Optional[float],
                              pattern_type: str) -> float:
        """Calcule le score de confiance pour une ligne"""
        confidence = 0.5
        
        # Bonus pour les patterns complets
        if pattern_type == 'full':
            confidence += 0.3
        elif pattern_type == 'mechanic':
            confidence += 0.2
        elif pattern_type == 'total_only':
            confidence += 0.1
        
        # Vérifier la cohérence mathématique
        if qty and unit_price and total:
            calculated = qty * unit_price
            if abs(calculated - total) < 0.01:
                confidence += 0.15
            elif abs(calculated - total) < 1:
                confidence += 0.05
        
        # Bonus pour une bonne description
        if len(desc) > 10:
            confidence += 0.05
        
        # Malus pour description trop courte ou suspecte
        if len(desc) < 5:
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def process_file(self, file_path: str, filename: str) -> ExtractionResult:
        """Traite un fichier complet (PDF ou image)"""
        # Déterminer le type de fichier
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            raw_text = self.extract_from_pdf(file_path)
        else:
            raw_text = self.extract_from_image(file_path)
        
        # Parser les lignes
        lines = self.parse_lines(raw_text)
        
        # Convertir en dictionnaires
        lines_dict = [
            {
                "description": line.description,
                "quantity": line.quantity,
                "unit_price": line.unit_price,
                "total": line.total,
                "confidence": round(line.confidence, 2)
            }
            for line in lines
        ]
        
        return ExtractionResult(
            filename=filename,
            raw_text=raw_text,
            lines=lines_dict
        )


# Instance globale du moteur
engine = OCREngine()
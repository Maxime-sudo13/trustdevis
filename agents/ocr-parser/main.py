"""
Service FastAPI pour l'extraction OCR de devis TrustDevis
"""

import os
import tempfile
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from engine import OCREngine, ExtractionResult

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="TrustDevis OCR Parser",
    description="Service d'extraction de texte et de données structurées depuis des PDF et images de devis",
    version="1.0.0"
)

# Initialiser le moteur OCR
ocr_engine = OCREngine()

# Modèles de réponse Pydantic
class LineItem(BaseModel):
    description: str
    quantity: Optional[float]
    unit_price: Optional[float]
    total: Optional[float]
    confidence: float

class ExtractionResponse(BaseModel):
    filename: str
    raw_text: str
    lines: List[LineItem]


# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}


def validate_file_extension(filename: str) -> bool:
    """Vérifie si l'extension du fichier est autorisée"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_upload_file(upload_file: UploadFile) -> str:
    """Sauvegarde le fichier uploadé temporairement"""
    try:
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            return tmp.name
    finally:
        upload_file.file.close()


def cleanup_file(file_path: str):
    """Supprime le fichier temporaire"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Erreur lors de la suppression du fichier temporaire: {e}")


@app.get("/")
async def root():
    """Endpoint racine - informations sur le service"""
    return {
        "service": "TrustDevis OCR Parser",
        "version": "1.0.0",
        "endpoints": [
            "/extract/pdf",
            "/extract/image",
            "/health"
        ]
    }


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {
        "status": "healthy",
        "service": "ocr-parser",
        "tesseract_available": True
    }


@app.post("/extract/pdf", response_model=ExtractionResponse)
async def extract_pdf(file: UploadFile = File(...)):
    """
    Extrait le texte et les données structurées d'un fichier PDF.
    
    - **file**: Fichier PDF à analyser
    
    Retourne le texte brut et les lignes structurées détectées.
    """
    # Validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier manquant")
    
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"Extension non supportée. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != '.pdf':
        raise HTTPException(status_code=400, detail="Ce endpoint accepte uniquement les fichiers PDF")
    
    # Sauvegarder le fichier
    temp_path = None
    try:
        temp_path = save_upload_file(file)
        logger.info(f"Fichier PDF reçu: {file.filename}, sauvegardé à: {temp_path}")
        
        # Traiter le fichier
        result = ocr_engine.process_file(temp_path, file.filename)
        
        return ExtractionResponse(
            filename=result.filename,
            raw_text=result.raw_text,
            lines=result.lines
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")
    
    finally:
        if temp_path:
            cleanup_file(temp_path)


@app.post("/extract/image", response_model=ExtractionResponse)
async def extract_image(file: UploadFile = File(...)):
    """
    Extrait le texte et les données structurées d'une image.
    
    - **file**: Image à analyser (PNG, JPG, JPEG, TIFF, BMP, GIF)
    
    Retourne le texte brut et les lignes structurées détectées.
    """
    # Validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier manquant")
    
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"Extension non supportée. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext == '.pdf':
        raise HTTPException(status_code=400, detail="Utilisez /extract/pdf pour les fichiers PDF")
    
    # Sauvegarder le fichier
    temp_path = None
    try:
        temp_path = save_upload_file(file)
        logger.info(f"Image reçue: {file.filename}, sauvegardée à: {temp_path}")
        
        # Traiter le fichier
        result = ocr_engine.process_file(temp_path, file.filename)
        
        return ExtractionResponse(
            filename=result.filename,
            raw_text=result.raw_text,
            lines=result.lines
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'image: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")
    
    finally:
        if temp_path:
            cleanup_file(temp_path)


@app.post("/extract", response_model=ExtractionResponse)
async def extract_generic(file: UploadFile = File(...)):
    """
    Endpoint générique pour extraire du texte d'un fichier (PDF ou image).
    Détecte automatiquement le type de fichier.
    
    - **file**: Fichier à analyser
    """
    # Validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier manquant")
    
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"Extension non supportée. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Sauvegarder le fichier
    temp_path = None
    try:
        temp_path = save_upload_file(file)
        logger.info(f"Fichier reçu: {file.filename}, sauvegardé à: {temp_path}")
        
        # Traiter le fichier
        result = ocr_engine.process_file(temp_path, file.filename)
        
        return ExtractionResponse(
            filename=result.filename,
            raw_text=result.raw_text,
            lines=result.lines
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")
    
    finally:
        if temp_path:
            cleanup_file(temp_path)


# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
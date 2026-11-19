"""
Point d'entrée principal FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as quote_router


app = FastAPI(
    title="TrustDevis Quote Generator API",
    description="API de génération de devis pour travaux du bâtiment",
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

# Routes
app.include_router(quote_router)


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "service": "TrustDevis Quote Generator",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate_quote": "POST /quote/generate",
            "get_quote": "GET /quote/{id}",
            "send_email": "POST /quote/send-email",
            "contact_artisans": "POST /quote/contact-artisans",
            "comparison": "GET /quote/{id}/comparison",
            "distribution": "GET /quote/{id}/distribution"
        }
    }


@app.get("/health")
async def health_check():
    """Vérification de santé"""
    return {
        "status": "healthy",
        "service": "quote-generator"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

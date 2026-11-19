"""
Middleware de sécurité pour le service Compliance RGPD
"""

import time
import hashlib
import hmac
import secrets
from typing import Optional, Callable
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Ajoute les headers de sécurité obligatoires"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Protection contre le clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Protection XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Politique de sécurité du contenu
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self';"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        # Strict Transport Security (HSTS) - uniquement en HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting simple par IP"""
    
    def __init__(self, app: ASGIApp, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Nettoyer les anciennes entrées
        self._clean_old_entries(current_time)
        
        # Vérifier le rate limit
        if client_ip in self.requests:
            request_count, window_start = self.requests[client_ip]
            if current_time - window_start < self.window:
                if request_count >= self.max_requests:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later."
                    )
                self.requests[client_ip] = (request_count + 1, window_start)
            else:
                self.requests[client_ip] = (1, current_time)
        else:
            self.requests[client_ip] = (1, current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Récupère l'IP client réelle"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_entries(self, current_time: float):
        """Nettoie les entrées expirées"""
        expired = [
            ip for ip, (_, window_start) in self.requests.items()
            if current_time - window_start > self.window
        ]
        for ip in expired:
            del self.requests[ip]


class GDPRAuditMiddleware(BaseHTTPMiddleware):
    """Middleware d'audit pour tracer les accès aux endpoints RGPD"""
    
    def __init__(self, app: ASGIApp, gdpr_core=None):
        super().__init__(app)
        self.gdpr_core = gdpr_core
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Ne logger que les endpoints sensibles
        sensitive_paths = ["/gdpr/", "/consent/"]
        
        if any(request.url.path.startswith(path) for path in sensitive_paths):
            client_ip = self._get_client_ip(request)
            user_id = self._extract_user_id(request)
            
            # Logger avant traitement
            if self.gdpr_core and user_id:
                self.gdpr_core.log_data_access(
                    user_id=user_id,
                    action=f"api_access_{request.method.lower()}",
                    ip=client_ip,
                    details=f"Endpoint: {request.url.path}"
                )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extrait l'user_id de la requête si possible"""
        # Depuis les paramètres de chemin
        user_id = request.path_params.get("user_id")
        if user_id:
            return user_id
        
        # Depuis le body (pour POST/PUT)
        # Note: Le body ne peut être lu qu'une fois, donc on skip ici
        # et on loggera dans l'endpoint directement
        
        return None


class APITokenAuth:
    """Authentification par token API simple"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
        self.tokens = set()  # En production: utiliser une base de données
    
    def add_token(self, token: str):
        """Ajoute un token valide"""
        self.tokens.add(token)
    
    def remove_token(self, token: str):
        """Révoque un token"""
        self.tokens.discard(token)
    
    def verify_token(self, credentials: Optional[HTTPAuthorizationCredentials]) -> bool:
        """Vérifie si le token est valide"""
        if not credentials:
            return False
        return credentials.credentials in self.tokens
    
    def generate_token(self) -> str:
        """Génère un nouveau token sécurisé"""
        return secrets.token_urlsafe(32)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validation des requêtes entrantes"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Vérifier la taille du body (protection contre les attaques par déni de service)
        content_length = request.headers.get("content-length")
        if content_length:
            max_size = 10 * 1024 * 1024  # 10 MB
            if int(content_length) > max_size:
                raise HTTPException(
                    status_code=413,
                    detail="Request entity too large"
                )
        
        # Vérifier le Content-Type pour les requêtes avec body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if content_type and not any(
                ct in content_type for ct in ["application/json", "multipart/form-data"]
            ):
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported media type"
                )
        
        return await call_next(request)


class CORSConfig:
    """Configuration CORS pour le service"""
    
    ALLOWED_ORIGINS = [
        "https://trustdevis.fr",
        "https://www.trustdevis.fr",
        "https://api.trustdevis.fr",
        # En développement
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    ALLOWED_HEADERS = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin"
    ]
    
    EXPOSED_HEADERS = [
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining"
    ]


def get_security_config():
    """Retourne la configuration de sécurité complète"""
    return {
        "middlewares": [
            SecurityHeadersMiddleware,
            RequestValidationMiddleware,
            RateLimitMiddleware,
            GDPRAuditMiddleware
        ],
        "cors": CORSConfig,
        "rate_limits": {
            "default": {"max_requests": 100, "window": 60},
            "sensitive": {"max_requests": 10, "window": 60}  # Pour /gdpr/delete
        }
    }

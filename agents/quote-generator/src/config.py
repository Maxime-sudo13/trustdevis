from pydantic import BaseModel, Field
from typing import Optional


class AppConfig(BaseModel):
    """Configuration de l'application"""
    
    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    debug: bool = Field(default=False)
    
    # Email
    smtp_host: Optional[str] = Field(default=None)
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    email_from: str = Field(default="devis@trustdevis.com")
    
    # Pricing
    default_vat_rate: float = Field(default=20.0)
    minimum_quote_amount: float = Field(default=150.0)
    
    # Storage
    storage_ttl_hours: int = Field(default=72)  # Durée de conservation des devis


# Instance globale
config = AppConfig()

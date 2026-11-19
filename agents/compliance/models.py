from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ConsentType(str, Enum):
    TERMS_OF_SERVICE = "terms_of_service"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY_SHARING = "third_party_sharing"
    COOKIES = "cookies"

class LegalBasis(str, Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class Consent(BaseModel):
    user_id: str
    type: ConsentType
    date: datetime
    ip: str
    version: str
    active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConsentCreate(BaseModel):
    user_id: str
    type: ConsentType
    version: str
    ip: Optional[str] = None

class ConsentRevoke(BaseModel):
    user_id: str
    type: ConsentType

class Treatment(BaseModel):
    id: str
    purpose: str
    legal_basis: LegalBasis
    retention: str  # Format: "30d", "1y", "indefinite"
    recipients: List[str]
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TreatmentCreate(BaseModel):
    id: str
    purpose: str
    legal_basis: LegalBasis
    retention: str
    recipients: List[str]
    description: Optional[str] = None

class DataAccessLog(BaseModel):
    user_id: str
    action: str
    date: datetime
    ip: str
    details: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DataAccessLogCreate(BaseModel):
    user_id: str
    action: str
    ip: Optional[str] = None
    details: Optional[str] = None

class GDPRExportRequest(BaseModel):
    user_id: str
    ip: Optional[str] = None

class GDPRDeleteRequest(BaseModel):
    user_id: str
    ip: Optional[str] = None
    reason: Optional[str] = None

class GDPRExportResponse(BaseModel):
    user_id: str
    export_date: datetime
    data: dict
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GDPRDeleteResponse(BaseModel):
    user_id: str
    deleted_at: datetime
    status: str
    anonymized: bool
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

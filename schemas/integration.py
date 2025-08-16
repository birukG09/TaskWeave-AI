"""
TaskWeave AI - Integration schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from models.integration import IntegrationType

class IntegrationConnect(BaseModel):
    provider: IntegrationType
    metadata: Optional[Dict[str, Any]] = {}

class IntegrationResponse(BaseModel):
    id: str
    org_id: str
    provider: IntegrationType
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

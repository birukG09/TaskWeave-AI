"""
TaskWeave AI - Automation schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator

class AutomationBase(BaseModel):
    name: str
    trigger: Dict[str, Any]
    conditions: Dict[str, Any] = {}
    actions: Dict[str, Any]
    enabled: bool = True
    
    @validator("name")
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Automation name must be at least 2 characters long")
        return v.strip()

class AutomationCreate(AutomationBase):
    pass

class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    trigger: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None

class AutomationResponse(AutomationBase):
    id: str
    org_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

"""
TaskWeave AI - Project schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    
    @validator("name")
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Project name must be at least 2 characters long")
        return v.strip()

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: str
    org_id: str
    created_by: str
    created_at: datetime
    
    class Config:
        orm_mode = True

"""
TaskWeave AI - Organization schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator

class OrganizationBase(BaseModel):
    name: str
    
    @validator("name")
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Organization name must be at least 2 characters long")
        return v.strip()

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: str
    owner_id: str
    plan: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class MembershipBase(BaseModel):
    role: str = "member"

class MembershipCreate(MembershipBase):
    email: str

class MembershipUpdate(MembershipBase):
    pass

class MembershipResponse(MembershipBase):
    id: str
    org_id: str
    user_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

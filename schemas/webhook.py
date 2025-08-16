"""
TaskWeave AI - Webhook schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl, validator

class WebhookBase(BaseModel):
    url: HttpUrl
    events: List[str]
    active: bool = True
    
    @validator("events")
    def validate_events(cls, v):
        if not v:
            raise ValueError("At least one event must be specified")
        return v

class WebhookCreate(WebhookBase):
    pass

class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    active: Optional[bool] = None

class WebhookResponse(WebhookBase):
    id: str
    org_id: str
    secret: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class WebhookTest(BaseModel):
    event: str

"""
TaskWeave AI - Report schemas
"""
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
from models.report import ReportType

class ReportGenerate(BaseModel):
    type: ReportType

class ReportResponse(BaseModel):
    id: str
    org_id: str
    type: ReportType
    content: Dict[str, Any]
    generated_at: datetime
    
    class Config:
        orm_mode = True

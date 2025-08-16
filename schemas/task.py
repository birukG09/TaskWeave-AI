"""
TaskWeave AI - Task schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator
from models.task import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 3
    labels: Optional[List[str]] = []
    
    @validator("title")
    def validate_title(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Task title cannot be empty")
        return v.strip()
    
    @validator("priority")
    def validate_priority(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Priority must be between 1 and 5")
        return v

class TaskCreate(TaskBase):
    project_id: Optional[str] = None
    assignee_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None

class TaskResponse(TaskBase):
    id: str
    project_id: Optional[str]
    org_id: str
    source: Optional[str]
    status: TaskStatus
    assignee_id: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

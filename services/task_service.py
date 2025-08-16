"""
TaskWeave AI - Task service
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import structlog

from models.task import Task, TaskStatus
from schemas.task import TaskCreate, TaskUpdate

logger = structlog.get_logger()

class TaskService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_tasks(
        self,
        org_id: str,
        project_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """Get tasks with filters"""
        query = self.db.query(Task).filter(Task.org_id == org_id)
        
        if project_id:
            query = query.filter(Task.project_id == project_id)
        
        if status:
            query = query.filter(Task.status == status)
        
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        
        return query.order_by(Task.priority.desc(), Task.created_at.desc()).offset(offset).limit(limit).all()
    
    async def create_task(self, org_id: str, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task = Task(
            org_id=org_id,
            project_id=task_data.project_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            assignee_id=task_data.assignee_id,
            labels=task_data.labels or []
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    async def update_task(self, org_id: str, task_id: str, task_update: TaskUpdate) -> Task:
        """Update task"""
        task = self.db.query(Task).filter(
            Task.id == task_id,
            Task.org_id == org_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    async def create_task_from_ai(self, org_id: str, ai_extracted_data: dict) -> Task:
        """Create task from AI-extracted data"""
        task = Task(
            org_id=org_id,
            title=ai_extracted_data.get("title", "Untitled Task"),
            description=ai_extracted_data.get("description"),
            priority=ai_extracted_data.get("priority", 3),
            source=ai_extracted_data.get("source"),
            labels=ai_extracted_data.get("labels", [])
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        logger.info("AI-generated task created", task_id=str(task.id), org_id=org_id, source=task.source)
        
        return task

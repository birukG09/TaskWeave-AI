"""
TaskWeave AI - Task model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, CheckConstraint, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum

from database import Base

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # Which integration/service created this task
    priority = Column(Integer, default=3)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    labels = Column(ARRAY(String), nullable=True, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    organization = relationship("Organization", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    
    __table_args__ = (
        CheckConstraint("priority BETWEEN 1 AND 5", name="check_priority_range"),
        Index("idx_tasks_org", "org_id"),
        Index("idx_tasks_project", "project_id"),
        Index("idx_tasks_status_priority", "status", "priority"),
    )
    
    def __repr__(self):
        return f"<Task {self.title}>"

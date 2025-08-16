"""
TaskWeave AI - Report model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from database import Base

class ReportType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(ReportType), nullable=False)
    content = Column(JSONB, nullable=False, default={})
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="reports")
    
    __table_args__ = (
        Index("idx_reports_org_type", "org_id", "type"),
    )
    
    def __repr__(self):
        return f"<Report {self.type} for {self.org_id}>"

"""
TaskWeave AI - Automation model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from database import Base

class Automation(Base):
    __tablename__ = "automations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    trigger = Column(JSONB, nullable=False, default={})
    conditions = Column(JSONB, nullable=False, default={})
    actions = Column(JSONB, nullable=False, default={})
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="automations")
    
    __table_args__ = (
        Index("idx_automations_org_enabled", "org_id", "enabled"),
    )
    
    def __repr__(self):
        return f"<Automation {self.name}>"

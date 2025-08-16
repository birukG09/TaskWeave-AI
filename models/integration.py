"""
TaskWeave AI - Integration model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from database import Base

class IntegrationType(str, enum.Enum):
    SLACK = "slack"
    GITHUB = "github"
    GMAIL = "gmail"
    TRELLO = "trello"
    NOTION = "notion"
    GDRIVE = "gdrive"

class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    provider = Column(SQLEnum(IntegrationType), nullable=False)
    oauth_access_token = Column(Text, nullable=True)
    oauth_refresh_token = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="integrations")
    
    __table_args__ = (
        Index("idx_integrations_org_provider", "org_id", "provider"),
    )
    
    def __repr__(self):
        return f"<Integration {self.provider} for {self.org_id}>"

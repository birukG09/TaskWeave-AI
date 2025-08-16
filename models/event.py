"""
TaskWeave AI - Event model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)
    external_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False, default={})
    ingested_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="events")
    
    __table_args__ = (
        Index("idx_events_org_provider", "org_id", "provider"),
        Index("idx_events_processed", "processed"),
    )
    
    def __repr__(self):
        return f"<Event {self.event_type} from {self.provider}>"

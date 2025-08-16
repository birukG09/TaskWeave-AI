"""
TaskWeave AI - Base integration class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()

class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        self.access_token = access_token
        self.metadata = metadata or {}
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the integration connection is working"""
        pass
    
    @abstractmethod
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch events from the integration"""
        pass
    
    @abstractmethod
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Create a task in the external service"""
        pass
    
    async def normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data to common format"""
        return {
            "id": event.get("id"),
            "type": event.get("type"),
            "timestamp": event.get("timestamp"),
            "data": event
        }

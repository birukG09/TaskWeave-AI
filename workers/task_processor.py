"""
TaskWeave AI - Task processing worker
"""
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import structlog

from database import SessionLocal
from models.event import Event
from models.task import Task
from models.integration import Integration
from ai.pipelines import TaskExtractor, PriorityScorer
from services.task_service import TaskService
from services.automation_service import AutomationService
from integrations import (
    SlackIntegration, 
    GitHubIntegration, 
    GmailIntegration,
    TrelloIntegration,
    NotionIntegration,
    GDriveIntegration
)

logger = structlog.get_logger()

class TaskProcessor:
    """Background worker for processing events and extracting tasks"""
    
    def __init__(self):
        self.task_extractor = TaskExtractor()
        self.priority_scorer = PriorityScorer()
    
    async def process_event(self, event_id: str) -> None:
        """Process a single event and extract tasks"""
        db = SessionLocal()
        try:
            # Get event
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event or event.processed:
                return
            
            logger.info("Processing event", event_id=event_id, provider=event.provider)
            
            # Extract tasks using AI
            tasks_data = await self.task_extractor.extract_tasks({
                "id": str(event.id),
                "type": event.event_type,
                "provider": event.provider,
                "timestamp": event.ingested_at.isoformat(),
                **event.payload
            })
            
            # Create tasks
            task_service = TaskService(db)
            created_tasks = []
            
            for task_data in tasks_data:
                # Score priority
                priority = await self.priority_scorer.score_priority(task_data)
                
                # Create task
                task = await task_service.create_task_from_ai(event.org_id, {
                    "title": task_data.get("title"),
                    "description": task_data.get("description"),
                    "priority": priority,
                    "source": f"{event.provider}:{event.event_type}",
                    "labels": [task_data.get("category", "auto-generated")]
                })
                
                created_tasks.append(task)
            
            # Mark event as processed
            event.processed = True
            db.commit()
            
            # Trigger automations
            automation_service = AutomationService(db)
            await automation_service.evaluate_automations(event.org_id, {
                "type": "tasks_created",
                "event_id": str(event.id),
                "tasks_created": len(created_tasks),
                "provider": event.provider
            })
            
            logger.info("Event processed", 
                       event_id=event_id, 
                       tasks_created=len(created_tasks))
            
        except Exception as e:
            logger.error("Event processing failed", event_id=event_id, error=str(e))
        finally:
            db.close()
    
    async def process_pending_events(self, limit: int = 100) -> None:
        """Process all pending events"""
        db = SessionLocal()
        try:
            # Get unprocessed events
            events = db.query(Event).filter(
                Event.processed == False
            ).limit(limit).all()
            
            logger.info("Processing pending events", count=len(events))
            
            # Process events concurrently
            tasks = [self.process_event(str(event.id)) for event in events]
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error("Batch event processing failed", error=str(e))
        finally:
            db.close()
    
    async def sync_integration_events(self, org_id: str, provider: str) -> None:
        """Sync events from an integration"""
        db = SessionLocal()
        try:
            # Get integration
            integration = db.query(Integration).filter(
                Integration.org_id == org_id,
                Integration.provider == provider
            ).first()
            
            if not integration or not integration.oauth_access_token:
                logger.warning("Integration not found or not configured", 
                             org_id=org_id, provider=provider)
                return
            
            # Get integration client
            integration_client = self._get_integration_client(
                provider, 
                integration.oauth_access_token,
                integration.metadata
            )
            
            if not integration_client:
                logger.error("Failed to create integration client", provider=provider)
                return
            
            # Test connection
            if not await integration_client.test_connection():
                logger.error("Integration connection test failed", provider=provider)
                return
            
            # Fetch events
            events = await integration_client.fetch_events()
            
            # Save events to database
            for event_data in events:
                # Check if event already exists
                existing = db.query(Event).filter(
                    Event.org_id == org_id,
                    Event.provider == provider,
                    Event.external_id == event_data.get("id")
                ).first()
                
                if existing:
                    continue
                
                # Create new event
                event = Event(
                    org_id=org_id,
                    provider=provider,
                    external_id=event_data.get("id"),
                    event_type=event_data.get("type", "unknown"),
                    payload=event_data
                )
                
                db.add(event)
            
            db.commit()
            logger.info("Integration events synced", 
                       org_id=org_id, provider=provider, count=len(events))
            
        except Exception as e:
            logger.error("Integration sync failed", 
                        org_id=org_id, provider=provider, error=str(e))
        finally:
            db.close()
    
    def _get_integration_client(self, provider: str, access_token: str, metadata: Dict[str, Any]):
        """Get integration client instance"""
        integration_classes = {
            "slack": SlackIntegration,
            "github": GitHubIntegration,
            "gmail": GmailIntegration,
            "trello": TrelloIntegration,
            "notion": NotionIntegration,
            "gdrive": GDriveIntegration
        }
        
        integration_class = integration_classes.get(provider)
        if not integration_class:
            return None
        
        return integration_class(access_token, metadata)
    
    async def run_continuous(self, interval: int = 300) -> None:
        """Run processor continuously"""
        logger.info("Starting continuous task processor", interval=interval)
        
        while True:
            try:
                await self.process_pending_events()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error("Continuous processing error", error=str(e))
                await asyncio.sleep(60)  # Short sleep on error

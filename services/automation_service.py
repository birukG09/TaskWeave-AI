"""
TaskWeave AI - Automation service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import structlog

from models.automation import Automation
from schemas.automation import AutomationCreate, AutomationUpdate

logger = structlog.get_logger()

class AutomationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_automation(self, org_id: str, automation_data: AutomationCreate) -> Automation:
        """Create a new automation"""
        automation = Automation(
            org_id=org_id,
            name=automation_data.name,
            trigger=automation_data.trigger,
            conditions=automation_data.conditions,
            actions=automation_data.actions,
            enabled=automation_data.enabled
        )
        
        self.db.add(automation)
        self.db.commit()
        self.db.refresh(automation)
        
        return automation
    
    async def update_automation(self, org_id: str, automation_id: str, automation_update: AutomationUpdate) -> Automation:
        """Update automation"""
        automation = self.db.query(Automation).filter(
            Automation.id == automation_id,
            Automation.org_id == org_id
        ).first()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        update_data = automation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(automation, field, value)
        
        self.db.commit()
        self.db.refresh(automation)
        
        return automation
    
    async def evaluate_automations(self, org_id: str, event_data: dict) -> None:
        """Evaluate automations against an event"""
        automations = self.db.query(Automation).filter(
            Automation.org_id == org_id,
            Automation.enabled == True
        ).all()
        
        for automation in automations:
            try:
                if await self._matches_trigger(automation.trigger, event_data):
                    if await self._matches_conditions(automation.conditions, event_data):
                        await self._execute_actions(automation.actions, event_data, org_id)
                        logger.info("Automation executed", automation_id=str(automation.id), org_id=org_id)
            except Exception as e:
                logger.error("Automation execution failed", automation_id=str(automation.id), error=str(e))
    
    async def _matches_trigger(self, trigger: dict, event_data: dict) -> bool:
        """Check if event matches automation trigger"""
        # Simple trigger matching - can be extended
        trigger_type = trigger.get("type")
        if trigger_type == "event":
            return (
                trigger.get("provider") == event_data.get("provider") and
                trigger.get("event_type") == event_data.get("event_type")
            )
        return False
    
    async def _matches_conditions(self, conditions: dict, event_data: dict) -> bool:
        """Check if event matches automation conditions"""
        if not conditions:
            return True
        
        # Simple condition matching - can be extended
        for key, expected_value in conditions.items():
            if event_data.get(key) != expected_value:
                return False
        
        return True
    
    async def _execute_actions(self, actions: dict, event_data: dict, org_id: str) -> None:
        """Execute automation actions"""
        action_type = actions.get("type")
        
        if action_type == "create_task":
            from services.task_service import TaskService
            task_service = TaskService(self.db)
            
            task_data = {
                "title": actions.get("task_title", "Automated Task"),
                "description": actions.get("task_description"),
                "priority": actions.get("task_priority", 3),
                "source": "automation",
                "labels": actions.get("task_labels", [])
            }
            
            await task_service.create_task_from_ai(org_id, task_data)
        
        elif action_type == "send_notification":
            # TODO: Implement notification sending
            pass
        
        elif action_type == "webhook":
            # TODO: Implement webhook calling
            pass

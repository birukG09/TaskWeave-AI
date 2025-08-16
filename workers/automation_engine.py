"""
TaskWeave AI - Automation engine worker
"""
import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import structlog

from database import SessionLocal
from models.automation import Automation
from models.event import Event
from models.organization import Organization
from services.automation_service import AutomationService
from services.webhook_service import WebhookService

logger = structlog.get_logger()

class AutomationEngine:
    """Background worker for processing automations"""
    
    def __init__(self):
        self.webhook_service = None
    
    async def process_automations(self, org_id: str, event_data: Dict[str, Any]) -> None:
        """Process automations for an organization event"""
        db = SessionLocal()
        try:
            automation_service = AutomationService(db)
            await automation_service.evaluate_automations(org_id, event_data)
            
        except Exception as e:
            logger.error("Automation processing failed", 
                        org_id=org_id, error=str(e))
        finally:
            db.close()
    
    async def run_periodic_automations(self) -> None:
        """Run automations that are triggered on a schedule"""
        db = SessionLocal()
        try:
            # Get all organizations
            organizations = db.query(Organization).all()
            
            for org in organizations:
                await self._run_org_periodic_automations(str(org.id))
            
        except Exception as e:
            logger.error("Periodic automations failed", error=str(e))
        finally:
            db.close()
    
    async def _run_org_periodic_automations(self, org_id: str) -> None:
        """Run periodic automations for an organization"""
        db = SessionLocal()
        try:
            # Get automations with schedule triggers
            automations = db.query(Automation).filter(
                Automation.org_id == org_id,
                Automation.enabled == True
            ).all()
            
            for automation in automations:
                trigger = automation.trigger
                
                if trigger.get("type") == "schedule":
                    await self._process_scheduled_automation(automation, db)
                elif trigger.get("type") == "webhook":
                    await self._process_webhook_automation(automation, db)
            
        except Exception as e:
            logger.error("Organization periodic automations failed", 
                        org_id=org_id, error=str(e))
        finally:
            db.close()
    
    async def _process_scheduled_automation(self, automation: Automation, db: Session) -> None:
        """Process a scheduled automation"""
        try:
            trigger = automation.trigger
            schedule = trigger.get("schedule", {})
            
            # Simple schedule processing - can be extended with cron-like functionality
            schedule_type = schedule.get("type")
            
            if schedule_type == "daily":
                # Run daily automation
                await self._execute_automation_actions(automation, {
                    "trigger_type": "schedule",
                    "schedule_type": "daily",
                    "timestamp": asyncio.get_event_loop().time()
                }, db)
            
            elif schedule_type == "weekly":
                # Run weekly automation  
                import datetime
                if datetime.datetime.now().weekday() == 0:  # Monday
                    await self._execute_automation_actions(automation, {
                        "trigger_type": "schedule",
                        "schedule_type": "weekly",
                        "timestamp": asyncio.get_event_loop().time()
                    }, db)
            
        except Exception as e:
            logger.error("Scheduled automation failed", 
                        automation_id=str(automation.id), error=str(e))
    
    async def _process_webhook_automation(self, automation: Automation, db: Session) -> None:
        """Process webhook-based automation"""
        try:
            # Webhook automations are typically triggered by external events
            # This would be called when webhooks are received
            pass
            
        except Exception as e:
            logger.error("Webhook automation failed", 
                        automation_id=str(automation.id), error=str(e))
    
    async def _execute_automation_actions(self, automation: Automation, trigger_data: Dict[str, Any], db: Session) -> None:
        """Execute automation actions"""
        try:
            actions = automation.actions
            action_type = actions.get("type")
            
            if action_type == "send_notification":
                await self._send_notification(automation.org_id, actions, trigger_data, db)
            
            elif action_type == "create_task":
                await self._create_automated_task(automation.org_id, actions, trigger_data, db)
            
            elif action_type == "webhook":
                await self._trigger_webhook(automation.org_id, actions, trigger_data, db)
            
            elif action_type == "integration_action":
                await self._trigger_integration_action(automation.org_id, actions, trigger_data, db)
            
            logger.info("Automation executed", 
                       automation_id=str(automation.id),
                       action_type=action_type)
            
        except Exception as e:
            logger.error("Automation action execution failed", 
                        automation_id=str(automation.id), error=str(e))
    
    async def _send_notification(self, org_id: str, actions: Dict[str, Any], trigger_data: Dict[str, Any], db: Session) -> None:
        """Send notification action"""
        try:
            # Initialize webhook service if needed
            if not self.webhook_service:
                self.webhook_service = WebhookService(db)
            
            notification_data = {
                "type": "automation_notification",
                "message": actions.get("message", "Automation triggered"),
                "automation_name": actions.get("automation_name", "Unknown"),
                "trigger_data": trigger_data,
                "timestamp": trigger_data.get("timestamp")
            }
            
            await self.webhook_service.send_webhooks(org_id, "notification", notification_data)
            
        except Exception as e:
            logger.error("Notification sending failed", error=str(e))
    
    async def _create_automated_task(self, org_id: str, actions: Dict[str, Any], trigger_data: Dict[str, Any], db: Session) -> None:
        """Create task action"""
        try:
            from services.task_service import TaskService
            
            task_service = TaskService(db)
            
            task_data = {
                "title": actions.get("task_title", "Automated Task"),
                "description": actions.get("task_description", "Created by automation"),
                "priority": actions.get("task_priority", 3),
                "source": "automation",
                "labels": actions.get("task_labels", ["automated"])
            }
            
            await task_service.create_task_from_ai(org_id, task_data)
            
        except Exception as e:
            logger.error("Automated task creation failed", error=str(e))
    
    async def _trigger_webhook(self, org_id: str, actions: Dict[str, Any], trigger_data: Dict[str, Any], db: Session) -> None:
        """Trigger webhook action"""
        try:
            if not self.webhook_service:
                self.webhook_service = WebhookService(db)
            
            webhook_data = {
                "type": "automation_webhook",
                "automation_data": actions,
                "trigger_data": trigger_data,
                "timestamp": trigger_data.get("timestamp")
            }
            
            await self.webhook_service.send_webhooks(org_id, "automation", webhook_data)
            
        except Exception as e:
            logger.error("Webhook triggering failed", error=str(e))
    
    async def _trigger_integration_action(self, org_id: str, actions: Dict[str, Any], trigger_data: Dict[str, Any], db: Session) -> None:
        """Trigger integration action"""
        try:
            from models.integration import Integration
            
            provider = actions.get("provider")
            if not provider:
                return
            
            integration = db.query(Integration).filter(
                Integration.org_id == org_id,
                Integration.provider == provider
            ).first()
            
            if not integration:
                logger.warning("Integration not found for automation", 
                             org_id=org_id, provider=provider)
                return
            
            # This would trigger specific integration actions
            # Implementation depends on the specific integration and action
            logger.info("Integration action triggered", 
                       org_id=org_id, provider=provider)
            
        except Exception as e:
            logger.error("Integration action failed", error=str(e))
    
    async def run_continuous(self, interval: int = 60) -> None:
        """Run automation engine continuously"""
        logger.info("Starting continuous automation engine", interval=interval)
        
        while True:
            try:
                await self.run_periodic_automations()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error("Continuous automation processing error", error=str(e))
                await asyncio.sleep(30)  # Short sleep on error

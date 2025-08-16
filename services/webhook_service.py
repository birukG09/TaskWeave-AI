"""
TaskWeave AI - Webhook service
"""
import hashlib
import hmac
import secrets
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import httpx
import structlog

from models.webhook import Webhook
from schemas.webhook import WebhookCreate, WebhookUpdate

logger = structlog.get_logger()

class WebhookService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_webhook(self, org_id: str, webhook_data: WebhookCreate) -> Webhook:
        """Create a new webhook"""
        webhook = Webhook(
            org_id=org_id,
            url=str(webhook_data.url),
            secret=secrets.token_urlsafe(32),
            events=webhook_data.events,
            active=webhook_data.active
        )
        
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        
        return webhook
    
    async def update_webhook(self, org_id: str, webhook_id: str, webhook_update: WebhookUpdate) -> Webhook:
        """Update webhook"""
        webhook = self.db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.org_id == org_id
        ).first()
        
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        update_data = webhook_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "url":
                value = str(value)
            setattr(webhook, field, value)
        
        self.db.commit()
        self.db.refresh(webhook)
        
        return webhook
    
    async def send_webhook(self, webhook: Webhook, event: str, payload: Dict[str, Any]) -> bool:
        """Send webhook notification"""
        if not webhook.active or event not in webhook.events:
            return False
        
        webhook_payload = {
            "event": event,
            "timestamp": payload.get("timestamp"),
            "data": payload
        }
        
        # Create signature
        signature = self._create_signature(webhook.secret, webhook_payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-TaskWeave-Signature": signature,
            "X-TaskWeave-Event": event
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    json=webhook_payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info("Webhook delivered", webhook_id=str(webhook.id), event=event)
                    return True
                else:
                    logger.warning("Webhook delivery failed", webhook_id=str(webhook.id), status=response.status_code)
                    return False
        
        except Exception as e:
            logger.error("Webhook delivery error", webhook_id=str(webhook.id), error=str(e))
            return False
    
    async def send_webhooks(self, org_id: str, event: str, payload: Dict[str, Any]) -> None:
        """Send webhooks to all active webhooks for an organization"""
        webhooks = self.db.query(Webhook).filter(
            Webhook.org_id == org_id,
            Webhook.active == True
        ).all()
        
        for webhook in webhooks:
            await self.send_webhook(webhook, event, payload)
    
    async def test_webhooks(self, org_id: str, event: str) -> Dict[str, Any]:
        """Test webhook delivery"""
        webhooks = self.db.query(Webhook).filter(
            Webhook.org_id == org_id,
            Webhook.active == True
        ).all()
        
        test_payload = {
            "event": event,
            "test": True,
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {"message": "This is a test webhook"}
        }
        
        results = []
        for webhook in webhooks:
            success = await self.send_webhook(webhook, event, test_payload)
            results.append({
                "webhook_id": str(webhook.id),
                "url": webhook.url,
                "success": success
            })
        
        return {
            "event": event,
            "tested_webhooks": len(results),
            "successful_deliveries": len([r for r in results if r["success"]]),
            "results": results
        }
    
    def _create_signature(self, secret: str, payload: Dict[str, Any]) -> str:
        """Create HMAC signature for webhook"""
        import json
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hmac.new(
            secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
